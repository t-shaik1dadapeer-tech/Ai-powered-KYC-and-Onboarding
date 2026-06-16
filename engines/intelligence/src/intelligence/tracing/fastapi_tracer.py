from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from intelligence.models import ApiItem, FlowStep, FlowTrace, Inventories
from intelligence.tracing.index import CodeIndex
from intelligence.tracing.sequence import build_sequence_diagram
from intelligence.walker import read_lines

HANDLER_SERVICE_CALL = re.compile(
    r"(?:return\s+)?(\w+Service)\s*\([^)]*\)\.(\w+)\s*\("
)
SERVICE_REPO_CALL = re.compile(r"self\._(\w+)\.(\w+)\s*\(")
SPRING_SERVICE_FIELD = re.compile(r"(\w+Service)\.(\w+)\s*\(")


class FastAPIFlowTracer:
    def __init__(self, repo_path: Path, files: List[Path], inventories: Inventories):
        self.repo_path = repo_path
        self.inventories = inventories
        self.index = CodeIndex(repo_path, files)

    def trace_all(self) -> List[FlowTrace]:
        return [self.trace_api(api) for api in self.inventories.apis]

    def trace_api(self, api: ApiItem) -> FlowTrace:
        steps: List[FlowStep] = []
        uncertainties: List[str] = []

        steps.append(
            FlowStep(
                layer="controller",
                symbol=f"router.{api.handler}",
                file=api.file,
                line=api.line,
                operation=f"{api.method} {api.path}",
            )
        )

        handler_file = self.repo_path / api.file
        if not handler_file.exists():
            uncertainties.append(f"Handler file not found: {api.file}")
            return self._finalize(api, steps, uncertainties)

        lines = read_lines(handler_file)
        body = "\n".join(lines[api.line - 1 : api.line + 8])
        call_match = HANDLER_SERVICE_CALL.search(body)

        if not call_match:
            uncertainties.append("Service call not resolved in handler")
            return self._finalize(api, steps, uncertainties)

        service_name, service_method = call_match.group(1), call_match.group(2)
        service = self.index.services.get(service_name)
        service_file = service.file if service else None
        service_line = None
        if service and service_method in service.methods:
            service_line = service.methods[service_method].start_line

        steps.append(
            FlowStep(
                layer="service",
                symbol=f"{service_name}.{service_method}",
                file=service_file,
                line=service_line,
            )
        )

        if not service:
            uncertainties.append(f"Service class not indexed: {service_name}")
            return self._finalize(api, steps, uncertainties)

        method = service.methods.get(service_method)
        if not method:
            uncertainties.append(f"Service method not found: {service_name}.{service_method}")
            return self._finalize(api, steps, uncertainties)

        repo_calls = SERVICE_REPO_CALL.findall("\n".join(method.body_lines))
        if not repo_calls:
            uncertainties.append(f"No repository calls in {service_name}.{service_method}")
            table = self._guess_table_from_handler(api.handler)
            if table:
                steps.append(
                    FlowStep(layer="database", symbol=f"table:{table}", operation="inferred")
                )
            return self._finalize(api, steps, uncertainties)

        seen_repo_steps = set()
        for attr, repo_method in repo_calls:
            repo_class = service.repo_attrs.get(attr)
            if not repo_class:
                uncertainties.append(f"Unknown repo attribute `_{attr}` on {service_name}")
                continue

            repo_key = f"{repo_class}.{repo_method}"
            if repo_key in seen_repo_steps:
                continue
            seen_repo_steps.add(repo_key)

            repo_info = self.index.repositories.get(repo_class)
            repo_file = repo_info.file if repo_info else None
            repo_line = (
                repo_info.methods[repo_method].start_line
                if repo_info and repo_method in repo_info.methods
                else None
            )

            steps.append(
                FlowStep(
                    layer="repository",
                    symbol=repo_key,
                    file=repo_file,
                    line=repo_line,
                )
            )

            table, table_uncertainties = self.index.resolve_repo_table(repo_class, repo_method)
            uncertainties.extend(table_uncertainties)
            if table:
                steps.append(
                    FlowStep(
                        layer="database",
                        symbol=f"table:{table}",
                        operation=self._db_operation(repo_method),
                    )
                )
            else:
                uncertainties.append(f"Database table unresolved for {repo_key}")

        return self._finalize(api, steps, uncertainties)

    def _finalize(
        self, api: ApiItem, steps: List[FlowStep], uncertainties: List[str]
    ) -> FlowTrace:
        unique_uncertainties = list(dict.fromkeys(uncertainties))
        confidence = self._score_confidence(steps, unique_uncertainties)
        trace = FlowTrace(
            endpoint=f"{api.method} {api.path}",
            steps=steps,
            confidence=confidence,
            uncertainties=unique_uncertainties,
            sequence_diagram=build_sequence_diagram(f"{api.method} {api.path}", steps),
        )
        trace.sync_chain_from_steps()
        return trace

    @staticmethod
    def _score_confidence(steps: List[FlowStep], uncertainties: List[str]) -> float:
        layers = {s.layer for s in steps}
        score = 0.4
        if "controller" in layers:
            score += 0.15
        if "service" in layers:
            score += 0.2
        if "repository" in layers:
            score += 0.15
        if "database" in layers:
            score += 0.1
        score -= 0.08 * len(uncertainties)
        return max(min(score, 1.0), 0.25)

    @staticmethod
    def _db_operation(method_name: str) -> str:
        if method_name.startswith("get") or method_name.startswith("find"):
            return "SELECT"
        if method_name.startswith("create") or method_name.startswith("save"):
            return "INSERT/UPDATE"
        if method_name.startswith("update"):
            return "UPDATE"
        if method_name.startswith("delete"):
            return "DELETE"
        return "SQL"

    @staticmethod
    def _guess_table_from_handler(handler: str) -> Optional[str]:
        hints = {
            "customer": "customers",
            "kyc": "kyc_submissions",
            "pan": "pan_records",
            "bank": "bank_records",
            "risk": "risk_assessments",
            "health": "",
            "metrics": "",
        }
        for key, table in hints.items():
            if key in handler.lower():
                return table or None
        return None


class SpringFlowTracer:
    """Best-effort Spring Boot flow tracing via controller → service naming."""

    def __init__(self, repo_path: Path, files: List[Path], inventories: Inventories):
        self.repo_path = repo_path
        self.inventories = inventories
        self.index = CodeIndex(repo_path, files)

    def trace_all(self) -> List[FlowTrace]:
        traces: List[FlowTrace] = []
        for api in self.inventories.apis:
            steps = [
                FlowStep(
                    layer="controller",
                    symbol=api.handler,
                    file=api.file,
                    line=api.line,
                    operation=f"{api.method} {api.path}",
                )
            ]
            uncertainties: List[str] = []
            handler_file = self.repo_path / api.file
            if handler_file.exists():
                body = "\n".join(read_lines(handler_file))
                svc_match = SPRING_SERVICE_FIELD.search(body)
                if svc_match:
                    svc_name, svc_method = svc_match.group(1), svc_match.group(2)
                    steps.append(FlowStep(layer="service", symbol=f"{svc_name}.{svc_method}"))
                    repo_name = svc_name.replace("Service", "Repository")
                    steps.append(FlowStep(layer="repository", symbol=f"{repo_name}.{svc_method}"))
                    table = svc_name.replace("Service", "").lower() + "s"
                    steps.append(
                        FlowStep(layer="database", symbol=f"table:{table}", operation="SQL")
                    )
                else:
                    uncertainties.append("Spring service injection not resolved statically")
            else:
                uncertainties.append(f"Controller file not found: {api.file}")

            trace = FlowTrace(
                endpoint=f"{api.method} {api.path}",
                steps=steps,
                confidence=0.55 if uncertainties else 0.75,
                uncertainties=uncertainties,
                sequence_diagram=build_sequence_diagram(f"{api.method} {api.path}", steps),
            )
            trace.sync_chain_from_steps()
            traces.append(trace)
        return traces
