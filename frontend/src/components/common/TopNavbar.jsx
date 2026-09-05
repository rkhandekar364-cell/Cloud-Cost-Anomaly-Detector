import React, { useState } from 'react';
import { 
  Cloud, 
  BarChart3, 
  AlertTriangle, 
  TrendingUp, 
  PieChart, 
  Lightbulb, 
  Database, 
  Upload, 
  RefreshCw,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { DataSourceModal } from './DataSourceModal';
import { ErrorBoundary } from './ErrorBoundary';

export const TopNavbar = ({ 
  activeTab, 
  setActiveTab, 
  apiConnected, 
  activeMeta, 
  onDatasetChanged, 
  onRefresh, 
  isRefreshing 
}) => {
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
    { id: 'forecast', label: 'Forecast', icon: TrendingUp },
    { id: 'cost-analysis', label: 'Cost Analysis', icon: PieChart },
    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
  ];

  const isDemo = !activeMeta || activeMeta.source === 'demo';
  const displayFilename = isDemo ? 'Demo Dataset' : (activeMeta?.filename || 'Uploaded Dataset');

  return (
    <header className="top-nav">
      {/* Brand Logo & Title */}
      <div className="brand-container" onClick={() => setActiveTab('overview')}>
        <div className="brand-logo-icon">
          <Cloud size={20} color="#171717" />
        </div>
        <div className="brand-title">
          CLOUDCOST <span className="brand-accent">ANOMALY DETECTOR</span>
        </div>
      </div>

      {/* Navigation Pills */}
      <nav>
        <ul className="nav-links">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <li key={item.id}>
                <button
                  className={`nav-pill ${isActive ? 'active' : ''}`}
                  onClick={() => setActiveTab(item.id)}
                >
                  <Icon size={16} color={isActive ? '#B7F34A' : '#A39F93'} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Right Controls Cluster */}
      <div className="nav-right">
        {/* Compact Data Source Trigger Button */}
        <button
          className="btn btn-ds-trigger"
          onClick={() => setIsPanelOpen(!isPanelOpen)}
          style={{
            backgroundColor: isDemo ? '#232323' : '#1C2E1A',
            borderColor: isPanelOpen ? '#B7F34A' : (isDemo ? '#333333' : '#B7F34A'),
            color: isDemo ? '#F4F1E8' : '#B7F34A',
            fontWeight: 700,
            fontSize: '12px',
            maxWidth: '180px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}
          title={`Active Dataset: ${displayFilename} (${activeMeta?.data_quality_score ?? 100}% Quality)`}
        >
          {isDemo ? <Database size={14} color="#B7F34A" style={{ flexShrink: 0 }} /> : <Upload size={14} color="#B7F34A" style={{ flexShrink: 0 }} />}
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {displayFilename}
          </span>
          <span 
            className="badge" 
            style={{ 
              backgroundColor: '#B7F34A', 
              color: '#171717', 
              fontSize: '10px', 
              padding: '1px 5px',
              flexShrink: 0 
            }}
          >
            {activeMeta?.data_quality_score ?? 100}%
          </span>
        </button>

        {/* Refresh Action */}
        <button 
          className="btn" 
          onClick={onRefresh} 
          disabled={isRefreshing}
          title="Refresh dashboard data"
        >
          <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} color="#B7F34A" />
          <span>{isRefreshing ? 'REFRESHING...' : 'REFRESH'}</span>
        </button>

        {/* API Connection Indicator */}
        <div 
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px', 
            fontSize: '12px', 
            fontWeight: 700,
            color: apiConnected ? '#63D6A2' : '#FF6B5C',
            backgroundColor: '#232323',
            border: '1px solid #333333',
            padding: '5px 10px',
            borderRadius: '6px',
            textTransform: 'uppercase',
            flexShrink: 0
          }}
        >
          {apiConnected ? <CheckCircle2 size={13} color="#63D6A2" /> : <XCircle size={13} color="#FF6B5C" />}
          <span>{apiConnected ? '● ONLINE' : '● OFFLINE'}</span>
        </div>
      </div>

      {/* Data Source Panel wrapped in ErrorBoundary */}
      <ErrorBoundary>
        <DataSourceModal
          isOpen={isPanelOpen}
          onClose={() => setIsPanelOpen(false)}
          activeMeta={activeMeta}
          onDatasetChanged={onDatasetChanged}
        />
      </ErrorBoundary>
    </header>
  );
};
