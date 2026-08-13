import './index.css'
import { Link } from 'react-router-dom'

function App() {
  

  return (
    <>
      <div className='welcome-container'>
        <nav className="nav-bar">
          <ul>
            <li><Link to = "/">Home</Link></li>
            <li><Link to = "/ticker">Ticker</Link></li>
            <li><Link to = "/filings">Filing Dashboard</Link></li>
            <li><Link to = "/chat">Chat</Link></li>
          </ul>
        </nav>
        <h1>Welcome To <span>FinScope</span></h1>
      </div>
    </>
  )
}

export default App
