import React, { useState, useEffect } from 'react'
import { Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, Box, Spinner, Alert, AlertIcon, AlertTitle, AlertDescription, Button, Tabs, TabList, Tab, TabPanels, TabPanel, Heading, Text, List, ListItem, Tag } from '@chakra-ui/react' // Using Chakra UI for better layout

// Helper function to render list items
const renderList = (items) => {
    if (!items || items.length === 0) return <Text fontSize="sm" color="gray.500">Not available.</Text>;
    if (typeof items === 'string') return <Text>{items}</Text>; // Handle if API returns string instead of list
    return (
        <List spacing={1} styleType="disc" pl={5}>
            {items.map((item, index) => (
                <ListItem key={index}>{item}</ListItem>
            ))}
        </List>
    );
};

// Helper function to render numbered list for instructions
const renderInstructions = (items) => {
    if (!items || items.length === 0) return <Text fontSize="sm" color="gray.500">Not available.</Text>;
    if (typeof items === 'string') return <Text>{items}</Text>; // Handle if API returns string instead of list
    return (
        <List as="ol" spacing={2} styleType="decimal" pl={5}>
            {items.map((item, index) => (
                <ListItem key={index}>{item}</ListItem>
            ))}
        </List>
    );
};

const RecipeSuggestions = ({ apiBaseUrl }) => {
  // State: meal type tabs, recipes, loading, error
  const [mealType, setMealType] = useState('any') // Default to 'any' or maybe 'breakfast'?
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const mealTypes = ['any', 'breakfast', 'lunch', 'dinner'];

  // Fetch recipes function
  const fetchRecipes = async (currentMealType) => {
    setLoading(true)
    setError(null)
    setRecipes([]) // Clear previous recipes
    console.log(`Fetching recipes for: ${currentMealType}`);
    
    try {
      // Fetch full recipes directly from the updated API endpoint
      const response = await fetch(`${apiBaseUrl}/api/recipes?meal_type=${currentMealType}&num=3`)
      
      if (!response.ok) {
        let errorMsg = `Failed to fetch recipes: ${response.statusText}`;
         try {
            const errData = await response.json();
            // Use error message from backend if available
            errorMsg = errData.error || errData.message || errorMsg;
         } catch (e) { /* Ignore if response body is not JSON */ }
        throw new Error(errorMsg)
      }
      
      const data = await response.json()

      // Check if the data itself contains an error message from the AI
      if (Array.isArray(data) && data.length > 0 && data[0]?.error) {
        throw new Error(data[0].error);
      }
      
      // Ensure data is an array
      if (!Array.isArray(data)) {
        console.error("API did not return an array:", data);
        throw new Error("Received unexpected data format from server.");
      }

      setRecipes(data)
      
    } catch (err) {
      console.error(`Error fetching recipes:`, err)
      setError(`Failed to load recipes: ${err.message}. Please try again.`)
    } finally {
      setLoading(false)
    }
  }
  
  // Fetch recipes when the component mounts or mealType changes
  useEffect(() => {
    fetchRecipes(mealType)
  }, [mealType, apiBaseUrl]) // Re-fetch if apiBaseUrl changes too

  // Handle tab change
  const handleTabsChange = (index) => {
    setMealType(mealTypes[index]);
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>Recipe Suggestions</Heading>
      
      {/* Meal Type Tabs */}
      <Tabs index={mealTypes.indexOf(mealType)} onChange={handleTabsChange} mb={6} variant="soft-rounded" colorScheme="blue">
        <TabList>
          {mealTypes.map(type => (
            <Tab key={type} textTransform="capitalize">{type}</Tab>
          ))}
        </TabList>
      </Tabs>

       {/* Refresh Button */} 
       <Button 
         mb={6}
         onClick={() => fetchRecipes(mealType)} 
         isLoading={loading} 
         loadingText="Generating..."
         colorScheme="blue"
       >
         Generate New Recipes
       </Button>

      {/* Loading State */}
      {loading && (
        <Box textAlign="center" py={10}>
          <Spinner size="xl" />
          <Text mt={4}>Generating recipe ideas...</Text>
        </Box>
      )}

      {/* Error Display */}
      {error && !loading && (
        <Alert status="error" mb={6} borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Error!</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
      )}

      {/* Recipe Results - Accordion */}
      {!loading && !error && recipes.length > 0 && (
        <Accordion allowMultiple>
          {recipes.map((recipe, index) => (
            // Skip rendering if recipe seems invalid or is an error placeholder
            !recipe.error && recipe.name ? (
              <AccordionItem key={index} borderTopWidth={index === 0 ? "1px" : undefined} borderBottomWidth="1px">
                <h2>
                  <AccordionButton _expanded={{ bg: 'blue.50', color: 'blue.800' }}>
                    <Box flex="1" textAlign="left" fontWeight="semibold">
                      {recipe.name || `Recipe Suggestion ${index + 1}`}
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <Box mb={4}>
                     <Heading size="sm" mb={2}>Description</Heading>
                     <Text fontSize="sm">{recipe.introduction || "No description available."}</Text>
                  </Box>

                  <Box display="flex" gap={4} mb={4} flexWrap="wrap">
                     {recipe.prepTime && <Tag size="md" variant='subtle' colorScheme='gray'>Prep: {recipe.prepTime}</Tag>}
                     {recipe.cookTime && <Tag size="md" variant='subtle' colorScheme='gray'>Cook: {recipe.cookTime}</Tag>}
                     {recipe.servings && <Tag size="md" variant='subtle' colorScheme='gray'>Servings: {recipe.servings}</Tag>}
                  </Box>

                  <Box mb={4}>
                     <Heading size="sm" mb={2}>Ingredients</Heading>
                     {renderList(recipe.ingredients)}
                  </Box>
                  
                  <Box mb={4}>
                     <Heading size="sm" mb={2}>Instructions</Heading>
                     {renderInstructions(recipe.instructions)}
                  </Box>

                  {recipe.nutritionalInfo && (
                      <Box mb={4}>
                         <Heading size="sm" mb={2}>Nutritional Info</Heading>
                         <Text fontSize="sm">{recipe.nutritionalInfo}</Text>
                      </Box>
                  )}

                  {recipe.tips && (
                       <Box>
                         <Heading size="sm" mb={2}>Tips & Variations</Heading>
                         <Text fontSize="sm">{recipe.tips}</Text>
                       </Box>
                  )}
                </AccordionPanel>
              </AccordionItem>
            ) : null // Don't render item if name is missing or it's an error
          ))}
        </Accordion>
      )}

      {/* No Recipes Found Message */}
      {!loading && !error && recipes.length === 0 && (
        <Box textAlign="center" py={10} color="gray.500">
          <Text>No recipes generated for "{mealType}".</Text>
          <Text mt={2}>Try generating recipes again, or check the food log.</Text>
        </Box>
      )}
    </Box>
  )
}

export default RecipeSuggestions;
// Removed previous complex state and logic for selecting ideas and generating full recipes separately. 