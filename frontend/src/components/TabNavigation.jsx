import React from 'react'

const TabNavigation = ({ activeTab, onTabChange }) => {
  return (
    <div className="bg-white shadow-sm">
      <div className="container mx-auto">
        <nav className="flex">
          <button
            className={`px-6 py-4 text-sm font-medium border-b-2 ${
              activeTab === 'foodLog'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => onTabChange('foodLog')}
          >
            Food Log
          </button>
          <button
            className={`px-6 py-4 text-sm font-medium border-b-2 ${
              activeTab === 'recipes'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => onTabChange('recipes')}
          >
            Recipe Suggestions
          </button>
        </nav>
      </div>
    </div>
  )
}

export default TabNavigation 