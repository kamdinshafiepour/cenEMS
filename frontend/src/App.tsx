/**
 * CenEMS Dashboard - Main Application Component
 */
import { useState, useEffect } from 'react';
import { api } from './api';
import type { Building, Device, Measurement } from './types';
import './App.css';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function App() {
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [selectedBuilding, setSelectedBuilding] = useState<string | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string | null>(null);
  const [latestReading, setLatestReading] = useState<Measurement | null>(null);
  const [timeSeries, setTimeSeries] = useState<Measurement[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load buildings on mount
  useEffect(() => {
    loadBuildings();
  }, []);

  // Load devices when building is selected
  useEffect(() => {
    if (selectedBuilding) {
      loadDevices(selectedBuilding);
    }
  }, [selectedBuilding]);

  // Load latest reading and time-series when device is selected
  useEffect(() => {
    if (selectedDevice) {
      loadLatestReading(selectedDevice);
      loadTimeSeries(selectedDevice);
    }
  }, [selectedDevice]);

  const loadBuildings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getBuildings();
      setBuildings(data);
    } catch (err) {
      setError('Failed to load buildings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadDevices = async (buildingId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDevices(buildingId);
      setDevices(data);
      setSelectedDevice(null); // Reset device selection
    } catch (err) {
      setError('Failed to load devices');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadLatestReading = async (deviceId: string) => {
    try {
      const data = await api.getLatest(deviceId, 'energy');
      setLatestReading(data.latest_reading);
    } catch (err) {
      console.error('Failed to load latest reading:', err);
    }
  };

  const loadTimeSeries = async (deviceId: string) => {
    try {
      // Get last 30 days of data
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 30);

      const data = await api.getTimeSeries(
        deviceId,
        'energy',
        start.toISOString(),
        end.toISOString()
      );
      setTimeSeries(data.measurements);
    } catch (err) {
      console.error('Failed to load time-series:', err);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>CenEMS Telemetry Dashboard</h1>
        <p>Energy Monitoring & Management System</p>
      </header>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Loading...</div>}

      {/* Buildings Section */}
      <section className="section">
        <h2>Buildings</h2>
        <div className="button-group">
          {buildings.length === 0 && !loading && (
            <p className="empty">No buildings found. Ingest some data first!</p>
          )}
          {buildings.map((building) => (
            <button
              key={building.building_id}
              className={selectedBuilding === building.building_id ? 'active' : ''}
              onClick={() => setSelectedBuilding(building.building_id)}
            >
              {building.name || building.building_id}
              <span className="badge">{building.device_count} devices</span>
            </button>
          ))}
        </div>
      </section>

      {/* Devices Section */}
      {selectedBuilding && (
        <section className="section">
          <h2>Devices in {buildings.find(b => b.building_id === selectedBuilding)?.name}</h2>
          <div className="button-group">
            {devices.length === 0 && <p className="empty">No devices in this building</p>}
            {devices.map((device) => (
              <button
                key={device.device_id}
                className={selectedDevice === device.device_id ? 'active' : ''}
                onClick={() => setSelectedDevice(device.device_id)}
              >
                {device.name || device.device_id}
                {device.location && <span className="location">📍 {device.location}</span>}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Latest Reading Section */}
      {selectedDevice && latestReading && (
        <section className="section">
          <h2>Latest Reading - {selectedDevice}</h2>
          <div className="reading-card">
            <div className="reading-row">
              <span className="label">Timestamp:</span>
              <span>{new Date(latestReading.timestamp).toLocaleString()}</span>
            </div>
            <div className="reading-row">
              <span className="label">Value:</span>
              <span className="value">{latestReading.value.toFixed(2)} {latestReading.unit}</span>
            </div>
            <div className="reading-row">
              <span className="label">Consumption:</span>
              <span className="delta">
                {latestReading.delta_value !== null
                  ? `${latestReading.delta_value.toFixed(2)} ${latestReading.unit}`
                  : 'N/A'}
              </span>
            </div>
            <div className="reading-row">
              <span className="label">Quality Flags:</span>
              <div className="flags">
                {latestReading.quality_flags.length === 0 && (
                  <span className="flag clean">Clean</span>
                )}
                {latestReading.quality_flags.map((flag) => (
                  <span
                    key={flag}
                    className={`flag ${flag === 'counter_reset' ? 'error' : 'warning'}`}
                  >
                    {flag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Time-Series Chart Section */}
      {selectedDevice && timeSeries.length > 0 && (
        <section className="section">
          <h2>Energy Consumption (Last 30 Days)</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeSeries}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis label={{ value: 'kWh', angle: -90, position: 'insideLeft' }} />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  formatter={(value) => [`${Number(value).toFixed(2)} kWh`, 'Energy']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  name="Energy (kWh)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {selectedDevice && timeSeries.length === 0 && (
        <section className="section">
          <p className="empty">No time-series data available for this device</p>
        </section>
      )}
    </div>
  );
}

export default App;
