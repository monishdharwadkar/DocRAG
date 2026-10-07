# REST & gRPC API Design Standards

## Principles
All internal and public APIs must strictly adhere to our unified OpenAPI 3.0 specification.

## URL Naming Standards
- Resource names must use plural nouns (e.g., `/api/v1/deployments`, `/api/v1/users`).
- Use kebab-case for URL path segments and parameter keys.
- Always include versioning prefix `/api/v1/` in all endpoint paths.

## Error Response Format
All error responses must return standard JSON payload:
```json
{
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "The requested resource could not be found.",
  "timestamp": "2026-10-07T12:00:00Z",
  "details": []
}
```

## Pagination & Filtering
- Pagination parameters: `page` (default 1) and `limit` (default 20, max 100).
- Response pagination envelope must include `total_count`, `total_pages`, `current_page`.
