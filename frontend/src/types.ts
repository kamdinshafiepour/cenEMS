/**
 * TypeScript type definitions for CenEMS telemetry data.
 */

export interface Measurement {
  timestamp: string;
  value: number;
  unit: string;
  delta_value: number | null;
  quality_flags: string[];
}

export interface LatestReadingResponse {
  device_id: string;
  building_id: string;
  metric_type: string;
  latest_reading: Measurement | null;
}

export interface TimeSeriesResponse {
  device_id: string;
  metric_type: string;
  measurements: Measurement[];
}

export interface Building {
  building_id: string;
  name: string;
  device_count: number;
}

export interface Device {
  device_id: string;
  building_id: string;
  name: string | null;
  location: string | null;
}
