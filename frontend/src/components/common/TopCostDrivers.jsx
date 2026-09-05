import React from 'react';
import { formatCurrency } from '../../utils/formatters';

export const TopCostDrivers = ({ drivers = [] }) => {
  const displayDrivers = (drivers || []).slice(0, 5);

  return (
    <div className="dark-panel" style={{ marginBottom: 0 }}>
      <div className="dark-panel-header">
        <div>
          <h3 className="dark-panel-title">TOP COST DRIVERS</h3>
          <p className="dark-panel-subtitle">Services driving 30-day spending growth</p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {displayDrivers.map((item, idx) => {
          const rankFormatted = String(item.rank || idx + 1).padStart(2, '0');
          const isPositive = (item.cost_change || 0) > 0;

          return (
            <div 
              key={item.rank || idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justify: 'space-between',
                padding: '14px 16px',
                border: '1px solid var(--border-dark)',
                borderRadius: '8px',
                backgroundColor: 'var(--bg-dark-panel)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span style={{ fontSize: '15px', fontWeight: 800, color: 'var(--accent-lime)', fontFamily: 'JetBrains Mono' }}>
                  {rankFormatted}
                </span>
                <div>
                  <div style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-cream)' }}>
                    {item.service}
                  </div>
                  <div style={{ fontSize: '11.5px', color: 'var(--text-muted-dark)', fontFamily: 'JetBrains Mono' }}>
                    {item.contribution_percentage}% of total increase
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '15px', fontWeight: 700, color: isPositive ? '#FF6B5C' : '#63D6A2', fontFamily: 'JetBrains Mono' }}>
                  {isPositive ? '+' : ''}{formatCurrency(item.cost_change)}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted-dark)' }}>
                  Net 30-day shift
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
