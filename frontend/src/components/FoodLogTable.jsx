import React from 'react'
import { format, parseISO } from 'date-fns'

// Placeholder image URL
const PLACEHOLDER_IMAGE_URL = 'https://via.placeholder.com/150?text=No+Image'

const FoodLogTable = ({ entries }) => {
  if (!entries || entries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No food logs yet. Press the button on your FoodBot to get started!</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Time
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Food Type
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Weight (g)
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Confidence
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Image
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {entries.map((entry) => (
            <tr key={entry.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {format(parseISO(entry.timestamp), 'MMM d, yyyy HH:mm:ss')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">
                  {entry.food_type}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {entry.weight_grams.toFixed(1)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {entry.confidence ? (
                  <div className="flex items-center">
                    <div className="mr-2 h-2 w-16 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 rounded-full" 
                        style={{ width: `${Math.round(entry.confidence * 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-500">
                      {Math.round(entry.confidence * 100)}%
                    </span>
                  </div>
                ) : (
                  <span className="text-sm text-gray-500">N/A</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {/* Generate food-specific placeholder images based on the food type */}
                <div className="block w-16 h-16 overflow-hidden rounded-md border border-gray-200 hover:border-blue-500 transition-colors">
                  <img 
                    src={`https://source.unsplash.com/100x100/?${entry.food_type.replace(/\s+/g, '-')},food`}
                    alt={entry.food_type} 
                    className="w-full h-full object-cover"
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default FoodLogTable 