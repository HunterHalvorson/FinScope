import React from 'react'
import { useState } from 'react';
import { CiSearch } from "react-icons/ci";
import '../pages/css/Chat.css'
import TypingAnimation from '../components/TypingAnimation';
import ReactMarkdown from 'react-markdown'
import { Link } from "react-router-dom";
import { useNavigate } from 'react-router-dom'

function Chat() {

  const navigate = useNavigate()

  const [ticker, setTicker] = useState('AAPL')
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [allMessages, setAllMessages] = useState([])

  const handleChat = async () => {
    setAllMessages(prev => [...prev, {role: 'user', message: query}])
    setQuery('')
    setLoading(true)
  
    try {
      const res = await fetch(
        `http://localhost:8000/chat?ticker=${ticker}&query=${encodeURIComponent(query)}`,
        {method: 'POST'}
      )
  
      const data = await res.json()
      setQuery('')

      setResponse(data.answer)
      setAllMessages([...allMessages, {role: 'user', message: query}, {role: 'assistant', message: data.answer}])
    } catch (err){
      console.log(err);
    } finally {
      setLoading(false);
    }
  }

  const displayMessages = loading 
  ? [...allMessages, { role: 'assistant', message: '...', isThinking: true }]
  : allMessages

  return (
    <>
      <button onClick={() => navigate('/')}>Return</button>
      <div className='page-container'>
        <div className="help-assistant-container">
          <div className="header">
            <div id='profile-icon'></div>
            <div className="header-group">
              <h2 id='filing-assistant-header'>Filing assistant</h2>
              <h5 id='status'>Active</h5>
            </div>
          </div>

          <div className="body">
            <p>This AI‑powered chat may make mistakes. <span>Learn more</span></p>
            {displayMessages.map((msg, index) => (
              <div key={index} className={`message-group ${msg.role}`}>
                <div className={`message ${msg.isThinking ? 'thinking' : ''}`}>
                  {msg.isThinking ? <TypingAnimation /> : <ReactMarkdown>{msg.message}</ReactMarkdown>}
                </div>
                <div className="message-meta">
                  <div className="small-profile-photo"></div>
                  <p className="time">8:00 PM</p>
                </div>
              </div>
            ))}
          </div>

          <div className="input-bar">
            <div className="search-wrapper">
              <CiSearch className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Search filings..."
                value = {ticker}
                onChange={(e) => setTicker(e.target.value)}
              />
            </div>
            <div className="message-input-wrapper">
              <input
                type="text"
                className="message-input"
                placeholder="Ask a question..."
                value = {query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button className="send-button" onClick={handleChat}>Send</button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Chat