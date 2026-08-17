import React from 'react'
import '../components/Modal.css'

function Modal({onClose, filing}) {

  console.log(filing)

  return (
    <>
      <div className="modal-container" onClick={onClose}>
        <div className="model-container-inner" onClick={(e) => e.stopPropagation()}>
          <div className="esc" onClick={onClose}>X</div>
          <h2><span>Filing Id:</span> {filing.filingId}</h2>
          <h2><span>Date:</span> {filing.date}</h2>
          <h3><span>Positive: </span>{filing.positive}</h3>
          <h3><span>Negative: </span>{filing.negative}</h3>
          <h3><span>Type: </span>{filing.type}</h3>
        </div>
      </div>
    </>
  )
}

export default Modal