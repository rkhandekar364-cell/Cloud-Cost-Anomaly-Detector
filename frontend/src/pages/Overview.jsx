import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MetricStrip } from '../components/common/MetricStrip';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { CostTrendChart } from '../components/charts/CostTrendChart';
import { ServiceCostMap } from '../components/charts/ServiceCostMap';
import { ProviderBarComparison } from '../components/charts/ProviderBarComparison';
import { AnomalyPulse } from '../components/charts/AnomalyPulse';
import { ActionCenter } from '../components/common/ActionCenter';
import { TopCostDrivers } from '../components/common/TopCostDrivers';
import { AnomalyDrawer } from '../components/common/AnomalyDrawer';

export const Overview = ({ onNavigateToAnomalies, onSelectAnomaly, activeMeta, onDatasetChanged }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    summary: null,
    dailyTrend: null,
    providerBreakdown: null,
    serviceBreakdown: null,
    anomaliesSummary: null,
    topAnomalies: null,
    forecastSummary: null,
    recommendations: null,
    drivers: null,
  });

  const [selectedAnomalyIndex, setSelectedAnomalyIndex] = useState(null);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        summary,
        dailyTrend,
        providerBreakdown,
        serviceBreakdown,
        anomaliesSummary,
        topAnomalies,
        forecastSummary,
        recommendations,
        drivers,
      ] = await Promise.all([
        api.getSummary(),
        api.getDailyTrend(),
        api.getProviderBreakdown(),
        api.getServiceBreakdown(),
        api.getAnomaliesSummary(),
        api.getTopAnomalies(5),
        api.getForecastSummary(),
        api.getRecommendations(),
        api.getCostDrivers(),
      ]);

      setData({
        summary,
        dailyTrend,
        providerBreakdown,
        serviceBreakdown,
        anomaliesSummary,
        topAnomalies,
        forecastSummary,
        recommendations,
        drivers,
      });
    } catch (err) {
      setError(err.message || 'Unable to connect to Cloud Cost API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeMeta]);

  const handleInspectAnomaly = async (index) => {
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

  if (loading) return <LoadingState message="Connecting to FinOps Control Room telemetry..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const { summary, dailyTrend, providerBreakdown, serviceBreakdown, anomaliesSummary, topAnomalies, forecastSummary, recommendations, drivers } = data;

  return (
    <div className="content-wrapper">
      {/* Editorial Hero Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">COST<br />COMMAND CENTER</h1>
          <p className="page-subtitle">See where cloud spending moves, why it moves, and what needs attention.</p>
        </div>

        {/* Small Technical Metadata Tags */}
        <div style={{ display: 'flex', gap: '12px', fontSize: '11.5px', fontFamily: 'JetBrains Mono', color: 'var(--text-muted-light)' }}>
          <div style={{ backgroundColor: 'var(--bg-app-subtle)', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-light)' }}>
            DATASET: <strong>SEP 2025 — AUG 2026</strong>
          </div>
          <div style={{ backgroundColor: 'var(--bg-app-subtle)', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-light)', color: '#171717' }}>
            STATUS: <strong style={{ color: '#059669' }}>● ONLINE</strong>
          </div>
        </div>
      </div>

      {/* Horizontal Dark Metric Rail */}
      <MetricStrip 
        summary={summary}
        anomaliesSummary={anomaliesSummary}
        forecastSummary={forecastSummary}
      />

      {/* Grid Row 1: Spending Activity Line Chart & Anomaly Pulse Matrix */}
      <div className="grid-2col">
        <div className="dark-panel" style={{ marginBottom: 0 }}>
          <div className="dark-panel-header">
            <div>
              <h3 className="dark-panel-title">SPENDING ACTIVITY</h3>
              <p className="dark-panel-subtitle">Daily expenditure time-series telemetry</p>
            </div>
          </div>
          <CostTrendChart data={dailyTrend?.trend || []} />
        </div>

        <div className="dark-panel" style={{ marginBottom: 0 }}>
          <div className="dark-panel-header">
            <div>
              <h3 className="dark-panel-title">ANOMALY PULSE</h3>
              <p className="dark-panel-subtitle">Real-time risk severity timeline</p>
            </div>
          </div>
          <AnomalyPulse 
            anomalies={topAnomalies?.top_anomalies || []}
            onSelectAnomaly={handleInspectAnomaly}
          />
        </div>
      </div>

      {/* Grid Row 2: Service Cost Map & Cloud Provider Comparison */}
      <div className="grid-2col-equal">
        <div className="dark-panel" style={{ marginBottom: 0 }}>
          <div className="dark-panel-header">
            <div>
              <h3 className="dark-panel-title">SERVICE COST MAP</h3>
              <p className="dark-panel-subtitle">Proportional spending distribution across cloud infrastructure</p>
            </div>
          </div>
          <ServiceCostMap data={serviceBreakdown?.breakdown || []} />
        </div>

        <div className="dark-panel" style={{ marginBottom: 0 }}>
          <div className="dark-panel-header">
            <div>
              <h3 className="dark-panel-title">PROVIDER COMPARISON</h3>
              <p className="dark-panel-subtitle">Provider capacity & spending allocation</p>
            </div>
          </div>
          <ProviderBarComparison data={providerBreakdown?.breakdown || []} />
        </div>
      </div>

      {/* Grid Row 3: Action Center & Top Cost Drivers */}
      <div className="grid-2col-equal" style={{ marginTop: '24px' }}>
        <ActionCenter 
          recommendations={recommendations?.recommendations || []}
          onNavigateToRecommendations={onNavigateToAnomalies}
        />

        <TopCostDrivers 
          drivers={drivers?.drivers || []}
        />
      </div>

      {/* Slide-Over Drawer for Quick Anomaly Inspection */}
      <AnomalyDrawer 
        isOpen={selectedAnomalyIndex !== null}
        onClose={() => {
          setSelectedAnomalyIndex(null);
          setAnalysisData(null);
        }}
        analysisData={analysisData}
        loading={drawerLoading}
      />
    </div>
  );
};
