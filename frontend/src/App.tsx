import { useEffect, useState } from 'react'
import { healthCheck } from './services/api'

function App() {
  const [health, setHealth] = useState<string | null>(null)

  useEffect(() => {
    async function fetchHealth() {
      try {

        const data = await healthCheck()
        setHealth(data.data.status)
      }catch (error) {
        setHealth('Error fetching health status')
      }
    }
    setHealth('Loading...')

    fetchHealth()
  }, [])

  return (
    <>
      <main className='w-7xl mx-auto flex flex-col items-center justify-center min-h-screen p-4'>
        <h1 className='text-4xl font-bold mb-4'>Health Check: {health}</h1>
      </main>
    </>
  )
}

export default App
