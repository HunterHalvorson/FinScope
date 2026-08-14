import React, {useState} from 'react'
import {FaSearch} from 'react-icons/fa'
import '../components/SearchBar.css'
import tickers from '../data/tickers.json'

function SearchBar({setResults}) {

  const [input, setInput] = useState("")

  const tickerList = Object.values(tickers); 

  const fetchData = (value) => {
    const results = tickerList.filter((ticker) => {
      return value &&
        ticker &&
        (ticker.ticker.toLowerCase().includes(value.toLowerCase()) ||
         ticker.title.toLowerCase().includes(value.toLowerCase()));
    });
    setResults(results);
  }

  const handleChange = (value) => {
    setInput(value);
    fetchData(value);
  }

  return (
    <div className='input-wrapper'>
      <FaSearch id = 'search-icons'/>
      <input placeholder='Type to search...' value = {input} onChange={(e) => {handleChange(e.target.value)}}/>
    </div>
  )
}

export default SearchBar