import React, { useState, useEffect } from 'react'

const RecipeSuggestions = ({ apiBaseUrl }) => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeMealType, setActiveMealType] = useState(null);

  const fetchRecipes = async (mealType) => {
    try {
      setLoading(true);
      setActiveMealType(mealType);
      
      const response = await fetch(`${apiBaseUrl}/api/recipes?meal_type=${mealType}&num_suggestions=3`);
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      setRecipes(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching recipes:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const MealTypeButton = ({ type, label }) => (
    <button
      onClick={() => fetchRecipes(type)}
      className={`px-4 py-2 rounded-md font-medium transition-colors ${
        activeMealType === type 
          ? 'bg-green-500 text-white' 
          : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="p-4 bg-white border border-gray-200 rounded-md shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Recipe Suggestions</h2>
      
      <div className="flex gap-4 mb-6">
        <MealTypeButton type="breakfast" label="Breakfast" />
        <MealTypeButton type="lunch" label="Lunch" />
        <MealTypeButton type="dinner" label="Dinner" />
      </div>
      
      {!activeMealType && !loading && (
        <div className="p-4 bg-blue-50 rounded-md">
          <p className="text-gray-700">Select a meal type to see recipe suggestions based on your food log items.</p>
        </div>
      )}
      
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">Error loading recipes: {error}</p>
        </div>
      )}
      
      {activeMealType && !loading && recipes.length === 0 && (
        <p className="text-gray-500">No recipe suggestions available for {activeMealType}. Try adding more food items.</p>
      )}
      
      {!loading && recipes.length > 0 && (
        <div className="space-y-6">
          {recipes.map((recipe, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-md border border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">{recipe.name}</h3>
              <p className="text-sm text-gray-600 mt-1 mb-3">{recipe.introduction}</p>
              
              <div className="flex flex-wrap gap-3 text-xs mb-3">
                {recipe.prepTime && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                    Prep: {recipe.prepTime}
                  </span>
                )}
                {recipe.cookTime && (
                  <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full">
                    Cook: {recipe.cookTime}
                  </span>
                )}
                {recipe.servings && (
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full">
                    Serves: {recipe.servings}
                  </span>
                )}
              </div>
              
              <div className="mt-3">
                <h4 className="text-md font-medium text-gray-800">Ingredients:</h4>
                <ul className="list-disc pl-5 mt-1">
                  {recipe.ingredients && recipe.ingredients.map((ingredient, i) => (
                    <li key={i} className="text-sm text-gray-600">{ingredient}</li>
                  ))}
                </ul>
              </div>
              
              {recipe.instructions && (
                <div className="mt-3">
                  <h4 className="text-md font-medium text-gray-800">Instructions:</h4>
                  <ol className="list-decimal pl-5 mt-1">
                    {recipe.instructions.map((step, i) => (
                      <li key={i} className="text-sm text-gray-600 mt-1">{step}</li>
                    ))}
                  </ol>
                </div>
              )}
              
              {recipe.tips && (
                <div className="mt-3 p-2 bg-yellow-50 rounded border border-yellow-100">
                  <h4 className="text-sm font-medium text-gray-800">Tips:</h4>
                  <p className="text-sm text-gray-600">{recipe.tips}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecipeSuggestions 