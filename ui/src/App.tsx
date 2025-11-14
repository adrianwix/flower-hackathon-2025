import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface HealthResponse {
  status: string
}

const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await fetch(`${API_URL}/health`)
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  return response.json()
}

function App() {
  const [count, setCount] = useState(0)

  const { data, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>

      <div className="card">
        <div style={{ marginBottom: '1rem' }}>
          <h3>Backend Status</h3>
          {isLoading ? (
            <p>Checking backend connection...</p>
          ) : error ? (
            <p style={{ color: '#ff6b6b' }}>❌ Backend Error: {error instanceof Error ? error.message : 'Unknown error'}</p>
          ) : (
            <p style={{ color: '#51cf66' }}>✅ Backend is {data?.status}</p>
          )}
          <p style={{ fontSize: '0.9rem', opacity: 0.7 }}>API: {API_URL}</p>
        </div>

        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
