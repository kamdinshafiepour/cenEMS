/**
 * API client for CenEMS backend.
 */
import axios from 'axios';
import type { LatestReadingResponse, TimeSeriesResponse, Building, Device } from './types';

const API_BASE = '/api';

export const api = {
  // Get all buildings
  getBuildings: async (): Promise<Building[]> => {
    const response = await axios.get(`${API_BASE}/buildings`);
    return response.data.buildings;
  },

  // Get devices for a building
  getDevices: async (buildingId: string): Promise<Device[]> => {
    const response = await axios.get(`${API_BASE}/devices`, {
      params: { building_id: buildingId }
    });
    return response.data.devices;
  },

  // Get latest reading for a device
  getLatest: async (deviceId: string, metricType: string): Promise<LatestReadingResponse> => {
    const response = await axios.get(`${API_BASE}/latest`, {
      params: { device_id: deviceId, metric_type: metricType }
    });
    return response.data;
  },

  // Get time-series data
  getTimeSeries: async (
    deviceId: string,
    metricType: string,
    start: string,
    end: string
  ): Promise<TimeSeriesResponse> => {
    const response = await axios.get(`${API_BASE}/timeseries`, {
      params: {
        device_id: deviceId,
        metric_type: metricType,
        start,
        end
      }
    });
    return response.data;
  }
};
