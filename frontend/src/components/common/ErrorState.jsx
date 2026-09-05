import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const ErrorState = ({ message = "Unable to connect to the Cloud Cost API.", onRetry }) => {
  return (
    <div style={{ padding: '40px 24px', textAlign: 'center', backgroundColor: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: '8px', margin: '20px 0' }}>
      <AlertCircle size={36} color="#DC2626" style={{ margin: '0 auto 12px auto' }} />
      <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#991B1B', marginBottom: '4px' }}>
        Service Connection Error
      </h3>
      <p style={{ fontSize: '13px', color: '#B91C1C', marginBottom: '16px' }}>
        {message}
      </p>
      {onRetry && (
        <button className="btn btn-primary" onClick={onRetry}>
          <RefreshCw size={14} />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};
