import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <div className="page-bg-image min-h-screen">
      <App />
    </div>
  </React.StrictMode>
)