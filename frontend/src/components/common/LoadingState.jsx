import React from 'react';

export const LoadingState = ({ message = "Loading cloud analytics..." }) => {
  return (
    <div style={{ padding: '60px 20px', textAlign: 'center', backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid var(--border-color)', margin: '20px 0' }}>
      <div style={{ display: 'inline-block', width: '32px', height: '32px', border: '3px solid #E2E8F0', borderTopColor: 'var(--primary-blue)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      <p style={{ marginTop: '12px', fontSize: '14px', color: 'var(--text-muted)', fontWeight: 500 }}>
        {message}
      </p>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
