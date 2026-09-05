import React from 'react';
import { X } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';
import { RiskBadge } from './RiskBadge';
import { LoadingState } from './LoadingState';

export const AnomalyDrawer = ({ isOpen, onClose, analysisData, loading }) => {
  if (!isOpen) return null;

  const anomaly = analysisData?.anomaly;
  const rootCause = analysisData?.root_cause;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="drawer-header">
          <div>
            <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--accent-lime)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Observability Investigation
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-cream)', marginTop: '2px', textTransform: 'uppercase' }}>
              ANOMALY DETAILS
            </h2>
          </div>
          <button className="btn btn-sm" onClick={onClose} style={{ padding: '6px' }}>
            <X size={18} color="var(--text-cream)" />
          </button>
        </div>

        {/* Body */}
        <div className="drawer-body">
          {loading ? (
            <LoadingState message="Investigating telemetry dimensions & empirical root cause..." />
          ) : anomaly ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              {/* Summary Banner */}
              <div style={{ backgroundColor: 'var(--bg-dark-panel)', border: '1px solid var(--border-dark)', borderRadius: '8px', padding: '18px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-cream)' }}>
                    {anomaly.service}
                  </span>
                  <RiskBadge level={anomaly.risk_level} />
                </div>
                <div style={{ fontSize: '12.5px', color: 'var(--text-muted-dark)' }}>
                  Detected on <strong>{anomaly.date}</strong> across {anomaly.cloud_provider} ({anomaly.region})
                </div>
              </div>

              {/* Cost Comparison */}
              <div>
                <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted-dark)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '10px' }}>
                  Cost Comparison
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', backgroundColor: 'var(--bg-dark-panel)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-dark)' }}>
                  <div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted-dark)' }}>Actual Cost</div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: '#FF6B5C', fontFamily: 'JetBrains Mono' }}>{formatCurrency(anomaly.actual_cost)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted-dark)' }}>Expected Baseline</div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-cream)', fontFamily: 'JetBrains Mono' }}>{formatCurrency(anomaly.expected_cost)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted-dark)' }}>Deviation</div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: '#FF6B5C', fontFamily: 'JetBrains Mono' }}>+{anomaly.deviation_percentage}%</div>
                  </div>
                </div>
              </div>

              {/* WHY IT HAPPENED (Root-Cause Analysis) */}
              <div>
                <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted-dark)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '10px' }}>
                  WHY IT HAPPENED
                </h4>
                <div style={{ backgroundColor: 'var(--bg-dark-panel)', border: '1px solid var(--border-dark)', borderRadius: '8px', padding: '16px' }}>
                  <p style={{ fontSize: '13.5px', color: 'var(--text-cream)', lineHeight: 1.5, marginBottom: '14px' }}>
                    {rootCause?.summary}
                  </p>

                  <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted-dark)', marginBottom: '10px', textTransform: 'uppercase' }}>
                    Contributing Dimensions:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {rootCause?.contributing_factors?.map((f) => (
                      <div key={f.rank} style={{ borderLeft: '3px solid var(--accent-lime)', backgroundColor: '#1A1A1A', padding: '10px 14px', borderRadius: '0 6px 6px 0', border: '1px solid var(--border-dark)', borderLeftWidth: '3px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 700, color: 'var(--text-cream)' }}>
                          <span>{f.rank}. {f.title}</span>
                          <span style={{ color: '#FF6B5C', fontFamily: 'JetBrains Mono' }}>+{formatCurrency(f.impact_amount)}</span>
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted-dark)', marginTop: '4px' }}>
                          {f.description}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* WHAT TO DO (Recommendations) */}
              <div>
                <h4 style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted-dark)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '10px' }}>
                  WHAT TO DO
                </h4>
                <div style={{ backgroundColor: '#2A241A', border: '1px solid #F5B942', borderRadius: '8px', padding: '16px' }}>
                  <div style={{ fontSize: '13.5px', fontWeight: 700, color: '#F5B942', marginBottom: '6px' }}>
                    Action: {anomaly.recommendation}
                  </div>
                  <div style={{ fontSize: '12.5px', color: '#EAE6DA' }}>
                    Reasoning: {anomaly.reason}
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="drawer-footer">
          <button className="btn btn-primary" onClick={onClose}>
            DONE REVIEWING
          </button>
        </div>
      </div>
    </div>
  );
};
