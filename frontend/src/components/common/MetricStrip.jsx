import React from 'react';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

export const MetricStrip = ({ summary, anomaliesSummary, forecastSummary }) => {
  // Safely resolve anomaly counts without any undefined errors!
  const totalAnomalies = anomaliesSummary?.total_anomalies ?? 0;
  const criticalCount = anomaliesSummary?.anomalies_by_risk_level?.Critical 
    ?? anomaliesSummary?.critical_anomalies 
    ?? 0;
  const highCount = anomaliesSummary?.anomalies_by_risk_level?.High 
    ?? anomaliesSummary?.high_risk_anomalies 
    ?? 0;

  return (
    <div className="metric-rail">
      {/* 1. TOTAL SPEND */}
      <div className="metric-rail-item">
        <div className="metric-rail-label">Total Spend</div>
        <div className="metric-rail-value">{formatCurrency(summary?.total_cloud_spend)}</div>
        <div className="metric-rail-subtext">
          <span style={{ color: '#B7F34A', fontWeight: 700 }}>{summary?.total_records ?? 0}</span>
          <span>billing records</span>
        </div>
      </div>

      {/* 2. DAILY BURN */}
      <div className="metric-rail-item">
        <div className="metric-rail-label">Daily Burn</div>
        <div className="metric-rail-value">
          {formatCurrency(summary?.average_daily_spend)}
          <span style={{ fontSize: '15px', fontWeight: 500, color: 'var(--text-muted-dark)' }}>/day</span>
        </div>
        <div className="metric-rail-subtext">
          <span>{summary?.number_of_services ?? 0} services across {summary?.number_of_cloud_providers ?? 0} providers</span>
        </div>
      </div>

      {/* 3. ANOMALIES */}
      <div className="metric-rail-item">
        <div className="metric-rail-label">Anomalies Detected</div>
        <div className="metric-rail-value" style={{ color: totalAnomalies > 0 ? '#FF6B5C' : 'var(--accent-lime)' }}>
          {totalAnomalies}
        </div>
        <div className="metric-rail-subtext">
          <span style={{ color: '#FF6B5C', fontWeight: 700 }}>{criticalCount} Critical</span>
          <span>, </span>
          <span style={{ color: '#F5B942', fontWeight: 700 }}>{highCount} High Risk</span>
        </div>
      </div>

      {/* 4. 30-DAY OUTLOOK */}
      <div className="metric-rail-item">
        <div className="metric-rail-label">30-Day Outlook</div>
        <div className="metric-rail-value" style={{ color: '#F5B942' }}>
          {formatCurrency(forecastSummary?.predicted_next_30_day_spend)}
        </div>
        <div className="metric-rail-subtext">
          <span>Trend: </span>
          <span style={{ fontWeight: 700, color: forecastSummary?.percentage_change > 0 ? '#FF6B5C' : '#63D6A2' }}>
            {forecastSummary?.spending_trend?.toUpperCase() ?? 'STABLE'} ({formatPercentage(forecastSummary?.percentage_change)})
          </span>
        </div>
      </div>
    </div>
  );
};
