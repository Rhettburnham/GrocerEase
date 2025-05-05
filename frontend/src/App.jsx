import { useState, useEffect } from 'react'
import { format } from 'date-fns'
import FoodLogTable from './components/FoodLogTable'
import RecipeSuggestions from './components/RecipeSuggestions'
import Header from './components/Header'
import TabNavigation from './components/TabNavigation'

// Define the base URL for the API
// We'll check both ports 8000 and 8001
const API_BASE_URL_OPTIONS = [
  import.meta.env.VITE_API_BASE_URL,
  'http://localhost:8000',
  'http://localhost:8001'
];

function App() {
  const [logEntries, setLogEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('foodLog') // 'foodLog' or 'recipes'
  const [apiBaseUrl, setApiBaseUrl] = useState('')
  
  // Function to test API endpoints and find working one
  useEffect(() => {
    const checkApiEndpoints = async () => {
      for (const url of API_BASE_URL_OPTIONS) {
        if (!url) continue;
        
        try {
          const response = await fetch(`${url}/api/health`, { 
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            // Short timeout for quick check
            signal: AbortSignal.timeout(2000)
          });
          
          if (response.ok) {
            console.log(`API endpoint working: ${url}`);
            setApiBaseUrl(url);
            return;
          }
        } catch (err) {
          console.log(`API endpoint ${url} not available`);
        }
      }
      
      // If we get here, no endpoints worked
      setApiBaseUrl(API_BASE_URL_OPTIONS[1]); // Default to localhost:8000
      setError("Could not connect to API server. Make sure it's running.")
    };
    
    checkApiEndpoints();
  }, []);
  
  // Function to fetch log entries from the backend API
  const fetchLogEntries = async () => {
    if (!apiBaseUrl) return;
    
    try {
      setLoading(true)
      setError(null) // Clear previous errors
      
      // Fetch the data from the backend API endpoint
      const response = await fetch(`${apiBaseUrl}/api/item-log`)
      if (!response.ok) {
        // Try to get error message from backend response
        let errorMsg = `HTTP error! status: ${response.status}`;
        try {
            const errData = await response.json();
            errorMsg = errData.error || errorMsg;
        } catch (e) {
            // Ignore if response is not JSON
        }
        throw new Error(errorMsg)
      }
      const data = await response.json()
      setLogEntries(data)

    } catch (err) {
      console.error('Error fetching log entries:', err)
      setError(`Failed to load food log: ${err.message}`)
      setLogEntries([]) // Clear potentially stale data on error
    } finally {
      setLoading(false)
    }
  }
  
  // Fetch log entries when API base URL is determined and active tab is 'foodLog'
  useEffect(() => {
    if (apiBaseUrl && activeTab === 'foodLog') {
        fetchLogEntries()
    }
  }, [apiBaseUrl, activeTab]) 
  
  // Function to handle tab changes
  const handleTabChange = (tab) => {
    setActiveTab(tab)
  }
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />
      
      <main className="container mx-auto px-4 py-8 flex-grow">
        {/* Global Error Display */} 
        {error && activeTab === 'foodLog' && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'foodLog' ? (
            <>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-800">Food Log</h2>
                <button 
                  onClick={fetchLogEntries} // Keep refresh button
                  disabled={loading} // Disable while loading
                  className={`bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {loading ? 'Refreshing...' : 'Refresh'}
                </button>
              </div>
              
              {loading && logEntries.length === 0 ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                </div>
              ) : !loading && logEntries.length === 0 && !error ? (
                 <p className="text-center text-gray-500 py-4">Your food log is empty. Add items using the FoodBot!</p>
              ) : (
                <FoodLogTable entries={logEntries} apiBaseUrl={apiBaseUrl} onRefresh={fetchLogEntries} />
              )}
            </>
          ) : (
            // Pass API base URL and trigger fetch from within the component
            <RecipeSuggestions apiBaseUrl={apiBaseUrl} /> 
          )}
        </div>
      </main>
      
      <footer className="bg-gray-800 text-white py-4 mt-auto">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; {new Date().getFullYear()} GrocerEase FoodBot</p>
        </div>
      </footer>
    </div>
  )
}

export default App 