import React from 'react';

export const KpiCard = ({ title, value, subtext, icon: Icon, trend, color = 'var(--primary-blue)' }) => {
  return (
    <div className="kpi-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span className="kpi-title">{title}</span>
        {Icon && (
          <div style={{ width: '32px', height: '32px', borderRadius: '6px', backgroundColor: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Icon size={16} color={color} />
          </div>
        )}
      </div>
      <div className="kpi-value">{value}</div>
      {subtext && <div className="kpi-subtext">{subtext}</div>}
    </div>
  );
};
