
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts'

function LineChartComponent({matchingTickerData, ticker}) {

  const chartData = matchingTickerData
    .slice()
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .map(f => (
      {
        date: f.date,
        positive: f.positive,
        negative: f.negative,
        uncertainty: f.uncertainty,
        netSentiment: f.netSentiment
      }
    ));

  return (
    <div style={{ marginTop: 24, padding: '0 24px' }}>
      <div style={{ textAlign: 'center', marginBottom: 8 }}>
        <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>
          Sentiment Over Time
        </h3>
        <p style={{ margin: '4px 0 0', fontSize: 13, color: '#666' }}>
          {ticker} — {chartData.length} filings
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 10, right: 30, bottom: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3"/>
          <XAxis dataKey="date"/>
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="positive" stroke="#22c55e" strokeWidth={2} />
          <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} />
          <Line type="monotone" dataKey="uncertainty" stroke="#f59e0b" strokeWidth={2} />
          <Line type="monotone" dataKey="netSentiment" stroke="#3b82f6" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default LineChartComponent