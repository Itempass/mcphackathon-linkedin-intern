import React from 'react'
import ReactDOM from 'react-dom/client'
import Sidepanel from './Sidepanel'
import './index.css'

console.log('Sidepanel main.tsx loaded');

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Sidepanel />
  </React.StrictMode>,
) 