import React from 'react'
import './SearchResultsList.css'
import SearchResult from './SearchResult'

function SearchResultsList({results, setSelectedTicker}) {
  return (
    <div className='results-list'>
      {
        results.map((result, id) => {
          return <SearchResult result={result} setSelectedTicker = {setSelectedTicker} key = {id}/>
        })
      }
    </div>
  )
}

export default SearchResultsList