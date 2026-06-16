FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --omit=dev

COPY bin ./bin
COPY lib ./lib
COPY commands ./commands

ENV API_BASE_URL=http://onboarding-api:8000

ENTRYPOINT ["node", "bin/kyc-cli.js"]
