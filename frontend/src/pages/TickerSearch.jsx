import { mockTickers } from "./mockData";
import './css/TickerSearch.css'
import SearchBar from "../components/SearchBar";
import { useState } from "react";
import SearchResultsList from "../components/SearchResultsList";

export default function TickerSearch(){

  const [result, setResult] = useState([])

  return (
    <div className = 'ticker'>
      <div className="search-bar-container">
        <SearchBar setResults = {setResult}/>
        <SearchResultsList results = {result}/>
      </div>
    </div>
  );
}