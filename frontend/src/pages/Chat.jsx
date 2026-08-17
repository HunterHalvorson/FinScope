import React from 'react'
import { useState } from 'react';
import { CiSearch } from "react-icons/ci";
import '../pages/css/Chat.css'

function Chat() {

  const mockMessages = [
    {
      id: "msg-1",
      role: "user",
      content: "What did Apple cite as its top risk factor in the most recent 10-K?",
    },
    {
      id: "msg-2",
      role: "assistant",
      content:
        "In the 2024-11-01 10-K, Apple's top-listed risk factor was global supply chain concentration, particularly reliance on manufacturing partners in a small number of countries. The filing also flags heightened uncertainty around new tariffs and export restrictions compared to the prior year's filing.",
      citations: [
        { filingId: "aapl-2024-q4-10k", date: "2024-11-01", section: "Risk Factors" },
        { filingId: "aapl-2024-q4-10k", date: "2024-11-01", section: "MD&A" },
      ],
    },
    {
      id: "msg-3",
      role: "user",
      content: "How does that compare to what they said in 2023?",
    },
    {
      id: "msg-4",
      role: "assistant",
      content:
        "In the 2023-11-02 10-K, supply chain risk was also listed first, but the language was less specific — it referenced 'geopolitical tensions' broadly rather than naming tariffs or export controls directly. The shift in specificity between the two filings lines up with the drop in net sentiment score from 0.12 to -0.03 over that period.",
      citations: [
        { filingId: "aapl-2023-q4-10k", date: "2023-11-02", section: "Risk Factors" },
      ],
    },
    {
      id: "msg-5",
      role: "user",
      content: "Did sentiment recover after that?",
    },
    {
      id: "msg-6",
      role: "assistant",
      content:
        "Yes. Net sentiment climbed back to 0.09 by the 2024-08-01 10-Q and reached 0.11 in the most recent filing, tracking a similar rebound in positive-word density across the MD&A sections.",
      citations: [
        { filingId: "aapl-2024-q3-10q", date: "2024-08-01", section: "MD&A" },
        { filingId: "aapl-2024-q4-10k", date: "2024-11-01", section: "MD&A" },
      ],
    },
  ];

  return (
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
          {mockMessages.map((msg) => (
            <div key={msg.id} className={`message-group ${msg.role}`}>
              <div className="message">{msg.content}</div>
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
            />
          </div>
          <div className="message-input-wrapper">
            <input
              type="text"
              className="message-input"
              placeholder="Ask a question..."
            />
            <button className="send-button">Send</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat