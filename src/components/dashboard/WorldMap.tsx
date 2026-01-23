// src/components/dashboard/WorldMap.tsx
'use client';

import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { Alert } from '@/types/alert';

type WorldMapProps = {
  alerts: Alert[];
};

const severityColor = (severity: Alert['severity']) => {
  switch (severity) {
    case 'CRITICAL':
    case 'HIGH':
      return '#E57373'; // primary-red
    case 'MEDIUM':
      return '#FFB74D'; // caution-amber
    case 'LOW':
    default:
      return '#81C784'; // safe-green
  }
};

export default function WorldMap({ alerts }: WorldMapProps) {
  return (
    <MapContainer
      center={[20, 0]}
      zoom={2}
      scrollWheelZoom={false}
      style={{ height: '100%', width: '100%', borderRadius: 12, overflow: 'hidden' }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {alerts
        .filter((a) => a.location)
        .map((alert) => (
          <CircleMarker
            key={alert.id}
            center={[alert.location!.lat, alert.location!.lng]}
            radius={10}
            pathOptions={{
              color: severityColor(alert.severity),
              fillColor: severityColor(alert.severity),
              fillOpacity: 0.7
            }}
          >
            <Tooltip direction="top" offset={[0, -8]} opacity={1}>
              <div className="text-xs">
                <p className="font-semibold">{alert.title}</p>
                <p>
                  {alert.impactedPoCount} POs · $
                  {alert.estimatedRevenueImpact.toLocaleString()}
                </p>
              </div>
            </Tooltip>
          </CircleMarker>
        ))}
    </MapContainer>
  );
}
