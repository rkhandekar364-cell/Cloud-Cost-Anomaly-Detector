import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Upload, CheckCircle2, AlertCircle, RefreshCw, Database, X } from 'lucide-react';

export const DataSourceModal = ({ isOpen, onClose, activeMeta, onDatasetChanged }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [activating, setActivating] = useState(false);

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isDemo = !activeMeta || activeMeta.source === 'demo';

  // Safely format date range object or string without throwing React child error!
  const formatDateRange = (dr) => {
    if (!dr) return '12 Months';
    if (typeof dr === 'string') return dr;
    if (typeof dr === 'object' && dr !== null) {
      if (dr.min_date && dr.max_date) {
        return `${dr.min_date} to ${dr.max_date}`;
      }
    }
    return '12 Months';
  };

  // Safely format provider count
  const getProviderCount = (p) => {
    if (typeof p === 'number') return p;
    if (Array.isArray(p)) return p.length;
    return 3;
  };

  // Safely format service count
  const getServiceCount = (s) => {
    if (typeof s === 'number') return s;
    if (Array.isArray(s)) return s.length;
    return 9;
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setPreviewData(null);

    try {
      const res = await api.uploadDataset(file);
      setPreviewData(res);
    } catch (err) {
      setUploadError(err.message || 'Failed to parse and normalize file.');
    } finally {
      setUploading(false);
    }
  };

  const handleActivate = async () => {
    if (!previewData) return;

    setActivating(true);
    try {
      await api.activateDataset(previewData.filename);
      onDatasetChanged();
      setPreviewData(null);
      onClose();
    } catch (err) {
      setUploadError(err.message || 'Failed to activate dataset.');
    } finally {
      setActivating(false);
    }
  };

  const handleRestoreDemo = async () => {
    setActivating(true);
    try {
      await api.restoreDemoDataset();
      onDatasetChanged();
      setPreviewData(null);
      onClose();
    } catch (err) {
      setUploadError(err.message || 'Failed to restore demo dataset.');
    } finally {
      setActivating(false);
    }
  };

  return (
    <>
      {/* Backdrop for click-outside close */}
      <div className="ds-panel-backdrop" onClick={onClose} />

      {/* Fixed Viewport Data Source Panel */}
      <div className="ds-panel" onClick={(e) => e.stopPropagation()}>
        {/* Panel Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #333333', paddingBottom: '14px', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={18} color="#B7F34A" />
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#F4F1E8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              DATA SOURCE
            </h3>
          </div>
          <button 
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', color: '#A39F93' }}
            title="Close panel (Esc)"
          >
            <X size={18} />
          </button>
        </div>

        {/* Section 1: Active Dataset Details */}
        <div style={{ backgroundColor: '#232323', border: '1px solid #333333', borderRadius: '8px', padding: '16px', marginBottom: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#A39F93', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              ACTIVE DATASET
            </span>
            <span 
              className="badge" 
              style={{ backgroundColor: '#B7F34A', color: '#171717', fontSize: '10px', padding: '1px 6px' }}
            >
              {activeMeta?.data_quality_score ?? 100}% QUALITY
            </span>
          </div>

          <div style={{ fontSize: '16px', fontWeight: 700, color: '#B7F34A', marginBottom: '10px', wordBreak: 'break-all' }}>
            {isDemo ? 'Demo Dataset' : (activeMeta?.filename ?? 'Uploaded Dataset')}
          </div>

          {/* Metadata Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '12px', fontFamily: 'JetBrains Mono', color: '#F4F1E8' }}>
            <div>
              <span style={{ color: '#A39F93' }}>Records:</span>{' '}
              <strong>{activeMeta?.record_count ?? 5466}</strong>
            </div>
            <div>
              <span style={{ color: '#A39F93' }}>Period:</span>{' '}
              <strong>{formatDateRange(activeMeta?.date_range)}</strong>
            </div>
            <div>
              <span style={{ color: '#A39F93' }}>Providers:</span>{' '}
              <strong>{getProviderCount(activeMeta?.providers)}</strong>
            </div>
            <div>
              <span style={{ color: '#A39F93' }}>Services:</span>{' '}
              <strong>{getServiceCount(activeMeta?.services)}</strong>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div style={{ borderBottom: '1px solid #333333', marginBottom: '18px' }} />

        {/* Section 2: Use Your Own Billing Data */}
        <div style={{ marginBottom: '18px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#F4F1E8', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '4px' }}>
            USE YOUR OWN BILLING DATA
          </div>
          <p style={{ fontSize: '12px', color: '#A39F93', marginBottom: '12px', lineHeight: 1.4 }}>
            Upload a cloud billing export file to analyze real spending.
          </p>

          <label 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justify: 'center', 
              gap: '8px',
              padding: '12px',
              border: '2px dashed #444444',
              borderRadius: '8px',
              backgroundColor: '#232323',
              cursor: 'pointer',
              color: '#F4F1E8',
              fontSize: '13px',
              fontWeight: 700,
              transition: 'all 0.15s ease'
            }}
          >
            <Upload size={16} color="#B7F34A" />
            <span>+ UPLOAD BILLING FILE</span>
            <input 
              type="file" 
              accept=".csv,.xlsx,.xls" 
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </label>
          <div style={{ fontSize: '11px', color: '#A39F93', textAlign: 'center', marginTop: '6px', fontFamily: 'JetBrains Mono' }}>
            CSV • XLS • XLSX
          </div>
        </div>

        {uploading && (
          <div style={{ padding: '12px', textAlign: 'center', fontSize: '12px', color: '#A39F93' }}>
            <RefreshCw size={16} className="spin" style={{ margin: '0 auto 4px auto' }} color="#B7F34A" />
            Parsing columns & calculating quality...
          </div>
        )}

        {uploadError && (
          <div style={{ backgroundColor: '#2A1A1A', border: '1px solid #FF6B5C', padding: '10px 12px', borderRadius: '6px', fontSize: '12px', color: '#FF6B5C', marginBottom: '14px' }}>
            <AlertCircle size={14} style={{ display: 'inline', marginRight: '6px' }} />
            {uploadError}
          </div>
        )}

        {/* Uploaded File Mapping Preview */}
        {previewData && (
          <div style={{ backgroundColor: '#222A1A', border: '1px solid #B7F34A', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '13px', fontWeight: 700, color: '#B7F34A' }}>
                Mapping Confidence ({previewData.total_records ?? previewData.records?.length ?? 0} rows)
              </span>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#B7F34A', fontFamily: 'JetBrains Mono' }}>
                Score: {previewData.data_quality?.data_quality_score ?? 100}%
              </span>
            </div>

            <div className="dark-table-container" style={{ maxHeight: '140px', overflowY: 'auto', marginBottom: '12px' }}>
              <table className="custom-table" style={{ fontSize: '12px' }}>
                <thead>
                  <tr>
                    <th>Canonical</th>
                    <th>Source</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {(previewData.mappings || []).map((m, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 700, color: '#B7F34A' }}>{m.canonical_field}</td>
                      <td><code>{m.source_column}</code></td>
                      <td className="mono-val">{((m.confidence || 0) * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <button 
              className="btn btn-primary" 
              onClick={handleActivate}
              disabled={activating}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              <CheckCircle2 size={16} />
              <span>{activating ? 'ACTIVATING...' : 'USE THIS DATASET'}</span>
            </button>
          </div>
        )}

        {/* Section 3: Restore Demo Dataset */}
        <div style={{ marginTop: '12px' }}>
          <button 
            className="btn" 
            onClick={handleRestoreDemo} 
            disabled={activating || isDemo}
            style={{ 
              width: '100%', 
              justify: 'center', 
              backgroundColor: isDemo ? '#1D1D1D' : '#232323',
              color: isDemo ? '#77746B' : '#F4F1E8',
              borderColor: '#333333'
            }}
          >
            <RefreshCw size={14} className={activating ? 'spin' : ''} color={isDemo ? '#77746B' : '#B7F34A'} />
            <span>{isDemo ? 'DEMO DATASET ACTIVE' : 'RESTORE DEMO DATASET'}</span>
          </button>
        </div>
      </div>
    </>
  );
};
