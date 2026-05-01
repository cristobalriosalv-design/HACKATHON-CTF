FROM oven/bun:1.2.2-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN bun install

COPY . .
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN bun run build

FROM oven/bun:1.2.2-alpine

WORKDIR /app
COPY package.json ./
RUN bun install --production
COPY --from=builder /app/dist ./dist

EXPOSE 5173
CMD ["bun", "run", "preview"]
