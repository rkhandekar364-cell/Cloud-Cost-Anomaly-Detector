import React from 'react';
import { Info } from 'lucide-react';

export const EmptyState = ({ message = "No cost anomalies detected for the selected period." }) => {
  return (
    <div style={{ padding: '40px 24px', textAlign: 'center', backgroundColor: '#FFFFFF', border: '1px solid var(--border-color)', borderRadius: '8px', margin: '20px 0' }}>
      <Info size={32} color="var(--text-muted)" style={{ margin: '0 auto 8px auto' }} />
      <p style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: 500 }}>
        {message}
      </p>
    </div>
  );
};
