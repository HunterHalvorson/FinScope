import React from 'react'
import { Link } from 'react-router-dom'
import './NotFoundMessage.css'
import { FiSlash } from "react-icons/fi";

function NotFoundMessage() {
  return (
    <div className='message-container'>
      <FiSlash id = 'stop-icon'/>
      <h2>Ticker Not Found</h2>
      <p>We don't have filing data for this ticker yet. Please check the symbol or return to search.</p>
      <button><Link to="/ticker">Back to Search</Link></button>
    </div>
  )
}

export default NotFoundMessage