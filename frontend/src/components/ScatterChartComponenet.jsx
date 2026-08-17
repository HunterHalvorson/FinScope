import React from 'react'
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';

function ScatterChartComponenet({ matchingTickerData }) {

  const chartData = matchingTickerData[0].filings
    .slice()
    .sort((a, b) => new Date(a.filingDate) - new Date(b.filingDate))
    .map(f => ({
      date: f.filingDate,
      positive: f.sentiment.positive,
      negative: f.sentiment.negative,
      uncertainty: f.sentiment.uncertainty,
      netSentiment: f.netSentiment,
      forwardReturn30d: f.forwardReturn30d
    }));

  return (
    <div style={{ marginTop: 64, padding: '0 24px' }}>
      <div style={{ textAlign: 'center', marginBottom: 8 }}>
        <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>
          Sentiment vs. 30-Day Forward Return
        </h3>
        <p style={{ margin: '4px 0 0', fontSize: 13, color: '#666' }}>
          {matchingTickerData[0].ticker} — {chartData.length} filings
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="netSentiment"
            name="Net Sentiment"
            label={{ value: 'Net Sentiment', position: 'insideBottom', offset: -10 }}
            tickFormatter={(v) => v.toFixed(2)}
          />
          <YAxis
            type="number"
            dataKey="forwardReturn30d"
            name="30d Forward Return"
            label={{ value: '30d Forward Return', angle: -90, position: 'insideLeft' }}
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
          />
          <ZAxis range={[200, 200]} />
          <ReferenceLine x={0} stroke="#666" strokeDasharray="3 3" />
          <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            formatter={(value, name) =>
              name === 'forwardReturn30d' ? `${(value * 100).toFixed(1)}%` : value.toFixed(3)
            }
          />
          <Legend verticalAlign="top" />
          <Scatter name="Filings" data={chartData} fill="#f97316" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ScatterChartComponenet