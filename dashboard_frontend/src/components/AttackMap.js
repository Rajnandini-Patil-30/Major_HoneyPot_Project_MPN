import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { dashboardAPI } from '../api/dashboardAPI';
import 'leaflet/dist/leaflet.css';
import './AttackMap.css';

function AttackMap({ onPinClick }) {
  const [geoData, setGeoData] = useState([]);

  const fetchGeoData = useCallback(async () => {
    try {
      const res = await dashboardAPI.getGeoMap();
      setGeoData(res.data || []);
    } catch (err) {
      console.error('Error fetching geo map data:', err);
    }
  }, []);

  useEffect(() => {
    fetchGeoData();
    const interval = setInterval(fetchGeoData, 5000);
    return () => clearInterval(interval);
  }, [fetchGeoData]);

  const getRadius = (count) => {
    if (count >= 20) return 14;
    if (count >= 10) return 11;
    if (count >= 5) return 8;
    return 6;
  };

  return (
    <div className="attack-map-container">
      <div className="map-header">
        <span className="map-title">GLOBAL THREAT MAP</span>
        <span className="map-stats">{geoData.length} active origins</span>
      </div>
      <MapContainer
        center={[20, 0]}
        zoom={2}
        minZoom={2}
        maxZoom={8}
        className="attack-map"
        zoomControl={false}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          subdomains="abcd"
        />
        {geoData.map((pin, idx) => (
          <CircleMarker
            key={`${pin.ip}-${idx}`}
            center={[pin.latitude, pin.longitude]}
            radius={getRadius(pin.count)}
            pathOptions={{
              color: '#e74c3c',
              fillColor: '#e74c3c',
              fillOpacity: 0.7,
              weight: 1,
            }}
            className="attack-pin"
            eventHandlers={{
              click: () => onPinClick && onPinClick(pin),
            }}
          >
            <Popup className="attack-popup">
              <div className="popup-content">
                <div className="popup-ip">{pin.ip}</div>
                <div className="popup-location">
                  {pin.city}, {pin.country}
                </div>
                <div className="popup-count">{pin.count} attacks</div>
                <div className="popup-time">Last: {pin.last_seen}</div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}

export default AttackMap;
