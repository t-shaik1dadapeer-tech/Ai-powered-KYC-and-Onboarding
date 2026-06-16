from intelligence.generators.api_map import generate_api_map
from intelligence.generators.er_diagram import generate_er_diagram
from intelligence.models import AnalysisResult, ApiItem, ModelItem


def test_er_diagram():
    models = [
        ModelItem(name="Customer", table="customers", file="models/customer.py", line=1),
        ModelItem(name="Order", table="orders", file="models/order.py", line=1),
    ]
    diagram = generate_er_diagram(models)
    assert "erDiagram" in diagram
    assert "CUSTOMERS" in diagram


def test_api_map():
    result = AnalysisResult.empty("/repo", "fastapi", 0.9)
    result.inventories.apis = [
        ApiItem(method="GET", path="/health", handler="health", file="health.py", line=1)
    ]
    content = generate_api_map(result)
    assert "GET" in content
    assert "/health" in content
