import React from 'react'
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer} from 'recharts'
import mockData from '../data/mockData.json'

function LineChartComponent({matchingTickerData}) {

  const chartData = matchingTickerData[0].filings
    .slice()
    .sort((a, b) => new Date(a.filingDate) - new Date(b.filingDate))
    .map(f => (
      {
        date: f.filingDate,
        positive: f.sentiment.positive,
        negative: f.sentiment.negative,
        uncertainty: f.sentiment.uncertainty,
        netSentiment: f.netSentiment
      }
    ));
  
  console.log(chartData)

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data = {chartData}>
        <CartesianGrid strokeDasharray="3 3"/>
        <XAxis dataKey = "date"/>
        <Legend/>
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="positive" stroke="#a78bfa" strokeWidth={2} />     
        <Line type="monotone" dataKey="negative" stroke="#f472b6" strokeWidth={2} />      
        <Line type="monotone" dataKey="uncertainty" stroke="#818cf8" strokeWidth={2} />   
        <Line type="monotone" dataKey="netSentiment" stroke="#e879f9" strokeWidth={2} />  
      </LineChart>
    </ResponsiveContainer>
  )
}

export default LineChartComponent