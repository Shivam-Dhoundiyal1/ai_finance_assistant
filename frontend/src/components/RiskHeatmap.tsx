import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface RiskMetric {
  category: string;
  volatility: number;
  expectedReturn: number;
  riskScore: number; // 0-100
}

interface RiskHeatmapProps {
  data: RiskMetric[];
  title?: string;
}

const getRiskColor = (score: number): string => {
  if (score < 20) return '#10B981'; // Green - Low risk
  if (score < 40) return '#84CC16'; // Lime - Low-Moderate
  if (score < 60) return '#F59E0B'; // Amber - Moderate
  if (score < 80) return '#F97316'; // Orange - Moderate-High
  return '#EF4444'; // Red - High risk
};

  interface CustomTooltipProps {
    active?: boolean;
    payload?: Array<{ payload: RiskMetric }>;
  }

  const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 border border-gray-300 rounded shadow">
        <p className="font-semibold text-gray-800">{data.category}</p>
        <p className="text-sm text-gray-600">Volatility: {(data.volatility * 100).toFixed(1)}%</p>
        <p className="text-sm text-gray-600">Expected Return: {(data.expectedReturn * 100).toFixed(1)}%</p>
        <p className="text-sm font-semibold" style={{ color: getRiskColor(data.riskScore) }}>
          Risk Score: {data.riskScore}/100
        </p>
      </div>
    );
  }
  return null;
};

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({
  data,
  title = 'Portfolio Risk Analysis',
}) => {
  const averageRisk = useMemo(
    () => Math.round(data.reduce((sum, item) => sum + item.riskScore, 0) / (data.length || 1)),
    [data]
  );

  const riskLevel = useMemo(() => {
    if (averageRisk < 30) return 'Low';
    if (averageRisk < 50) return 'Moderate';
    if (averageRisk < 70) return 'Moderately High';
    return 'High';
  }, [averageRisk]);

  const riskColor = getRiskColor(averageRisk);

  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>

      <div className="flex-1 flex flex-col">
        {/* Risk Level Summary */}
        <div className="mb-4 p-4 bg-gray-50 rounded-lg border-l-4" style={{ borderLeftColor: riskColor }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 uppercase tracking-wide">Portfolio Risk Level</p>
              <p className="text-2xl font-bold" style={{ color: riskColor }}>
                {riskLevel}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 uppercase">Risk Score</p>
              <p className="text-3xl font-bold" style={{ color: riskColor }}>
                {averageRisk}
              </p>
            </div>
          </div>
        </div>

        {/* Risk Chart */}
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="category" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 12 }} />
              <YAxis yAxisId="left" label={{ value: 'Risk Score', angle: -90, position: 'insideLeft' }} />
              <YAxis yAxisId="right" orientation="right" label={{ value: 'Return (%)', angle: 90, position: 'insideRight' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar yAxisId="left" dataKey="riskScore" fill="#8B5CF6" name="Risk Score" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getRiskColor(entry.riskScore)} />
                ))}
              </Bar>
              <Bar yAxisId="right" dataKey="expectedReturn" fill="#3B82F6" name="Expected Return (%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <p>No risk data available</p>
          </div>
        )}

        {/* Risk Metrics Table */}
        <div className="mt-6">
          <p className="text-sm font-semibold text-gray-700 mb-3">Individual Position Risk</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 font-semibold text-gray-700">Position</th>
                  <th className="text-right py-2 px-3 font-semibold text-gray-700">Volatility</th>
                  <th className="text-right py-2 px-3 font-semibold text-gray-700">Return</th>
                  <th className="text-right py-2 px-3 font-semibold text-gray-700">Risk</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3 text-gray-700">{item.category}</td>
                    <td className="text-right py-2 px-3 text-gray-600">{(item.volatility * 100).toFixed(1)}%</td>
                    <td className="text-right py-2 px-3 text-gray-600">{(item.expectedReturn * 100).toFixed(1)}%</td>
                    <td className="text-right py-2 px-3 font-semibold" style={{ color: getRiskColor(item.riskScore) }}>
                      {item.riskScore}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
