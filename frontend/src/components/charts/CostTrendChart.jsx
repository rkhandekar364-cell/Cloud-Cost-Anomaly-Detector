import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { formatCurrency } from '../../utils/formatters';

export const CostTrendChart = ({ data = [] }) => {
  if (!data || data.length === 0) return null;

  return (
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 15, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2B2B2B" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 11, fill: '#A39F93', fontFamily: 'Space Grotesk' }} 
            tickLine={false}
            interval={Math.floor(data.length / 8)}
          />
          <YAxis 
            tick={{ fontSize: 11, fill: '#A39F93', fontFamily: 'JetBrains Mono' }} 
            tickLine={false}
            tickFormatter={(val) => `$${val}`}
          />
          <Tooltip 
            formatter={(value) => [formatCurrency(value), 'Spend']}
            labelFormatter={(label) => `Date: ${label}`}
            contentStyle={{ backgroundColor: '#171717', borderColor: '#333333', color: '#F4F1E8', borderRadius: '8px', fontSize: '12px', fontFamily: 'Space Grotesk' }}
            itemStyle={{ color: '#B7F34A', fontFamily: 'JetBrains Mono', fontWeight: 'bold' }}
          />
          <Line 
            type="monotone" 
            dataKey="total_cost" 
            stroke="#B7F34A" 
            strokeWidth={2.5} 
            dot={false}
            activeDot={{ r: 6, fill: '#B7F34A' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
