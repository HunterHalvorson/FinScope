import React from 'react'
import {useParams} from 'react-router-dom'
import mockData from '../data/mockData.json'
import NotFoundMessage from '../components/NotFoundMessage'
import '../pages/css/FilingDashboard.css'

function FilingDashboard() {

  const params = useParams()
  const tickerName = params.symbol

  const matchingTickerData = mockData.filter((tickerObject) => tickerObject.ticker === tickerName)

  console.log(matchingTickerData)

  if (matchingTickerData.length == 0){
    return <NotFoundMessage/>
  }

  return (
    <>
     <h1>{matchingTickerData[0].name}</h1>
    </>
  )
}

export default FilingDashboard