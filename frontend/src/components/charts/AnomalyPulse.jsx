import React, { useState } from 'react';
import { formatCurrency } from '../../utils/formatters';
import { RiskBadge } from '../common/RiskBadge';

export const AnomalyPulse = ({ anomalies = [], onSelectAnomaly }) => {
  const [hoveredAnomaly, setHoveredAnomaly] = useState(null);

  if (!anomalies || anomalies.length === 0) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted-dark)', fontSize: '13px' }}>
        No anomalies detected in the current telemetry window.
      </div>
    );
  }

  const displayAnomalies = anomalies.slice(0, 30);

  const getRiskColor = (level) => {
    const l = (level || '').toLowerCase();
    if (l === 'critical') return '#FF6B5C'; // Coral
    if (l === 'high') return '#F5B942';     // Amber
    if (l === 'medium') return '#B7F34A';   // Lime
    return '#A39F93';
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted-dark)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Observability Pulse Timeline ({anomalies.length} Telemetry Events)
        </div>
        <div style={{ display: 'flex', gap: '14px', fontSize: '11.5px', color: 'var(--text-cream)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#FF6B5C' }} /> Critical
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#F5B942' }} /> High
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#B7F34A' }} /> Medium
          </span>
        </div>
      </div>

      {/* Pulse Timeline Matrix */}
      <div 
        style={{ 
          backgroundColor: '#171717', 
          borderRadius: '8px', 
          padding: '22px', 
          display: 'flex', 
          alignItems: 'center', 
          justify: 'space-between', 
          gap: '10px',
          overflowX: 'auto',
          minHeight: '84px',
          border: '1px solid #333333'
        }}
      >
        {displayAnomalies.map((item, idx) => {
          const color = getRiskColor(item.risk_level);
          const isSelected = hoveredAnomaly === idx;

          return (
            <div
              key={idx}
              onClick={() => onSelectAnomaly && onSelectAnomaly(idx)}
              onMouseEnter={() => setHoveredAnomaly(idx)}
              onMouseLeave={() => setHoveredAnomaly(null)}
              style={{
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                backgroundColor: color,
                cursor: 'pointer',
                boxShadow: isSelected ? `0 0 14px ${color}` : `0 0 5px ${color}80`,
                transform: isSelected ? 'scale(1.45)' : 'scale(1)',
                transition: 'all 0.15s ease',
                flexShrink: 0
              }}
              title={`${item.date} - ${item.service} (${formatCurrency(item.actual_cost)})`}
            />
          );
        })}
      </div>

      {/* Hover / Click Preview Box */}
      {hoveredAnomaly !== null && displayAnomalies[hoveredAnomaly] && (
        <div 
          style={{ 
            marginTop: '14px', 
            backgroundColor: '#232323', 
            border: '1px solid #333333', 
            borderRadius: '8px', 
            padding: '14px 18px',
            display: 'flex',
            alignItems: 'center',
            justify: 'space-between'
          }}
        >
          <div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-cream)' }}>
              {displayAnomalies[hoveredAnomaly].service} Spike on {displayAnomalies[hoveredAnomaly].date}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted-dark)', fontFamily: 'JetBrains Mono' }}>
              Actual: {formatCurrency(displayAnomalies[hoveredAnomaly].actual_cost)} vs Expected: {formatCurrency(displayAnomalies[hoveredAnomaly].expected_cost)} (+{displayAnomalies[hoveredAnomaly].deviation_percentage}%)
            </div>
          </div>
          <RiskBadge level={displayAnomalies[hoveredAnomaly].risk_level} />
        </div>
      )}
    </div>
  );
};
