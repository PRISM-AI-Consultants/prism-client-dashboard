# Agent Conventions

All agents in this directory inherit these base instructions.

## Shared Rules

1. **Single responsibility** — Each agent owns one domain and does it well
2. **Delegate I/O** — Agents never perform file I/O or API calls directly; they invoke tools
3. **Structured output** — All agent responses are JSON-serializable
4. **Error surfacing** — If a tool call fails, the agent reports the error upward with context rather than silently retrying
5. **Stateless** — Agents do not maintain state between invocations; all context is passed in

## Naming

- Files use `kebab-case` with role-noun format (e.g., `data-collector.md`, `analyst.md`)

## Response Format

Agents return results in this shape:
```json
{
  "ok": true,
  "result": { ... }
}
```

On failure:
```json
{
  "ok": false,
  "error": {
    "code": "AGENT_NAME/ERROR_TYPE",
    "message": "Human-readable explanation",
    "detail": {},
    "retryable": false
  }
}
```
