import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { ForecastChart } from '../components/charts/ForecastChart';
import { formatCurrency, formatPercentage } from '../utils/formatters';

export const Forecast = ({ activeMeta }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [forecastSummary, setForecastSummary] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [dailyTrend, setDailyTrend] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [serviceForecasts, setServiceForecasts] = useState(null);
  const [horizonDays, setHorizonDays] = useState(30);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [fSummary, fData, dTrend, fEval, sForecast] = await Promise.all([
        api.getForecastSummary(),
        api.getForecast(horizonDays),
        api.getDailyTrend(),
        api.getForecastEvaluation(),
        api.getServiceForecasts(),
      ]);

      setForecastSummary(fSummary);
      setForecastData(fData);
      setDailyTrend(dTrend);
      setEvaluation(fEval);
      setServiceForecasts(sForecast);
    } catch (err) {
      setError(err.message || 'Failed to load cloud cost forecast.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeMeta, horizonDays]);

  if (loading) return <LoadingState message="Calculating Holt Exponential Smoothing time-series predictions..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="content-wrapper">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">COST FORECAST</h1>
          <p className="page-subtitle">30-Day Cost Outlook & backtesting holdout evaluation workspace.</p>
        </div>

        {/* Horizon Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: '#171717', padding: '6px', borderRadius: '8px', border: '1px solid var(--border-dark)' }}>
          <button
            className={`btn btn-sm ${horizonDays === 7 ? 'btn-primary' : ''}`}
            onClick={() => setHorizonDays(7)}
          >
            7 DAYS
          </button>
          <button
            className={`btn btn-sm ${horizonDays === 30 ? 'btn-primary' : ''}`}
            onClick={() => setHorizonDays(30)}
          >
            30 DAYS
          </button>
        </div>
      </div>

      {/* Split Layout: LEFT Chart, RIGHT Forecast Summary Box */}
      <div className="grid-2col" style={{ marginBottom: '24px' }}>
        {/* LEFT: Large Forecast Chart */}
        <div className="dark-panel" style={{ marginBottom: 0 }}>
          <div className="dark-panel-header">
            <div>
              <h3 className="dark-panel-title">30-DAY COST OUTLOOK</h3>
              <p className="dark-panel-subtitle">Historical spend transition into predicted horizon</p>
            </div>
          </div>
          <ForecastChart 
            historicalData={dailyTrend?.trend || []} 
            forecastData={forecastData?.forecast || []} 
          />
        </div>

        {/* RIGHT: Forecast Summary Sidebar */}
        <div className="dark-panel" style={{ marginBottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div className="dark-panel-header" style={{ marginBottom: '14px' }}>
              <h3 className="dark-panel-title">FORECAST SUMMARY</h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ backgroundColor: '#232323', padding: '14px 16px', borderRadius: '8px', border: '1px solid #333333' }}>
                <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--text-muted-dark)', textTransform: 'uppercase' }}>PROJECTED SPEND</div>
                <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--accent-lime)', fontFamily: 'JetBrains Mono', marginTop: '2px' }}>
                  {formatCurrency(forecastSummary?.predicted_next_30_day_spend)}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-cream)', marginTop: '2px' }}>
                  Avg: {formatCurrency(forecastData?.average_daily_forecast)}/day
                </div>
              </div>

              <div style={{ backgroundColor: '#232323', padding: '14px 16px', borderRadius: '8px', border: '1px solid #333333' }}>
                <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--text-muted-dark)', textTransform: 'uppercase' }}>TREND & CHANGE</div>
                <div style={{ fontSize: '20px', fontWeight: 700, color: forecastSummary?.spending_trend === 'increasing' ? '#F5B942' : 'var(--accent-lime)', marginTop: '2px' }}>
                  {forecastSummary?.spending_trend?.toUpperCase() ?? 'STABLE'}
                </div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: (forecastSummary?.percentage_change || 0) > 0 ? '#FF6B5C' : '#63D6A2', fontFamily: 'JetBrains Mono', marginTop: '2px' }}>
                  {formatPercentage(forecastSummary?.percentage_change)} shift
                </div>
              </div>

              <div style={{ backgroundColor: '#232323', padding: '14px 16px', borderRadius: '8px', border: '1px solid #333333' }}>
                <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--text-muted-dark)', textTransform: 'uppercase', marginBottom: '8px' }}>BACKTEST ACCURACY METRICS</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', textAlign: 'center' }}>
                  <div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted-dark)' }}>MAE</div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-cream)', fontFamily: 'JetBrains Mono' }}>{formatCurrency(evaluation?.mae)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted-dark)' }}>RMSE</div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-cream)', fontFamily: 'JetBrains Mono' }}>{formatCurrency(evaluation?.rmse)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted-dark)' }}>MAPE</div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent-lime)', fontFamily: 'JetBrains Mono' }}>{evaluation?.mape}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: '16px', backgroundColor: '#232323', border: '1px solid #333333', borderRadius: '8px', padding: '12px 14px' }}>
            <p style={{ fontSize: '12px', color: 'var(--text-muted-dark)', lineHeight: 1.4 }}>
              {forecastSummary?.explanation}
            </p>
          </div>
        </div>
      </div>

      {/* Service-Level Projections */}
      <div className="dark-panel">
        <div className="dark-panel-header">
          <div>
            <h3 className="dark-panel-title">SERVICE-LEVEL 30-DAY PROJECTIONS</h3>
            <p className="dark-panel-subtitle">Forecasted spend per cloud service</p>
          </div>
        </div>
        <div className="dark-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Service</th>
                <th>Status</th>
                <th>30-Day Forecast</th>
                <th>Trend %</th>
              </tr>
            </thead>
            <tbody>
              {serviceForecasts?.services?.map((svc, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 700, color: 'var(--accent-lime)' }}>{svc.service}</td>
                  <td>
                    <span className={`badge ${svc.status === 'available' ? 'badge-medium' : 'badge-low'}`}>
                      {svc.status}
                    </span>
                  </td>
                  <td className="mono-val" style={{ fontWeight: 700 }}>
                    {svc.status === 'available' ? formatCurrency(svc.predicted_30_day_spend) : 'N/A'}
                  </td>
                  <td className="mono-val" style={{ fontWeight: 700, color: (svc.trend_percentage || 0) > 0 ? '#FF6B5C' : '#63D6A2' }}>
                    {svc.status === 'available' ? formatPercentage(svc.trend_percentage) : 'N/A'}
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
