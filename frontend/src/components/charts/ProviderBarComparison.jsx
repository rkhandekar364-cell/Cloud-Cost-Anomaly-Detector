import React from 'react';
import { formatCurrency } from '../../utils/formatters';

export const ProviderBarComparison = ({ data = [] }) => {
  if (!data || data.length === 0) return null;

  const totalSpend = data.reduce((acc, curr) => acc + (curr.total_cost || 0), 0);

  const getProviderColor = (provider) => {
    const p = (provider || '').toLowerCase();
    if (p.includes('aws') || p.includes('amazon')) return '#B7F34A'; // Electric Lime
    if (p.includes('azure') || p.includes('microsoft')) return '#F5B942'; // Amber
    if (p.includes('gcp') || p.includes('google')) return '#63D6A2'; // Mint
    return '#EAE6DA';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {data.map((item, idx) => {
        const cost = item.total_cost || 0;
        const percentage = totalSpend > 0 ? ((cost / totalSpend) * 100).toFixed(1) : 0;
        const barColor = getProviderColor(item.cloud_provider);

        return (
          <div 
            key={item.cloud_provider || idx} 
            style={{ 
              backgroundColor: 'var(--bg-dark-panel)', 
              padding: '16px 18px', 
              borderRadius: '8px', 
              border: '1px solid var(--border-dark)' 
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: barColor }} />
                <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-cream)' }}>
                  {item.cloud_provider}
                </span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-cream)', fontFamily: 'JetBrains Mono', marginRight: '8px' }}>
                  {formatCurrency(cost)}
                </span>
                <span style={{ fontSize: '12.5px', fontWeight: 600, color: barColor, fontFamily: 'JetBrains Mono' }}>
                  ({percentage}%)
                </span>
              </div>
            </div>

            {/* Horizontal Provider Lane Bar */}
            <div style={{ width: '100%', height: '10px', backgroundColor: '#333333', borderRadius: '5px', overflow: 'hidden' }}>
              <div 
                style={{ 
                  width: `${percentage}%`, 
                  height: '100%', 
                  backgroundColor: barColor, 
                  borderRadius: '5px',
                  transition: 'width 0.5s ease-out'
                }} 
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};
