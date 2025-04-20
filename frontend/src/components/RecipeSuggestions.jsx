import React, { useState, useEffect } from 'react'

const RecipeSuggestions = ({ ingredients }) => {
  const [selectedCategory, setSelectedCategory] = useState('breakfast')
  const [selectedRecipe, setSelectedRecipe] = useState(null)
  const [availableIngredients, setAvailableIngredients] = useState({})
  const [recipes, setRecipes] = useState({
    breakfast: [],
    lunch: [],
    dinner: []
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [generatingRecipe, setGeneratingRecipe] = useState(false)
  const [fullRecipe, setFullRecipe] = useState(null)
  
  // Process the ingredients to create a map of ingredient name to available amount
  useEffect(() => {
    const ingredientMap = {}
    ingredients.forEach((item) => {
      ingredientMap[item.food_type] = item.weight_grams
    })
    setAvailableIngredients(ingredientMap)
  }, [ingredients])
  
  // Fetch recipes for a specific meal type
  const fetchRecipes = async (mealType) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`/api/recipe-ideas?meal_type=${mealType}`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch recipes: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      // Update recipes for the specified meal type
      setRecipes(prev => ({
        ...prev,
        [mealType]: data || []
      }))
      
    } catch (err) {
      console.error(`Error fetching ${mealType} recipes:`, err)
      setError(`Failed to load ${mealType} recipes: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }
  
  // Generate a detailed recipe when a dish is selected
  const handleRecipeSelect = async (recipe) => {
    setSelectedRecipe(recipe)
    
    try {
      setGeneratingRecipe(true)
      
      // Call the API to generate a full recipe
      const response = await fetch('/api/recipe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipe_name: recipe.name,
          ingredients: recipe.requiredAmounts
        })
      })
      
      if (!response.ok) {
        throw new Error(`Failed to generate recipe: ${response.statusText}`)
      }
      
      const data = await response.json()
      setFullRecipe(data)
      
    } catch (err) {
      console.error('Error generating recipe:', err)
      setError(`Failed to generate recipe: ${err.message}`)
    } finally {
      setGeneratingRecipe(false)
    }
  }
  
  // Fetch recipes for the current meal type
  const handleRefresh = () => {
    fetchRecipes(selectedCategory)
  }
  
  // Fetch recipes when the category changes
  useEffect(() => {
    // Only fetch if we don't already have recipes for this category
    if (recipes[selectedCategory].length === 0 && !loading) {
      fetchRecipes(selectedCategory)
    }
  }, [selectedCategory])
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Recipe Suggestions</h2>
        <button 
          onClick={handleRefresh}
          disabled={loading}
          className={`bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {loading ? 'Generating...' : 'Generate New Recipes'}
        </button>
      </div>
      
      {/* Category Selection */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button
            className={`px-4 py-2 rounded-md ${selectedCategory === 'breakfast' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => setSelectedCategory('breakfast')}
          >
            Breakfast
          </button>
          <button
            className={`px-4 py-2 rounded-md ${selectedCategory === 'lunch' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => setSelectedCategory('lunch')}
          >
            Lunch
          </button>
          <button
            className={`px-4 py-2 rounded-md ${selectedCategory === 'dinner' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => setSelectedCategory('dinner')}
          >
            Dinner
          </button>
        </div>
      </div>
      
      {/* Loading state */}
      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {/* Error message */}
      {error && !loading && (
        <div className="bg-red-100 text-red-700 p-4 rounded-md mb-6">
          {error}
        </div>
      )}
      
      {/* Recipe Cards */}
      {!loading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recipes[selectedCategory].map((recipe, index) => (
            <div 
              key={index} 
              className={`border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow ${selectedRecipe?.name === recipe.name ? 'ring-2 ring-blue-500' : ''}`}
              onClick={() => handleRecipeSelect(recipe)}
            >
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-2">{recipe.name}</h3>
                <p className="text-gray-600 text-sm mb-4">{recipe.description}</p>
                
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">Ingredients:</h4>
                  <ul className="text-sm text-gray-600">
                    {recipe.ingredients.map((ingredient) => (
                      <li key={ingredient} className="flex justify-between">
                        <span>{ingredient}</span>
                        <span>{recipe.requiredAmounts[ingredient]}g</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="px-4 py-3 bg-gray-50 flex justify-end">
                <button 
                  className="text-sm font-medium text-blue-600 hover:text-blue-800" 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRecipeSelect(recipe);
                  }}
                >
                  Generate Recipe
                </button>
              </div>
            </div>
          ))}
          
          {recipes[selectedCategory].length === 0 && !loading && (
            <div className="col-span-full text-center py-12 text-gray-500">
              <p>No recipes available for this meal category.</p>
              <p className="mt-2 text-sm">Click "Generate New Recipes" to create recipe suggestions.</p>
            </div>
          )}
        </div>
      )}
      
      {/* Full Recipe Details */}
      {selectedRecipe && (
        <div className="mt-8 p-6 border rounded-lg bg-gray-50">
          <h3 className="text-xl font-semibold mb-4">{selectedRecipe.name} Recipe</h3>
          
          {generatingRecipe ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : fullRecipe ? (
            <div className="space-y-4">
              {fullRecipe.introduction && (
                <div>
                  <h4 className="font-medium">Introduction</h4>
                  <p className="text-gray-700">{fullRecipe.introduction}</p>
                </div>
              )}
              
              <div className="grid grid-cols-3 gap-4 text-sm">
                {fullRecipe.prepTime && (
                  <div className="bg-gray-100 p-3 rounded">
                    <span className="block font-medium">Prep Time</span>
                    <span>{fullRecipe.prepTime}</span>
                  </div>
                )}
                
                {fullRecipe.cookTime && (
                  <div className="bg-gray-100 p-3 rounded">
                    <span className="block font-medium">Cook Time</span>
                    <span>{fullRecipe.cookTime}</span>
                  </div>
                )}
                
                {fullRecipe.servings && (
                  <div className="bg-gray-100 p-3 rounded">
                    <span className="block font-medium">Servings</span>
                    <span>{fullRecipe.servings}</span>
                  </div>
                )}
              </div>
              
              {fullRecipe.ingredients && (
                <div>
                  <h4 className="font-medium">Ingredients</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {Array.isArray(fullRecipe.ingredients) ? 
                      fullRecipe.ingredients.map((ing, idx) => (
                        <li key={idx}>{ing}</li>
                      )) : 
                      Object.entries(fullRecipe.ingredients).map(([ing, amount], idx) => (
                        <li key={idx}>{ing}: {amount}</li>
                      ))
                    }
                  </ul>
                </div>
              )}
              
              {fullRecipe.instructions && (
                <div>
                  <h4 className="font-medium">Instructions</h4>
                  {Array.isArray(fullRecipe.instructions) ? (
                    <ol className="list-decimal pl-5 space-y-2">
                      {fullRecipe.instructions.map((step, idx) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  ) : (
                    <p className="text-gray-700">{fullRecipe.instructions}</p>
                  )}
                </div>
              )}
              
              {fullRecipe.nutritionalInfo && (
                <div>
                  <h4 className="font-medium">Nutritional Information</h4>
                  <p className="text-gray-700">{fullRecipe.nutritionalInfo}</p>
                </div>
              )}
              
              {fullRecipe.tips && (
                <div>
                  <h4 className="font-medium">Tips & Variations</h4>
                  <p className="text-gray-700">{fullRecipe.tips}</p>
                </div>
              )}
            </div>
          ) : (
            <p className="mb-4 italic text-gray-600">
              Click "Generate Recipe" to create a detailed recipe with instructions using the ChatGPT API.
            </p>
          )}
          
          <div className="flex justify-end mt-4">
            <button 
              className="text-sm font-medium text-gray-600 hover:text-gray-800"
              onClick={() => {
                setSelectedRecipe(null)
                setFullRecipe(null)
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default RecipeSuggestions 