import React from 'react';

export const RiskBadge = ({ level }) => {
  const normalized = (level || 'Low').toLowerCase();
  let badgeClass = 'badge-low';

  if (normalized === 'critical') badgeClass = 'badge-critical';
  else if (normalized === 'high') badgeClass = 'badge-high';
  else if (normalized === 'medium') badgeClass = 'badge-medium';

  return (
    <span className={`badge ${badgeClass}`}>
      {level || 'Low'}
    </span>
  );
};
