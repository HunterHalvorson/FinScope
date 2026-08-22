import React, { useEffect, useState } from 'react'
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
} from 'recharts'

function ScatterChartComponent({ ticker }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resultsResponse = await fetch(`http://localhost:8000/analysis/event-study/${ticker}`)
        const resultData = await resultsResponse.json()
        setData(resultData)
        setLoading(false)
      } catch (err) {
        setError(err.message)
        setLoading(false)
      }
    }
    fetchData()
  }, [ticker])

  if (loading) return <div style={{ padding: '24px', textAlign: 'center', color: '#666' }}>Loading...</div>
  if (error) return <div style={{ padding: '24px', color: '#ef4444' }}>Error: {error}</div>
  if (!data || !data.data) return <div style={{ padding: '24px', color: '#999' }}>No data available</div>

  const headerStyle = {
    marginTop: 64,
    padding: '0 24px'
  }

  const titleStyle = {
    margin: 0,
    fontSize: 20,
    fontWeight: 700,
    color: '#1f2937',
    marginBottom: 24
  }

  const statsContainerStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 16,
    marginBottom: 32,
    padding: 20,
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    border: '1px solid #e5e7eb'
  }

  const statStyle = {
    textAlign: 'center'
  }

  const statLabelStyle = {
    fontSize: 12,
    color: '#6b7280',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  }

  const statValueStyle = {
    fontSize: 18,
    fontWeight: 700,
    marginTop: 4
  }

  const chartContainerStyle = {
    marginBottom: 40,
    padding: 20,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    border: '1px solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
  }

  const chartTitleStyle = {
    fontSize: 16,
    fontWeight: 600,
    marginBottom: 4,
    color: '#1f2937'
  }

  const chartSubtitleStyle = {
    fontSize: 13,
    color: '#6b7280',
    margin: 0
  }

  return (
    <div style={headerStyle}>
      <h1 style={titleStyle}>Event Study Analysis</h1>

      {/* Stats Cards */}
      <div style={statsContainerStyle}>
        <div style={statStyle}>
          <div style={statLabelStyle}>Filings Analyzed</div>
          <div style={{ ...statValueStyle, color: '#3b82f6' }}>{data.data.length}</div>
        </div>
        <div style={statStyle}>
          <div style={statLabelStyle}>MDA Correlation</div>
          <div style={{ ...statValueStyle, color: data.mdaCorr > 0 ? '#10b981' : '#ef4444' }}>
            {data.mdaCorr.toFixed(3)}
          </div>
        </div>
        <div style={statStyle}>
          <div style={statLabelStyle}>Risk Correlation</div>
          <div style={{ ...statValueStyle, color: data.riskCorr > 0 ? '#10b981' : '#ef4444' }}>
            {data.riskCorr.toFixed(3)}
          </div>
        </div>
      </div>

      {/* MDA Sentiment Chart */}
      <div style={chartContainerStyle}>
        <div style={chartTitleStyle}>📊 MDA Sentiment vs Forward Return</div>
        <p style={chartSubtitleStyle}>{ticker} — Management Discussion & Analysis tone predicting stock performance</p>
        <ResponsiveContainer width="100%" height={380}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              type="number"
              dataKey="mda_sentiment"
              name="MDA Sentiment"
              label={{ value: 'MDA Sentiment →', position: 'insideBottomRight', offset: -15 }}
              tickFormatter={(v) => v.toFixed(2)}
              stroke="#6b7280"
            />
            <YAxis
              type="number"
              dataKey="forward_return"
              name="Forward Return"
              label={{ value: '← Forward Return', angle: -90, position: 'insideLeftTop', offset: 10 }}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              stroke="#6b7280"
            />
            <ZAxis range={[100, 100]} />
            <ReferenceLine x={0} stroke="#d1d5db" strokeDasharray="3 3" />
            <ReferenceLine y={0} stroke="#d1d5db" strokeDasharray="3 3" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: 8,
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
              formatter={(value, name) =>
                name === 'forward_return' ? `${(value * 100).toFixed(2)}%` : value.toFixed(4)
              }
            />
            <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: 16 }} />
            <Scatter name="Filings" data={data.data} fill="#3b82f6" fillOpacity={0.7} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Risk Sentiment Chart */}
      <div style={chartContainerStyle}>
        <div style={chartTitleStyle}>⚠️ Risk Sentiment vs Forward Return</div>
        <p style={chartSubtitleStyle}>{ticker} — Risk factors language tone predicting stock performance</p>
        <ResponsiveContainer width="100%" height={380}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              type="number"
              dataKey="risk_sentiment"
              name="Risk Sentiment"
              label={{ value: 'Risk Sentiment →', position: 'insideBottomRight', offset: -15 }}
              tickFormatter={(v) => v.toFixed(2)}
              stroke="#6b7280"
            />
            <YAxis
              type="number"
              dataKey="forward_return"
              name="Forward Return"
              label={{ value: '← Forward Return', angle: -90, position: 'insideLeftTop', offset: 10 }}
              tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              stroke="#6b7280"
            />
            <ZAxis range={[100, 100]} />
            <ReferenceLine x={0} stroke="#d1d5db" strokeDasharray="3 3" />
            <ReferenceLine y={0} stroke="#d1d5db" strokeDasharray="3 3" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: 8,
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
              formatter={(value, name) =>
                name === 'forward_return' ? `${(value * 100).toFixed(2)}%` : value.toFixed(4)
              }
            />
            <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: 16 }} />
            <Scatter name="Filings" data={data.data} fill="#f59e0b" fillOpacity={0.7} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default ScatterChartComponent