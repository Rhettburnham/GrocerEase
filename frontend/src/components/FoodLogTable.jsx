import React, { useState } from 'react'
import { format } from 'date-fns'

// Placeholder image URL
const PLACEHOLDER_IMAGE_URL = 'https://via.placeholder.com/150?text=No+Image'

const FoodLogTable = ({ entries, apiBaseUrl, onRefresh }) => {
  const [captureStatus, setCaptureStatus] = useState('idle'); // 'idle', 'running', 'complete'
  const [captureMessage, setCaptureMessage] = useState('');
  
  // Function to start a single food capture
  const startSingleCapture = async () => {
    setCaptureStatus('running');
    setCaptureMessage('Capturing food item...');
    
    try {
      // Send request to start the capture process (single item)
      const response = await fetch(`${apiBaseUrl}/api/start-capture`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ num_items: 1 })
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      // Poll for completion
      let complete = false;
      let initialItemCount = entries ? entries.length : 0;
      let pollCount = 0;
      
      while (!complete && pollCount < 15) { // Max 30 seconds (15 * 2s)
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
        pollCount++;
        
        // Check if new item has been added
        const checkResponse = await fetch(`${apiBaseUrl}/api/item-log`);
        if (checkResponse.ok) {
          const data = await checkResponse.json();
          
          if (data.length > initialItemCount) {
            complete = true;
          }
        }
        
        // Also check capture status endpoint
        const statusResponse = await fetch(`${apiBaseUrl}/api/capture-status`);
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          if (!statusData.running) {
            complete = true;
          }
        }
      }
      
      // Mark capture as complete
      setCaptureStatus('complete');
      setCaptureMessage('Item captured successfully!');
      
      // Refresh the table
      if (onRefresh) {
        onRefresh();
      }
      
      // Auto-reset after 3 seconds
      setTimeout(() => {
        setCaptureStatus('idle');
        setCaptureMessage('');
      }, 3000);
      
    } catch (error) {
      console.error('Error during food capture:', error);
      setCaptureStatus('idle');
      setCaptureMessage(`Error: ${error.message}`);
    }
  };
  
  // Always show the capture control panel
  const renderCaptureControls = () => (
    <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
      {captureStatus === 'idle' ? (
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Food Capture</h3>
            <p className="text-sm text-gray-500">Press the button to capture a food item</p>
          </div>
          <button 
            onClick={startSingleCapture}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors"
          >
            Capture Item
          </button>
        </div>
      ) : captureStatus === 'running' ? (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">{captureMessage}</h3>
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500"></div>
          </div>
          <p className="text-sm text-gray-500 text-center mt-2">The system is capturing and analyzing a food item...</p>
        </div>
      ) : (
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-green-600">{captureMessage}</h3>
            <p className="text-sm text-gray-500">Ready to capture another item</p>
          </div>
          <button 
            onClick={startSingleCapture}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors"
          >
            Capture Another
          </button>
        </div>
      )}
    </div>
  );
  
  return (
    <div>
      {/* Always render capture controls */}
      {renderCaptureControls()}
      
      {/* Food log table - only if there are entries */}
      {entries && entries.length > 0 ? (
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
      ) : captureStatus !== 'running' && (
        // Display message when no entries and not capturing
        <div className="text-center py-6">
          <p className="text-gray-500">No food logs yet. Press the Capture Item button to start logging food.</p>
        </div>
      )}
    </div>
  )
}

export default FoodLogTable 