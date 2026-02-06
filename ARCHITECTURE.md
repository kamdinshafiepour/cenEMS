# Architecture

## Design Principles

1. **Correctness over performance**: Data accuracy is priority
2. **Transparency**: Flag issues, don't hide them
3. **Idempotency**: All operations safe to retry
4. **Audit trail**: Never lose original data

## Technology Choices

**FastAPI**: Auto-generated docs, async support, type safety

**PostgreSQL**: ACID guarantees, JSONB support, time-series capable

**SQLAlchemy**: Type-safe ORM, migrations via Alembic

**React**: Component-based UI, TypeScript for safety

## Configuration

Backend reads `DATABASE_URL` from environment via Pydantic BaseSettings.

**Local dev**: Credentials in docker-compose.yml (simple setup)

**Production**: Use `.env` file (gitignored) with `${POSTGRES_PASSWORD}` substitution

**Trade-off**: Convenience for exercise vs production security

## Data Model

### Separation Strategy

Two tables:
- **raw_events**: Immutable audit log (JSONB payload)
- **normalized_measurements**: Queryable time-series (indexed)

**Why**: Audit trail + query performance. Can re-normalize if rules change.

**Trade-off**: Storage overhead (~2x). Acceptable for data integrity.

## Deduplication

### Problem
Retries, network issues, client buffering cause duplicate events.

### Solution
```python
event_id = sha256(f"{device_id}|{timestamp}|{metric_type}|{value}")
```

**Properties**:
- Deterministic: same input = same ID
- No external state (no Redis needed)
- Collision-resistant (SHA256)
- Fast (~1μs)

**Alternative considered**: Client UUIDs. Rejected: requires client coordination.

## Counter Reset Detection

### Problem
Meters reset when replaced, power cycled, or firmware updated.

### Solution
```python
delta = current_value - previous_value
if delta < 0:
    return {"delta": None, "flags": ["counter_reset"]}
```

**Why NULL delta**: Cannot compute meaningful consumption across reset.

**Why flag instead of fix**: Per requirements - transparency over silent correction. Users need to know resets occurred.

## Out-of-Order Handling

### Problem
Events arrive late due to network delays, buffering, clock skew.

### Solution
1. Accept all events (no rejection)
2. Detect: compare timestamp with existing data
3. Insert at correct position
4. Recompute delta for next measurement
5. Flag with `out_of_order`

**Trade-off**: 4 queries per out-of-order event. Acceptable for demo scale.

**Alternative considered**: Time window buffering. Rejected: adds complexity, state.

## Quality Flags

Array of strings in normalized_measurements:
- `first_reading`: No previous measurement
- `counter_reset`: Negative delta
- `out_of_order`: Late arrival
- `suspicious_jump`: Delta > 10,000 kWh

**Why array**: Multiple flags possible (e.g., out_of_order + suspicious_jump).

## Scalability

### Current Scale
- ~1,000 devices
- ~100 events/sec
- Single server

### Bottlenecks
1. **Synchronous normalization**: ~500 events/sec max
   - Solution: Celery + RabbitMQ

2. **Out-of-order recomputation**: 4 queries each
   - Solution: Batch updates

3. **Connection pooling**: 5 connections
   - Solution: PgBouncer

### Production Changes
- TimescaleDB for automatic partitioning
- Async processing queue
- Connection pooler
- API rate limiting
- Authentication (OAuth2)

## Testing Strategy

23 unit tests using pytest with SQLite in-memory database.

Coverage:
- Edge cases: duplicates, counter resets, out-of-order, large jumps
- Unit conversions: Wh, MWh → kWh
- Timestamp normalization: All timezones → UTC
- Delta computation: First readings, resets, negative values

## Conclusion

Architecture optimized for correctness and transparency. Simple enough for 4-5 hour implementation, clear upgrade path for production.

Key decisions:
* Deterministic deduplication (no race conditions)
* Transparent quality flags (no silent fixes)
* Audit trail (raw + normalized storage)
* Correct deltas (even with out-of-order data)
