import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import TickerSearch from './pages/TickerSearch.jsx';
import NotFoundPage from './pages/NotFoundPage.jsx';
import Chat from './pages/Chat.jsx';
import FilingDashboard from './pages/FilingDashboard.jsx';

const router = createBrowserRouter([
  { path: '/', element: <App />, errorElement: <NotFoundPage /> },
  { path: '/ticker', element: <TickerSearch />, errorElement: <NotFoundPage /> },
  { path: '/chat', element: <Chat />, errorElement: <NotFoundPage /> },
  { path: '/filings', element: <FilingDashboard />, errorElement: <NotFoundPage /> },
  { path: '*', element: <NotFoundPage /> },
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)