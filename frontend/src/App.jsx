import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import FoodLogTable from './components/FoodLogTable'
import RecipeSuggestions from './components/RecipeSuggestions'
import Header from './components/Header'
import TabNavigation from './components/TabNavigation'

function App() {
  const [logEntries, setLogEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('foodLog') // 'foodLog' or 'recipes'
  
  // Function to fetch log entries directly from our JSON file
  const fetchLogEntries = async () => {
    try {
      setLoading(true)
      
      // Fetch the data from our local JSON file
      const response = await fetch('/data/food_log.json')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setLogEntries(data)
      setError(null)
    } catch (err) {
      console.error('Error fetching log entries:', err)
      setError('Failed to load data. Please try again later.')
    } finally {
      setLoading(false)
    }
  }
  
  // Fetch log entries on component mount
  useEffect(() => {
    fetchLogEntries()
  }, [])
  
  // Function to handle tab changes
  const handleTabChange = (tab) => {
    setActiveTab(tab)
  }
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />
      
      <main className="container mx-auto px-4 py-8 flex-grow">
        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'foodLog' ? (
            <>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-800">Food Log</h2>
                <button 
                  onClick={fetchLogEntries}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors"
                >
                  Refresh
                </button>
              </div>
              
              {loading && logEntries.length === 0 ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                </div>
              ) : error ? (
                <div className="bg-red-100 text-red-700 p-4 rounded-md">{error}</div>
              ) : (
                <FoodLogTable entries={logEntries} />
              )}
            </>
          ) : (
            <RecipeSuggestions ingredients={logEntries} />
          )}
        </div>
      </main>
      
      <footer className="bg-gray-800 text-white py-4">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; {new Date().getFullYear()} FoodBot - Powered by Raspberry Pi</p>
        </div>
      </footer>
    </div>
  )
}

export default App 