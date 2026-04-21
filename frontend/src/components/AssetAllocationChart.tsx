import React, { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface AssetAllocation {
  name: string;
  value: number;
  percentage: string;
}

interface AssetAllocationChartProps {
  data: AssetAllocation[];
  title?: string;
}

// Color palette for asset classes
const COLORS = [
  '#3B82F6', // Blue - Stocks
  '#10B981', // Green - Bonds
  '#F59E0B', // Amber - Real Estate
  '#8B5CF6', // Purple - Crypto
  '#EF4444', // Red - Cash
  '#06B6D4', // Cyan - Commodities
];

  interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{ payload: AssetAllocation }>;
  }

  const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-2 border border-gray-300 rounded shadow">
        <p className="font-semibold text-gray-800">{data.name}</p>
        <p className="text-sm text-gray-600">${data.value.toLocaleString()}</p>
        <p className="text-sm text-blue-600 font-semibold">{data.percentage}%</p>
      </div>
    );
  }
  return null;
};

export const AssetAllocationChart: React.FC<AssetAllocationChartProps> = ({
  data,
  title = 'Asset Allocation',
}) => {
  const totalValue = useMemo(
    () => data.reduce((sum, item) => sum + item.value, 0),
    [data]
  );

  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>

      {totalValue > 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name} ${percentage}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-gray-400">
          <p>No portfolio data available</p>
        </div>
      )}

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-xs text-gray-500 uppercase">Total Value</p>
          <p className="text-xl font-bold text-gray-800">
            ${totalValue.toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-xs text-gray-500 uppercase">Asset Classes</p>
          <p className="text-xl font-bold text-gray-800">{data.length}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-xs text-gray-500 uppercase">Largest Position</p>
          <p className="text-xl font-bold text-blue-600">
            {data.length > 0 && data[0].name}
          </p>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-xs text-gray-500 uppercase">Diversification</p>
          <p className="text-xl font-bold text-green-600">
            {data.length >= 3 ? 'Good' : 'Poor'}
          </p>
        </div>
      </div>
    </div>
  );
};
