import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import Admin from './Admin.jsx'
import './react-shell.css'

const isAdmin = window.location.pathname.replace(/\/+$/, '') === '/admin2'

createRoot(document.getElementById('root')).render(isAdmin ? <Admin /> : <App />)
