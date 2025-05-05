import React, { useState } from 'react'
import { format } from 'date-fns'

// Placeholder image URL
const PLACEHOLDER_IMAGE_URL = 'https://via.placeholder.com/150?text=No+Image'

const FoodLogTable = ({ entries, apiBaseUrl, onRefresh }) => {
  const [captureStatus, setCaptureStatus] = useState('idle'); // 'idle', 'running', 'complete'
  const [captureMessage, setCaptureMessage] = useState('');
  const [captureProgress, setCaptureProgress] = useState(0);
  
  // Function to start the food capture process
  const startFoodCapture = async () => {
    setCaptureStatus('running');
    setCaptureMessage('Starting food capture process...');
    setCaptureProgress(0);
    
    try {
      // Send request to start the capture process
      const response = await fetch(`${apiBaseUrl}/api/start-capture`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      // Start polling for updates
      let complete = false;
      let itemCount = 0;
      
      while (!complete && itemCount < 7) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds between polls
        
        // Check if new items have been added
        const checkResponse = await fetch(`${apiBaseUrl}/api/item-log`);
        if (checkResponse.ok) {
          const data = await checkResponse.json();
          
          // Calculate how many new items have been added
          const newItemCount = data.length;
          itemCount = newItemCount;
          
          // Update progress (7 items total)
          const progress = Math.min(Math.round((itemCount / 7) * 100), 100);
          setCaptureProgress(progress);
          setCaptureMessage(`Captured ${itemCount} of 7 items...`);
          
          if (itemCount >= 7) {
            complete = true;
          }
        }
      }
      
      setCaptureStatus('complete');
      setCaptureMessage('Food capture complete!');
      setCaptureProgress(100);
      
      // Refresh the table
      if (onRefresh) {
        onRefresh();
      }
      
    } catch (error) {
      console.error('Error during food capture:', error);
      setCaptureStatus('idle');
      setCaptureMessage(`Error: ${error.message}`);
    }
  };
  
  // Function to reset the capture process
  const resetCapture = () => {
    setCaptureStatus('idle');
    setCaptureMessage('');
    setCaptureProgress(0);
  };
  
  if (!entries || entries.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500 mb-6">No food logs yet. Start the capture process to log food items.</p>
        
        {captureStatus === 'idle' ? (
          <button 
            onClick={startFoodCapture}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md transition-colors"
          >
            Start Food Capture
          </button>
        ) : captureStatus === 'running' ? (
          <div>
            <p className="mb-2">{captureMessage}</p>
            <div className="w-full max-w-md mx-auto bg-gray-200 rounded-full h-4 mb-4">
              <div 
                className="bg-green-500 h-4 rounded-full transition-all duration-500" 
                style={{ width: `${captureProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500">Please wait while items are being captured...</p>
          </div>
        ) : (
          <div>
            <p className="text-green-600 mb-4">{captureMessage}</p>
            <button 
              onClick={resetCapture}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md transition-colors"
            >
              Reset
            </button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div>
      {/* Control panel for capture process */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        {captureStatus === 'idle' ? (
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Food Capture</h3>
              <p className="text-sm text-gray-500">Start capturing food items</p>
            </div>
            <button 
              onClick={startFoodCapture}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors"
            >
              Start Capture
            </button>
          </div>
        ) : captureStatus === 'running' ? (
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">{captureMessage}</h3>
            <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
              <div 
                className="bg-green-500 h-4 rounded-full transition-all duration-500" 
                style={{ width: `${captureProgress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500">The system is capturing and analyzing food items...</p>
          </div>
        ) : (
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium text-green-600">{captureMessage}</h3>
              <p className="text-sm text-gray-500">All items have been captured successfully</p>
            </div>
            <button 
              onClick={resetCapture}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors"
            >
              Reset
            </button>
          </div>
        )}
      </div>
      
      {/* Food log table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Food Type
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Weight (g)
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Image
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {entries.map((entry, index) => {
              // Support both original format and item_log.json format
              const foodType = entry.food_type || entry.item || 'Unknown';
              const weight = entry.weight_grams || entry.weight || 0;
              const imagePath = entry.image_path || '';
              
              return (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {foodType}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {typeof weight === 'number' ? weight.toFixed(1) : weight}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="block w-16 h-16 overflow-hidden rounded-md border border-gray-200 hover:border-blue-500 transition-colors">
                      {imagePath ? (
                        <img 
                          src={`${apiBaseUrl}/api/images/${imagePath.split('/').pop()}`} 
                          alt={foodType}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            // Fallback to Unsplash if server image fails
                            e.target.onerror = null;
                            e.target.src = `https://source.unsplash.com/100x100/?${encodeURIComponent(foodType)},food`;
                          }}
                        />
                      ) : (
                        <img 
                          src={`https://source.unsplash.com/100x100/?${encodeURIComponent(foodType)},food`}
                          alt={foodType} 
                          className="w-full h-full object-cover"
                        />
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default FoodLogTable 