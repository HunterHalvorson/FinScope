import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import NotFoundMessage from '../components/NotFoundMessage'
import '../pages/css/FilingDashboard.css'
import LineChartComponent from '../components/LineChartComponent'
import Modal from '../components/Modal'
import ScatterChartComponenet from '../components/ScatterChartComponenet'

function FilingDashboard() {

  const { symbol } = useParams()
  const [filings, setFilings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modalActive, setModalActive] = useState(false)
  const [selectedFiling, setSelectedFiling] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resultsResponse = await fetch(`http://localhost:8000/results?ticker=${symbol}`);
        const resultData = await resultsResponse.json();

        // transform the data
        const listData = resultData
          .sort((a, b) => new Date(a.filing_date) - new Date(b.filing_date))
          .map(filing => ({
            filingId: `${filing.ticker}-${filing.accession}`,
            type: filing.form,
            date: filing.filing_date,
            positive: filing.mda_positive,      
            negative: filing.mda_negative,
            uncertainty: filing.mda_uncertainty,
            litigious: filing.mda_litigious,
            netSentiment: filing.mda_positive - filing.mda_negative,
            forwardReturn30d: filing.forward_return,
            topRiskTopics: [] 
          }))
        setFilings(listData);
        setLoading(false);
      }catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }
    fetchData()
  }, [symbol])

  

  const handleFilingClick = (filing) =>{
    setModalActive(!modalActive)
    setSelectedFiling(filing);
  }


  if (loading)return <div>Loading...</div>
  if (error || filings.length === 0) return <NotFoundMessage />

  return (
    <>
      {modalActive && <Modal onClose={() => setModalActive(false)} filing = {selectedFiling}/>}
      <h1>{symbol}</h1>
      <div style={{ width: '100%', height: 400, marginBottom: 80 }}>
        <LineChartComponent matchingTickerData={filings} ticker={symbol} />
      </div>
      <div style={{ width: '100%', height: 400, marginBottom: 800 }}>
        <ScatterChartComponenet ticker={symbol} />
      </div>
      <div className="filing-list-container">
        {filings.map((filing) => (
          <h3 onClick={() => handleFilingClick(filing)}>{filing.type} — {filing.date}</h3>
        ))}
      </div>
    </>
  )
}

export default FilingDashboard