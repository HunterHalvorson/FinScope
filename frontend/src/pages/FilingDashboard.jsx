import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import mockData from '../data/mockData.json'
import NotFoundMessage from '../components/NotFoundMessage'
import '../pages/css/FilingDashboard.css'
import LineChartComponent from '../components/LineChartComponent'
import { CgAddR } from "react-icons/cg";
import Modal from '../components/Modal'

function FilingDashboard() {

  const params = useParams()
  const tickerName = params.symbol
  let [modalActive, setModalActive] = useState(false);
  const [selectedFiling, setSelectedFiling] = useState(null);

  const matchingTickerData = mockData.filter((tickerObject) => tickerObject.ticker === tickerName)

  if (matchingTickerData.length == 0) {
    return <NotFoundMessage />
  }

  const handleFilingClick = (filing) =>{
    setModalActive(!modalActive)
    setSelectedFiling(filing);
  }

  const listData = matchingTickerData[0].filings
    .slice()
    .sort((a, b) => new Date(a.filingDate) - new Date(b.filingDate))
    .map(f => ({
      filingId: f.filingId,
      type: f.type,
      date: f.filingDate,
      positive: f.sentiment.positive,
      negative: f.sentiment.negative,
      uncertainty: f.sentiment.uncertainty,
      litigious: f.sentiment.litigious,
      netSentiment: f.netSentiment,
      forwardReturn30d: f.forwardReturn30d,
      topRiskTopics: f.topRiskTopics
    }));

  return (
    <>
      {modalActive && <Modal onClose={() => setModalActive(false)} filing = {selectedFiling}/>}
      <div style={{ width: '100%', height: 400 }}>
        <h1>{matchingTickerData[0].name}</h1>
        <LineChartComponent matchingTickerData={matchingTickerData} />
      </div>
      <div className="filing-list-container">
        {listData.map((filing) => (
          <h3 onClick={() => handleFilingClick(filing)}>{filing.type} — {filing.date}</h3>
        ))}
      </div>
    </>
  )
}

export default FilingDashboard