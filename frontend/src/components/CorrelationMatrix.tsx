import React, { useMemo } from 'react';

interface CorrelationData {
  assets: string[];
  matrix: number[][]; // 2D array of correlation coefficients (-1 to 1)
}

interface CorrelationMatrixProps {
  data: CorrelationData;
  title?: string;
}

const getCorrelationColor = (value: number): string => {
  // Negative correlation (diversification benefit) - Green
  if (value < -0.5) return '#10B981';
  if (value < -0.2) return '#84CC16';
  // Neutral/Weak positive - Yellow/Amber
  if (value < 0.3) return '#F59E0B';
  if (value < 0.6) return '#F97316';
  // Strong positive correlation - Red
  return '#EF4444';
};

// const getCorrelationInterpretation = (value: number): string => {
//   if (value < 0) return 'Inverse';
//   if (value < 0.3) return 'Low';
//   if (value < 0.7) return 'Moderate';
//   return 'High';
// };

export const CorrelationMatrix: React.FC<CorrelationMatrixProps> = ({
  data,
  title = 'Asset Correlation Matrix',
}) => {
  const cellSize = 60;
  // const maxValue = Math.max(...data.assets.map((_, i) => Math.max(...data.matrix[i])));

  const diversificationScore = useMemo(() => {
    // Calculate average correlation (lower is better for diversification)
    let sum = 0;
    let count = 0;
    for (let i = 0; i < data.matrix.length; i++) {
      for (let j = i + 1; j < data.matrix[i].length; j++) {
        sum += data.matrix[i][j];
        count++;
      }
    }
    const avgCorrelation = count > 0 ? sum / count : 0;
    // Convert to diversification score (0-100, higher is better)
    return Math.max(0, Math.round((1 - avgCorrelation) * 50));
  }, [data.matrix]);

  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>

      <div className="flex-1 flex flex-col">
        {/* Diversification Score */}
        <div className="mb-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 uppercase tracking-wide">Diversification Quality</p>
              <p className="text-2xl font-bold text-blue-600">{diversificationScore > 50 ? 'Good' : 'Fair'}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 uppercase">Score</p>
              <p className="text-3xl font-bold text-blue-600">{diversificationScore}/100</p>
            </div>
          </div>
        </div>

        {/* Correlation Matrix */}
        {data.assets.length > 0 ? (
          <div className="overflow-x-auto flex-1">
            <div className="inline-block">
              {/* Header row */}
              <div className="flex">
                <div style={{ width: cellSize, height: cellSize }} className="bg-gray-100 border border-gray-300" />
                {data.assets.map((asset, idx) => (
                  <div
                    key={`header-${idx}`}
                    style={{ width: cellSize, height: cellSize }}
                    className="bg-gray-100 border border-gray-300 flex items-center justify-center"
                  >
                    <p className="text-xs font-semibold text-gray-700 text-center px-1">{asset}</p>
                  </div>
                ))}
              </div>

              {/* Data rows */}
              {data.matrix.map((row, i) => (
                <div key={`row-${i}`} className="flex">
                  <div
                    style={{ width: cellSize, height: cellSize }}
                    className="bg-gray-100 border border-gray-300 flex items-center justify-center"
                  >
                    <p className="text-xs font-semibold text-gray-700 text-center px-1">{data.assets[i]}</p>
                  </div>
                  {row.map((value, j) => (
                    <div
                      key={`cell-${i}-${j}`}
                      style={{
                        width: cellSize,
                        height: cellSize,
                        backgroundColor:
                          i === j
                            ? '#f0f0f0'
                            : `${getCorrelationColor(value)}20`,
                        borderColor: i === j ? '#d1d5db' : getCorrelationColor(value),
                      }}
                      className="border flex items-center justify-center cursor-help hover:opacity-80 transition"
                      title={`${data.assets[i]} ↔ ${data.assets[j]}: ${value.toFixed(2)}`}
                    >
                      <div className="text-center">
                        <p className="text-lg font-bold" style={{ color: getCorrelationColor(value) }}>
                          {value.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <p>No correlation data available</p>
          </div>
        )}

        {/* Legend */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 rounded border border-gray-200 bg-green-50">
            <p className="text-xs text-gray-600 uppercase">Inverse (-1.0 to -0.5)</p>
            <p className="text-sm font-semibold text-green-600">Best Diversification</p>
          </div>
          <div className="p-3 rounded border border-gray-200 bg-yellow-50">
            <p className="text-xs text-gray-600 uppercase">Low (-0.5 to 0.3)</p>
            <p className="text-sm font-semibold text-amber-600">Good Diversification</p>
          </div>
          <div className="p-3 rounded border border-gray-200 bg-orange-50">
            <p className="text-xs text-gray-600 uppercase">Moderate (0.3 to 0.6)</p>
            <p className="text-sm font-semibold text-orange-600">Fair Diversification</p>
          </div>
          <div className="p-3 rounded border border-gray-200 bg-red-50">
            <p className="text-xs text-gray-600 uppercase">High (0.6 to 1.0)</p>
            <p className="text-sm font-semibold text-red-600">Poor Diversification</p>
          </div>
        </div>

        {/* Insights */}
        <div className="mt-4 p-4 bg-blue-50 rounded border-l-4 border-blue-300">
          <p className="text-sm font-semibold text-gray-800 mb-2">💡 Diversification Insights</p>
          <ul className="text-sm text-gray-700 space-y-1">
            <li>• Negative correlations provide the most protection during market downturns</li>
            <li>• High correlations (above 0.7) suggest redundancy in your portfolio</li>
            <li>• Aim for an average correlation below 0.3 for good diversification</li>
            <li>• Consider adding uncorrelated assets (bonds, real estate, commodities)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
