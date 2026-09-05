import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { formatCurrency } from '../../utils/formatters';

const PROVIDER_COLORS = {
  AWS: '#2563EB',
  Azure: '#0D9488',
  GCP: '#6366F1'
};

export const ProviderDonutChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="total_cost"
            nameKey="provider"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={95}
            paddingAngle={4}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={PROVIDER_COLORS[entry.provider] || '#94A3B8'} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value, name, item) => [
              `${formatCurrency(value)} (${item.payload.percentage}%)`, 
              item.payload.provider
            ]}
            contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1E293B', color: '#FFFFFF', borderRadius: '6px', fontSize: '12px' }}
          />
          <Legend 
            verticalAlign="bottom" 
            height={36} 
            formatter={(value) => <span style={{ fontSize: '12px', color: '#475569', fontWeight: 500 }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
