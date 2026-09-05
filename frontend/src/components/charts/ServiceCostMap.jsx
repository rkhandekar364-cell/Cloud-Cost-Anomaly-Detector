import React from 'react';
import { formatCurrency } from '../../utils/formatters';

export const ServiceCostMap = ({ data = [] }) => {
  if (!data || data.length === 0) return null;

  const totalSpend = data.reduce((acc, curr) => acc + (curr.total_cost || 0), 0);

  // Control Room color accents (Lime, Amber, Mint, Cream)
  const colors = [
    '#B7F34A', '#F5B942', '#63D6A2', '#EAE6DA', '#D97706', '#A3E635'
  ];

  return (
    <div>
      <div className="service-map-grid">
        {data.map((svc, idx) => {
          const cost = svc.total_cost || 0;
          const percentage = totalSpend > 0 ? ((cost / totalSpend) * 100).toFixed(1) : 0;
          const accentColor = colors[idx % colors.length];

          return (
            <div 
              key={svc.service || idx} 
              className="service-block"
              title={`${svc.service}: ${formatCurrency(cost)} (${percentage}% of spend)`}
            >
              <div className="service-block-bar" style={{ backgroundColor: accentColor }} />
              
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-cream)' }}>
                  {svc.service}
                </span>
                <span 
                  style={{ 
                    fontSize: '11px', 
                    fontWeight: 700, 
                    color: '#171717', 
                    backgroundColor: accentColor, 
                    padding: '2px 6px', 
                    borderRadius: '4px',
                    fontFamily: 'JetBrains Mono'
                  }}
                >
                  {percentage}%
                </span>
              </div>

              <div style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-cream)', fontFamily: 'JetBrains Mono', marginBottom: '4px' }}>
                {formatCurrency(cost)}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11.5px', color: 'var(--text-muted-dark)' }}>
                <span>{svc.cloud_provider || 'AWS'}</span>
                <span>{svc.record_count ?? ''} records</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
