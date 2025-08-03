import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MarketChart = ({ interval }) => {
  // Mock data for demonstration
  const mockData = [
    { time: '09:15', nifty: 19000, banknifty: 44000, sensex: 65000 },
    { time: '09:30', nifty: 19050, banknifty: 44100, sensex: 65100 },
    { time: '09:45', nifty: 19100, banknifty: 44200, sensex: 65200 },
    { time: '10:00', nifty: 19080, banknifty: 44050, sensex: 65150 },
    { time: '10:15', nifty: 19120, banknifty: 44300, sensex: 65300 },
    { time: '10:30', nifty: 19150, banknifty: 44400, sensex: 65400 },
    { time: '10:45', nifty: 19200, banknifty: 44500, sensex: 65500 },
    { time: '11:00', nifty: 19180, banknifty: 44450, sensex: 65450 },
    { time: '11:15', nifty: 19220, banknifty: 44600, sensex: 65600 },
    { time: '11:30', nifty: 19250, banknifty: 44700, sensex: 65700 },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-400 text-sm">{`Time: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {`${entry.name}: ${entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={mockData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            fontSize={12}
          />
          <YAxis 
            stroke="#9CA3AF"
            fontSize={12}
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="nifty" 
            stroke="#3B82F6" 
            strokeWidth={2}
            dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2 }}
          />
          <Line 
            type="monotone" 
            dataKey="banknifty" 
            stroke="#10B981" 
            strokeWidth={2}
            dot={{ fill: '#10B981', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#10B981', strokeWidth: 2 }}
          />
          <Line 
            type="monotone" 
            dataKey="sensex" 
            stroke="#F59E0B" 
            strokeWidth={2}
            dot={{ fill: '#F59E0B', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#F59E0B', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="flex justify-center space-x-6 mt-4">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
          <span className="text-sm text-gray-300">NIFTY</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-success-500 rounded-full"></div>
          <span className="text-sm text-gray-300">BANKNIFTY</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
          <span className="text-sm text-gray-300">SENSEX</span>
        </div>
      </div>
    </div>
  );
};

export default MarketChart; 