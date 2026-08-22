import './TypingAnimation.css'
import React, { useState, useEffect } from 'react'

function TypingAnimation() {
  const [dots, setDots] = React.useState('.')
  
  React.useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length === 3 ? '.' : prev + '.')
    }, 500)
    return () => clearInterval(interval)
  }, [])
  
  return <span>{dots}</span>
}

export default TypingAnimation