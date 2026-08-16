import React from 'react'
import '../components/Modal.css'

function Modal({onClose, filing}) {

  console.log(filing)

  return (
    <>
      <div className="modal-container" onClick={onClose}>
        <div className="model-container-inner" onClick={(e) => e.stopPropagation()}>
          <h2><span>Filing Id:</span> {filing.filingId}</h2>
          <h3><span>Date:</span> {filing.date}</h3>
          <h4><span>Positive: </span>{filing.positive}</h4>
          <h4><span>Negative: </span>{filing.negative}</h4>
          <h4><span>Type: </span>{filing.type}</h4>
        </div>
      </div>
    </>
  )
}

export default Modal