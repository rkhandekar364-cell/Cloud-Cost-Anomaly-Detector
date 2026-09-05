import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { RiskBadge } from '../components/common/RiskBadge';
import { formatCurrency } from '../utils/formatters';
import { Filter } from 'lucide-react';

export const Recommendations = ({ activeMeta }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recData, setRecData] = useState(null);
  const [driversData, setDriversData] = useState(null);
  const [insightsData, setInsightsData] = useState(null);
  const [priorityFilter, setPriorityFilter] = useState('All');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [rData, dData, iData] = await Promise.all([
        api.getRecommendations(),
        api.getCostDrivers(),
        api.getBusinessInsights(),
      ]);

      setRecData(rData);
      setDriversData(dData);
      setInsightsData(iData);
    } catch (err) {
      setError(err.message || 'Failed to load recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeMeta]);

  if (loading) return <LoadingState message="Generating evidence-based optimization action board..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const recommendations = recData?.recommendations || [];
  const topDriver = driversData?.drivers?.[0];
  const topOpportunity = insightsData?.insights?.find((i) => i.id === 'largest_service');

  const filtered = recommendations.filter((r) => {
    if (priorityFilter !== 'All' && r.priority !== priorityFilter) return false;
    return true;
  });

  return (
    <div className="content-wrapper">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">RECOMMENDATIONS</h1>
          <p className="page-subtitle">Prioritized operational action board derived from billing telemetry & anomaly observations.</p>
        </div>
      </div>

      {/* Metric Rail */}
      <div className="metric-rail">
        <div className="metric-rail-item">
          <div className="metric-rail-label">Critical Actions</div>
          <div className="metric-rail-value" style={{ color: '#FF6B5C' }}>{recData?.critical || 0}</div>
          <div className="metric-rail-subtext">Immediate review required</div>
        </div>

        <div className="metric-rail-item">
          <div className="metric-rail-label">High Priority</div>
          <div className="metric-rail-value" style={{ color: '#F5B942' }}>{recData?.high || 0}</div>
          <div className="metric-rail-subtext">Significant potential savings</div>
        </div>

        <div className="metric-rail-item">
          <div className="metric-rail-label">Medium Priority</div>
          <div className="metric-rail-value" style={{ color: '#B7F34A' }}>{recData?.medium || 0}</div>
          <div className="metric-rail-subtext">Moderate baseline deviation</div>
        </div>

        <div className="metric-rail-item">
          <div className="metric-rail-label">Low Priority</div>
          <div className="metric-rail-value" style={{ color: '#A39F93' }}>{recData?.low || 0}</div>
          <div className="metric-rail-subtext">Minor resource tuning</div>
        </div>
      </div>

      {/* Highlights */}
      <div className="grid-2col-equal">
        <div style={{ backgroundColor: 'var(--bg-dark-panel)', border: '1px solid var(--border-dark)', borderRadius: '10px', padding: '20px 24px' }}>
          <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--accent-lime)', textTransform: 'uppercase', marginBottom: '4px' }}>
            TOP COST DRIVER
          </div>
          <h4 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-cream)', marginBottom: '4px' }}>
            {topDriver?.service} (+{formatCurrency(topDriver?.cost_change)})
          </h4>
          <p style={{ fontSize: '13px', color: 'var(--text-muted-dark)', lineHeight: 1.4 }}>
            Accounts for {topDriver?.contribution_percentage}% of recent 30-day spending growth. Prioritize configuration check for this service.
          </p>
        </div>

        <div style={{ backgroundColor: 'var(--bg-dark-panel)', border: '1px solid var(--border-dark)', borderRadius: '10px', padding: '20px 24px' }}>
          <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#63D6A2', textTransform: 'uppercase', marginBottom: '4px' }}>
            TOP OPTIMIZATION OPPORTUNITY
          </div>
          <h4 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-cream)', marginBottom: '4px' }}>
            {topOpportunity?.title}
          </h4>
          <p style={{ fontSize: '13px', color: 'var(--text-muted-dark)', lineHeight: 1.4 }}>
            {topOpportunity?.evidence}
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="dark-panel" style={{ padding: '14px 22px', marginTop: '24px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Filter size={16} color="var(--accent-lime)" />
          <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-cream)' }}>FILTER PRIORITY:</span>
          {['All', 'Critical', 'High', 'Medium', 'Low'].map((p) => (
            <button
              key={p}
              className={`btn ${priorityFilter === p ? 'btn-primary' : ''}`}
              onClick={() => setPriorityFilter(p)}
              style={{ padding: '4px 12px', fontSize: '12px' }}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <EmptyState message="No recommendations match the selected priority filter." />
      ) : (
        <div className="dark-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Priority</th>
                <th>Category</th>
                <th>Service</th>
                <th>Provider</th>
                <th>Region</th>
                <th>Observed Telemetry Reason</th>
                <th>Recommended Action Plan</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item, idx) => (
                <tr key={idx}>
                  <td><RiskBadge level={item.priority} /></td>
                  <td style={{ fontWeight: 700, color: 'var(--text-cream)' }}>{item.category}</td>
                  <td style={{ fontWeight: 700, color: 'var(--accent-lime)' }}>{item.service}</td>
                  <td>{item.provider}</td>
                  <td>{item.region}</td>
                  <td style={{ fontSize: '12.5px', color: 'var(--text-muted-dark)', maxWidth: '280px', whiteSpace: 'normal' }}>
                    {item.reason}
                  </td>
                  <td style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--text-cream)', maxWidth: '340px', whiteSpace: 'normal' }}>
                    {item.action}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
