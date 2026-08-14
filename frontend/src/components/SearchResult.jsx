import React from 'react'
import './SearchResult.css'
import { Link } from 'react-router-dom'

function SearchResult({result, setSelectedTicker}) {


  return (
    <div className='search-result'>
      <Link to = {`/ticker/${result.ticker}`}>
        {result.ticker} — {result.title}
      </Link>
    </div>
  )
}

export default SearchResult