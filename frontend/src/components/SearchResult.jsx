import React from 'react'
import './SearchResult.css'

function SearchResult({result}) {
  return (
    <div className='search-result'>
      {result.ticker} — {result.title}
    </div>
  )
}

export default SearchResult