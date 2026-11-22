import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './App.css'
import AppFunctional from './AppFunctional'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppFunctional />
  </StrictMode>,
)
