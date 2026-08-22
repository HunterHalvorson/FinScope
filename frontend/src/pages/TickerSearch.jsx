import { mockTickers } from "./mockData";
import './css/TickerSearch.css'
import SearchBar from "../components/SearchBar";
import { useState } from "react";
import SearchResultsList from "../components/SearchResultsList";
import { Link } from "react-router-dom";
import { useNavigate } from 'react-router-dom'

export default function TickerSearch(){

  const navigate = useNavigate()

  const [result, setResult] = useState([])

  return (

    <>
      <button onClick={() => navigate('/')}>Return</button>
      <div className = 'ticker'>
      <h1>Search for a <span>Company</span></h1>
      <p className="search-subtext">
        Enter a ticker or company name to view filing sentiment and stock performance.
      </p>
      <div className="search-bar-container">
        <SearchBar setResults = {setResult}/>
        <SearchResultsList results = {result}/>
      </div>
    </div>
    </>
  );
}