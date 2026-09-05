import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { formatCurrency } from '../../utils/formatters';

export const ServiceBarChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
          <XAxis 
            dataKey="service" 
            tick={{ fontSize: 11, fill: '#64748B' }} 
            tickLine={false}
            angle={-25}
            textAnchor="end"
          />
          <YAxis 
            tick={{ fontSize: 11, fill: '#64748B' }} 
            tickLine={false}
            tickFormatter={(val) => `$${val}`}
          />
          <Tooltip 
            formatter={(value, name, item) => [`${formatCurrency(value)} (${item.payload.percentage}%)`, 'Total Spend']}
            contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1E293B', color: '#FFFFFF', borderRadius: '6px', fontSize: '12px' }}
          />
          <Bar dataKey="total_cost" fill="#2563EB" radius={[4, 4, 0, 0]} barSize={36} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
