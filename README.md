# CenEMS - Energy Telemetry Service

Energy monitoring telemetry ingestion and normalization service with counter reset detection and out-of-order event handling.

## Features

- Telemetry ingestion with automatic deduplication (idempotent)
- Unit normalization (Wh/MWh → kWh)
- Counter reset detection (flags negative deltas, doesn't correct)
- Out-of-order event handling with delta recomputation
- Quality indicators (first_reading, counter_reset, out_of_order, suspicious_jump)
- REST API for queries (latest, time-series)
- React dashboard for visualization

## Quick Start

### Prerequisites
- Docker & Docker Compose

### Run
```bash
docker-compose up --build
```

Access:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432

### Local Development (Optional)
```bash
# Start database
docker-compose up postgres -d

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev
```

## API Endpoints

### POST /ingest
Ingest telemetry event.

Request:
```json
{
  "device_id": "meter-001",
  "building_id": "building-a",
  "timestamp": "2026-01-01T10:00:00Z",
  "metric_type": "energy",
  "value": 1234.56,
  "unit": "kWh"
}
```

Response: `201 Created` or `200 OK` (duplicate)

### GET /latest?device_id=X&metric_type=energy
Get most recent reading with quality flags and delta.

### GET /timeseries?device_id=X&metric_type=energy&start=...&end=...
Get historical measurements with quality metadata.

### GET /buildings
List all buildings with device counts.

### GET /devices?building_id=X
List devices in a building.

## Testing

```bash
cd backend
pytest -v
```

23 tests covering:
- Deduplication (SHA256 event IDs)
- Counter reset detection
- Out-of-order handling
- Unit conversions
- Timestamp normalization

## Demo Scripts

```bash
# Windows
examples\api-examples.bat

# Mac/Linux
bash examples/api-examples.sh
```

Demonstrates: normal sequences, duplicates, counter resets, out-of-order events, unit conversions.

## Design Decisions

### Deduplication
SHA256 hash of `device_id|timestamp|metric_type|value`. Deterministic, no external state needed.

### Counter Reset Detection
Per requirements: "flag rather than silently corrected."
- Detect: delta < 0
- Action: Set delta=NULL, add `counter_reset` flag
- Why: Transparency over silent fixes

### Out-of-Order Events
Accept all events regardless of order. Recompute affected deltas. Flag with `out_of_order`.

### Separate Raw/Normalized Storage
- `raw_events`: Immutable audit log
- `normalized_measurements`: Queryable time-series

Enables audit trail and re-normalization if rules change.

## Architecture

```
Device → POST /ingest → FastAPI → PostgreSQL
                          ↓
                       React UI
```

**Stack**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, React, TypeScript

**Database**:
- `raw_events`: Original payloads (JSONB)
- `normalized_measurements`: Processed data with quality flags (ARRAY)
- `buildings`, `devices`: Metadata

## Project Structure

```
cenEMS/
├── backend/
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   └── utils/       # Helpers
│   ├── tests/           # Unit tests (pytest)
│   └── alembic/         # Migrations
├── frontend/            # React + TypeScript
├── examples/            # API demo scripts
└── docker-compose.yml
```

## Trade-offs

**PostgreSQL vs TimescaleDB**: PostgreSQL for simplicity. Production should use TimescaleDB.

**Synchronous normalization**: Acceptable for demo (<100ms latency). Production should use async queue (Celery).

**SHA256 event IDs**: Client-provided UUIDs would also work but require coordination.

## License

MIT
