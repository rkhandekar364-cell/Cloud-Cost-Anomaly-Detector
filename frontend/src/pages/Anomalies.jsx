import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';
import { RiskBadge } from '../components/common/RiskBadge';
import { AnomalyDrawer } from '../components/common/AnomalyDrawer';
import { formatCurrency } from '../utils/formatters';
import { Filter } from 'lucide-react';

export const Anomalies = ({ initialSelectedId, onClearInitialSelected, activeMeta }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [anomaliesData, setAnomaliesData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);

  const [riskFilter, setRiskFilter] = useState('All');
  const [serviceFilter, setServiceFilter] = useState('All');
  const [providerFilter, setProviderFilter] = useState('All');
  const [sortBy, setSortBy] = useState('score');

  const [selectedAnomalyIndex, setSelectedAnomalyIndex] = useState(initialSelectedId ?? null);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [res, summary] = await Promise.all([
        api.getAnomalies(0.03),
        api.getAnomaliesSummary(0.03)
      ]);
      setAnomaliesData(res);
      setSummaryData(summary);
    } catch (err) {
      setError(err.message || 'Failed to load cost anomalies.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeMeta]);

  useEffect(() => {
    if (initialSelectedId !== null && initialSelectedId !== undefined) {
      handleOpenAnalysis(initialSelectedId);
    }
  }, [initialSelectedId]);

  const handleOpenAnalysis = async (index) => {
    setSelectedAnomalyIndex(index);
    setDrawerLoading(true);
    try {
      const res = await api.getAnomalyAnalysis(index);
      setAnalysisData(res);
    } catch (err) {
      console.error('Failed to fetch anomaly analysis:', err);
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleCloseDrawer = () => {
    setSelectedAnomalyIndex(null);
    setAnalysisData(null);
    if (onClearInitialSelected) onClearInitialSelected();
  };

  if (loading) return <LoadingState message="Running IsolationForest anomaly detection matrix..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const anomalies = anomaliesData?.anomalies || [];

  // SAFELY extract counts without undefined bugs!
  const totalCount = summaryData?.total_anomalies ?? anomaliesData?.total_anomalies ?? 0;
  const criticalCount = summaryData?.anomalies_by_risk_level?.Critical 
    ?? anomaliesData?.critical_anomalies 
    ?? 0;
  const highCount = summaryData?.anomalies_by_risk_level?.High 
    ?? anomaliesData?.high_risk_anomalies 
    ?? 0;
  const mediumCount = summaryData?.anomalies_by_risk_level?.Medium 
    ?? anomaliesData?.medium_risk_anomalies 
    ?? 0;
  const lowCount = summaryData?.anomalies_by_risk_level?.Low 
    ?? anomaliesData?.low_risk_anomalies 
    ?? 0;

  const servicesList = ['All', ...new Set(anomalies.map((a) => a.service))];
  const providersList = ['All', ...new Set(anomalies.map((a) => a.cloud_provider))];

  const filtered = anomalies.filter((a) => {
    if (riskFilter !== 'All' && a.risk_level !== riskFilter) return false;
    if (serviceFilter !== 'All' && a.service !== serviceFilter) return false;
    if (providerFilter !== 'All' && a.cloud_provider !== providerFilter) return false;
    return true;
  });

  filtered.sort((a, b) => {
    if (sortBy === 'score') return b.anomaly_score - a.anomaly_score;
    if (sortBy === 'cost') return b.actual_cost - a.actual_cost;
    if (sortBy === 'deviation') return b.deviation_percentage - a.deviation_percentage;
    if (sortBy === 'date') return b.date.localeCompare(a.date);
    return 0;
  });

  return (
    <div className="content-wrapper">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">ANOMALY MONITOR</h1>
          <p className="page-subtitle">IsolationForest telemetry monitoring & observability console.</p>
        </div>
      </div>

      {/* Top Metric Rail */}
      <div className="metric-rail">
        <div className="metric-rail-item">
          <div className="metric-rail-label">Total Anomalies</div>
          <div className="metric-rail-value">{totalCount}</div>
          <div className="metric-rail-subtext">
            <span>{anomaliesData?.anomaly_percentage ?? 0}% anomaly rate</span>
          </div>
        </div>

        <div className="metric-rail-item">
          <div className="metric-rail-label">Critical Risk</div>
          <div className="metric-rail-value" style={{ color: '#FF6B5C' }}>{criticalCount}</div>
          <div className="metric-rail-subtext">
            <span>≥200% surge above baseline</span>
          </div>
        </div>

        <div className="metric-rail-item">
          <div className="metric-rail-label">High Risk</div>
          <div className="metric-rail-value" style={{ color: '#F5B942' }}>{highCount}</div>
          <div className="metric-rail-subtext">
            <span>≥100% surge above baseline</span>
          </div>
        </div>

        <div className="metric-rail-item">
          <div className="metric-rail-label">Medium Risk</div>
          <div className="metric-rail-value" style={{ color: '#B7F34A' }}>{mediumCount}</div>
          <div className="metric-rail-subtext">
            <span>≥35% baseline deviation</span>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="dark-panel" style={{ padding: '16px 22px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 700, color: 'var(--accent-lime)' }}>
              <Filter size={16} />
              <span>FILTER MATRIX:</span>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-muted-dark)', marginRight: '6px' }}>Risk:</label>
              <select 
                value={riskFilter} 
                onChange={(e) => setRiskFilter(e.target.value)}
                style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-dark)', fontSize: '13px', backgroundColor: '#232323', color: '#F4F1E8', fontFamily: 'Space Grotesk' }}
              >
                <option value="All">All Risk Levels</option>
                <option value="Critical">Critical ({criticalCount})</option>
                <option value="High">High ({highCount})</option>
                <option value="Medium">Medium ({mediumCount})</option>
                <option value="Low">Low ({lowCount})</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-muted-dark)', marginRight: '6px' }}>Service:</label>
              <select 
                value={serviceFilter} 
                onChange={(e) => setServiceFilter(e.target.value)}
                style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-dark)', fontSize: '13px', backgroundColor: '#232323', color: '#F4F1E8', fontFamily: 'Space Grotesk' }}
              >
                {servicesList.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-muted-dark)', marginRight: '6px' }}>Provider:</label>
              <select 
                value={providerFilter} 
                onChange={(e) => setProviderFilter(e.target.value)}
                style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-dark)', fontSize: '13px', backgroundColor: '#232323', color: '#F4F1E8', fontFamily: 'Space Grotesk' }}
              >
                {providersList.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted-dark)' }}>Sort By:</label>
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-dark)', fontSize: '13px', backgroundColor: '#232323', color: '#F4F1E8', fontFamily: 'Space Grotesk' }}
            >
              <option value="score">Anomaly Score (High to Low)</option>
              <option value="cost">Actual Cost (High to Low)</option>
              <option value="deviation">Deviation % (High to Low)</option>
              <option value="date">Date (Recent First)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Dark Table */}
      {filtered.length === 0 ? (
        <EmptyState message="No cost anomalies matching the selected filter criteria." />
      ) : (
        <div className="dark-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Date</th>
                <th>Service</th>
                <th>Provider</th>
                <th>Region</th>
                <th>Actual Cost</th>
                <th>Expected Baseline</th>
                <th>Deviation %</th>
                <th>ML Score</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item, idx) => (
                <tr key={idx} onClick={() => handleOpenAnalysis(idx)}>
                  <td><RiskBadge level={item.risk_level} /></td>
                  <td style={{ fontWeight: 600 }}>{item.date}</td>
                  <td style={{ fontWeight: 700, color: 'var(--accent-lime)' }}>{item.service}</td>
                  <td>{item.cloud_provider}</td>
                  <td>{item.region}</td>
                  <td className="mono-val" style={{ fontWeight: 700 }}>{formatCurrency(item.actual_cost)}</td>
                  <td className="mono-val" style={{ color: 'var(--text-muted-dark)' }}>{formatCurrency(item.expected_cost)}</td>
                  <td className="mono-val" style={{ color: '#FF6B5C', fontWeight: 700 }}>+{item.deviation_percentage}%</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '48px', height: '6px', backgroundColor: '#333333', borderRadius: '3px', overflow: 'hidden' }}>
                        <div 
                          style={{ 
                            width: `${item.anomaly_score}%`, 
                            height: '100%', 
                            backgroundColor: item.anomaly_score >= 80 ? '#FF6B5C' : '#F5B942' 
                          }} 
                        />
                      </div>
                      <span className="mono-val" style={{ fontSize: '12px', fontWeight: 700 }}>{item.anomaly_score}</span>
                    </div>
                  </td>
                  <td>
                    <button className="btn btn-sm">
                      INVESTIGATE
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Slide-Over Drawer */}
      <AnomalyDrawer 
        isOpen={selectedAnomalyIndex !== null}
        onClose={handleCloseDrawer}
        analysisData={analysisData}
        loading={drawerLoading}
      />
    </div>
  );
};
