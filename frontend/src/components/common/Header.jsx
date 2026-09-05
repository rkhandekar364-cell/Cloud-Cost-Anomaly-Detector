import React, { useState } from 'react';
import { RefreshCw, Calendar, Database, Upload } from 'lucide-react';
import { DataSourceModal } from './DataSourceModal';

export const Header = ({ title, subtitle, onRefresh, isRefreshing, activeMeta, onDatasetChanged }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const isDemo = activeMeta?.source === 'demo';

  return (
    <header className="header">
      <div>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
          {title}
        </h1>
        {subtitle && (
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>
            {subtitle}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Active Data Source Button Control */}
        <button
          className="btn"
          onClick={() => setIsModalOpen(true)}
          style={{
            backgroundColor: isDemo ? '#F1F5F9' : '#F0FDF4',
            borderColor: isDemo ? 'var(--border-color)' : '#BBF7D0',
            color: isDemo ? 'var(--text-main)' : '#166534',
            fontWeight: 600,
            fontSize: '12px'
          }}
          title="Click to configure data source or upload billing export"
        >
          {isDemo ? <Database size={14} color="var(--primary-blue)" /> : <Upload size={14} color="#166534" />}
          <span>ACTIVE DATASET: {isDemo ? 'Demo Dataset' : activeMeta?.filename}</span>
          <span className="badge" style={{ backgroundColor: isDemo ? '#E2E8F0' : '#DCFCE7', color: isDemo ? '#475569' : '#15803D', fontSize: '10px', padding: '1px 6px' }}>
            {activeMeta?.data_quality_score ?? 100}% Quality
          </span>
        </button>

        <button 
          className="btn" 
          onClick={onRefresh} 
          disabled={isRefreshing}
          title="Refresh dashboard data"
        >
          <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
          <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      <DataSourceModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        activeMeta={activeMeta}
        onDatasetChanged={onDatasetChanged}
      />
    </header>
  );
};
