import React from 'react';
import { RiskBadge } from './RiskBadge';
import { ArrowRight, Zap } from 'lucide-react';

export const ActionCenter = ({ recommendations = [], onNavigateToRecommendations }) => {
  const topRecommendations = (recommendations || []).slice(0, 4);

  return (
    <div className="dark-panel" style={{ marginBottom: 0 }}>
      <div className="dark-panel-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap size={20} color="var(--accent-lime)" />
          <div>
            <h3 className="dark-panel-title">ACTION CENTER</h3>
            <p className="dark-panel-subtitle">Operational cost optimization queue</p>
          </div>
        </div>
        <button className="btn btn-sm btn-primary" onClick={onNavigateToRecommendations}>
          <span>VIEW ALL</span>
          <ArrowRight size={13} />
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {topRecommendations.map((item, idx) => (
          <div 
            key={idx} 
            style={{ 
              border: '1px solid var(--border-dark)', 
              borderRadius: '8px', 
              padding: '16px 18px',
              backgroundColor: 'var(--bg-dark-panel)',
              transition: 'all 0.15s ease'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-cream)' }}>
                {item.service} — {item.category}
              </span>
              <RiskBadge level={item.priority} />
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-muted-dark)', marginBottom: '12px', lineHeight: 1.4 }}>
              {item.action}
            </p>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '11.5px', color: 'var(--text-muted-dark)' }}>
                {item.provider} • {item.region}
              </span>
              <button 
                className="btn btn-sm" 
                onClick={onNavigateToRecommendations}
                style={{ fontSize: '11px', padding: '4px 10px', backgroundColor: '#333333', color: '#F4F1E8', borderColor: '#444444' }}
              >
                VIEW ANALYSIS
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
