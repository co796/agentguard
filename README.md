# AgentGuard

Lightweight local security monitoring layer built with Python, FastAPI and SQLite.

## Features

- Local security event logging
- FastAPI REST API
- SQLite event storage
- Health monitoring endpoint
- Structured event records
- Fully local execution

## API

### Health check

GET `/health`

Returns the current service status.

### Create event

POST `/events`

Example:

```json
{
  "event_type": "warning",
  "source": "local-monitor",
  "message": "Example security event"
}
