                 @echo off
REM CenEMS API Examples - Test all endpoints and edge cases (Windows Version)

set BASE_URL=http://localhost:8000

echo ================================
echo CenEMS API Testing Script
echo ================================
echo.

REM Health check
echo 1. Testing health endpoint...
curl -X GET "%BASE_URL%/health"
echo.
echo.

REM Ingest normal sequence
echo 2. Ingesting normal event sequence (meter-001)...
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-001\", \"building_id\": \"building-a\", \"timestamp\": \"2026-01-15T10:00:00Z\", \"metric_type\": \"energy\", \"value\": 1000.0, \"unit\": \"kWh\"}"
echo.

curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-001\", \"building_id\": \"building-a\", \"timestamp\": \"2026-01-15T11:00:00Z\", \"metric_type\": \"energy\", \"value\": 1012.5, \"unit\": \"kWh\"}"
echo.

curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-001\", \"building_id\": \"building-a\", \"timestamp\": \"2026-01-15T12:00:00Z\", \"metric_type\": \"energy\", \"value\": 1025.3, \"unit\": \"kWh\"}"
echo.

REM Test duplicate detection
echo 3. Testing duplicate detection (sending same event twice)...
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-002\", \"building_id\": \"building-a\", \"timestamp\": \"2026-01-15T10:00:00Z\", \"metric_type\": \"energy\", \"value\": 500.0, \"unit\": \"kWh\"}"
echo.

echo Sending duplicate...
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-002\", \"building_id\": \"building-a\", \"timestamp\": \"2026-01-15T10:00:00Z\", \"metric_type\": \"energy\", \"value\": 500.0, \"unit\": \"kWh\"}"
echo.

REM Test counter reset
echo 4. Testing counter reset detection...
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-003\", \"building_id\": \"building-b\", \"timestamp\": \"2026-01-15T10:00:00Z\", \"metric_type\": \"energy\", \"value\": 9950.0, \"unit\": \"kWh\"}"
echo.

curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-003\", \"building_id\": \"building-b\", \"timestamp\": \"2026-01-15T11:00:00Z\", \"metric_type\": \"energy\", \"value\": 50.0, \"unit\": \"kWh\"}"
echo.

REM Test out-of-order
echo 5. Testing out-of-order event handling...
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-004\", \"building_id\": \"building-b\", \"timestamp\": \"2026-01-15T10:00:00Z\", \"metric_type\": \"energy\", \"value\": 2000.0, \"unit\": \"kWh\"}"
echo.

curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-004\", \"building_id\": \"building-b\", \"timestamp\": \"2026-01-15T12:00:00Z\", \"metric_type\": \"energy\", \"value\": 2050.0, \"unit\": \"kWh\"}"
echo.

echo Sending late event (should be flagged as out-of-order)...
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-004\", \"building_id\": \"building-b\", \"timestamp\": \"2026-01-15T11:00:00Z\", \"metric_type\": \"energy\", \"value\": 2025.0, \"unit\": \"kWh\"}"
echo.

REM Test unit conversions
echo 6. Testing unit conversions...
echo Wh to kWh:
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-005\", \"building_id\": \"building-c\", \"timestamp\": \"2026-01-15T10:00:00Z\", \"metric_type\": \"energy\", \"value\": 5000, \"unit\": \"Wh\"}"
echo.

echo MWh to kWh:
curl -X POST "%BASE_URL%/ingest" -H "Content-Type: application/json" -d "{\"device_id\": \"meter-006\", \"building_id\": \"building-c\", \"timestamp\": \"2026-01-15T10:00:00Z\", \"metric_type\": \"energy\", \"value\": 2.5, \"unit\": \"MWh\"}"
echo.

REM Query endpoints
echo 7. Testing query endpoints...
echo Get all buildings:
curl -X GET "%BASE_URL%/buildings"
echo.

echo Get devices for building-a:
curl -X GET "%BASE_URL%/devices?building_id=building-a"
echo.

echo Get latest reading for meter-001:
curl -X GET "%BASE_URL%/latest?device_id=meter-001&metric_type=energy"
echo.

echo Get latest reading for meter-003 (should show counter_reset flag):
curl -X GET "%BASE_URL%/latest?device_id=meter-003&metric_type=energy"
echo.

echo Get time-series for meter-004 (should show out_of_order flag):
curl -X GET "%BASE_URL%/timeseries?device_id=meter-004&metric_type=energy&start=2026-01-15T00:00:00Z&end=2026-01-15T23:59:59Z"
echo.

echo ================================
echo Testing complete!
echo ================================
pause
