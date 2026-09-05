import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, ReferenceLine } from 'recharts';
import { formatCurrency } from '../../utils/formatters';

export const ForecastChart = ({ historicalData = [], forecastData = [] }) => {
  const formattedHistorical = historicalData.map((d) => ({
    date: d.date,
    Historical: d.total_cost,
    Forecast: null,
  }));

  const lastHistorical = historicalData.length > 0 ? historicalData[historicalData.length - 1] : null;

  const formattedForecast = forecastData.map((d) => ({
    date: d.date,
    Historical: null,
    Forecast: d.predicted_cost,
  }));

  if (lastHistorical && formattedForecast.length > 0) {
    formattedForecast.unshift({
      date: lastHistorical.date,
      Historical: lastHistorical.total_cost,
      Forecast: lastHistorical.total_cost,
    });
  }

  const combinedData = [...formattedHistorical, ...formattedForecast.slice(1)];

  if (combinedData.length === 0) return null;

  const todayDate = lastHistorical ? lastHistorical.date : null;

  return (
    <div style={{ width: '100%', height: 360 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={combinedData} margin={{ top: 20, right: 20, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2B2B2B" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 11, fill: '#A39F93', fontFamily: 'Space Grotesk' }} 
            tickLine={false}
            interval={Math.floor(combinedData.length / 8)}
          />
          <YAxis 
            tick={{ fontSize: 11, fill: '#A39F93', fontFamily: 'JetBrains Mono' }} 
            tickLine={false}
            tickFormatter={(val) => `$${val}`}
          />
          <Tooltip 
            formatter={(value, name) => [formatCurrency(value), name === 'Historical' ? 'Historical Spend' : '30-Day Forecast']}
            contentStyle={{ backgroundColor: '#171717', borderColor: '#333333', color: '#F4F1E8', borderRadius: '8px', fontSize: '12px', fontFamily: 'Space Grotesk' }}
          />
          <Legend verticalAlign="top" height={36} wrapperStyle={{ fontFamily: 'Space Grotesk', fontSize: '12px', color: '#F4F1E8' }} />

          {/* Vertical Coral TODAY Reference Line */}
          {todayDate && (
            <ReferenceLine 
              x={todayDate} 
              stroke="#FF6B5C" 
              strokeWidth={2} 
              strokeDasharray="4 4"
              label={{ value: 'TODAY', fill: '#FF6B5C', fontSize: 11, fontWeight: 700, position: 'top', fontFamily: 'Space Grotesk' }} 
            />
          )}

          <Line 
            type="monotone" 
            dataKey="Historical" 
            stroke="#B7F34A" 
            strokeWidth={2.5} 
            dot={false}
            name="Historical Spend"
          />
          <Line 
            type="monotone" 
            dataKey="Forecast" 
            stroke="#F5B942" 
            strokeWidth={2.5} 
            strokeDasharray="5 5" 
            dot={false}
            name="30-Day Forecast"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
