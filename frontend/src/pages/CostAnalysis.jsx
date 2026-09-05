import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { ServiceCostMap } from '../components/charts/ServiceCostMap';
import { ProviderBarComparison } from '../components/charts/ProviderBarComparison';
import { CostTrendChart } from '../components/charts/CostTrendChart';
import { formatCurrency } from '../utils/formatters';

export const CostAnalysis = ({ activeMeta }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [serviceData, setServiceData] = useState(null);
  const [providerData, setProviderData] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [driversData, setDriversData] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sData, pData, tData, dData] = await Promise.all([
        api.getServiceBreakdown(),
        api.getProviderBreakdown(),
        api.getDailyTrend(),
        api.getCostDrivers(),
      ]);

      setServiceData(sData);
      setProviderData(pData);
      setTrendData(tData);
      setDriversData(dData);
    } catch (err) {
      setError(err.message || 'Failed to load cost analysis.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeMeta]);

  if (loading) return <LoadingState message="Aggregating multi-dimensional cloud billing telemetry..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="content-wrapper">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">COST ANALYSIS</h1>
          <p className="page-subtitle">Data exploration workspace & cost driver analysis.</p>
        </div>
      </div>

      {/* Grid Row 1: Service Cost Map & Provider Comparison */}
      <div className="grid-2col-equal">
        <div className="dark-panel" style={{ marginBottom: 0 }}>
          <div className="dark-panel-header">
            <div>
              <h3 className="dark-panel-title">SERVICE COST MAP</h3>
              <p className="dark-panel-subtitle">Proportional cost breakdown by cloud service</p>
            </div>
          </div>
          <ServiceCostMap data={serviceData?.breakdown || []} />
        </div>

        <div className="dark-panel" style={{ marginBottom: 0 }}>
          <div className="dark-panel-header">
            <div>
              <h3 className="dark-panel-title">PROVIDER COMPARISON</h3>
              <p className="dark-panel-subtitle">Allocation across AWS, Azure, and GCP</p>
            </div>
          </div>
          <ProviderBarComparison data={providerData?.breakdown || []} />
        </div>
      </div>

      {/* Grid Row 2: Daily Spending Time Series */}
      <div className="dark-panel" style={{ marginTop: '24px' }}>
        <div className="dark-panel-header">
          <div>
            <h3 className="dark-panel-title">DAILY SPENDING TIME SERIES</h3>
            <p className="dark-panel-subtitle">Cumulative daily spending trend across all infrastructure</p>
          </div>
        </div>
        <CostTrendChart data={trendData?.trend || []} />
      </div>

      {/* Grid Row 3: Ranked Cost Drivers Table */}
      <div className="dark-panel">
        <div className="dark-panel-header">
          <div>
            <h3 className="dark-panel-title">RANKED COST DRIVERS ANALYSIS</h3>
            <p className="dark-panel-subtitle">Services contributing to recent 30-day spending shifts</p>
          </div>
        </div>
        <div className="dark-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Cloud Service</th>
                <th>Recent 30-Day Spend</th>
                <th>Previous 30-Day Spend</th>
                <th>Net Cost Change</th>
                <th>Contribution %</th>
              </tr>
            </thead>
            <tbody>
              {driversData?.drivers?.map((item) => (
                <tr key={item.rank}>
                  <td className="mono-val" style={{ fontWeight: 800, color: 'var(--accent-lime)' }}>#{item.rank}</td>
                  <td style={{ fontWeight: 700, color: 'var(--text-cream)' }}>{item.service}</td>
                  <td className="mono-val">{formatCurrency(item.recent_period_spend)}</td>
                  <td className="mono-val">{formatCurrency(item.previous_period_spend)}</td>
                  <td className="mono-val" style={{ fontWeight: 700, color: item.cost_change > 0 ? '#FF6B5C' : '#63D6A2' }}>
                    {item.cost_change > 0 ? '+' : ''}{formatCurrency(item.cost_change)}
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '80px', height: '6px', backgroundColor: '#333333', borderRadius: '3px', overflow: 'hidden' }}>
                        <div 
                          style={{ 
                            width: `${Math.min(100, item.contribution_percentage)}%`, 
                            height: '100%', 
                            backgroundColor: 'var(--accent-lime)' 
                          }} 
                        />
                      </div>
                      <span className="mono-val" style={{ fontWeight: 700 }}>{item.contribution_percentage}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
