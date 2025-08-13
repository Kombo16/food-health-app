""" Nutrition data fetching and amanagement service """

import requests
import wikipedia
import re
from typing import Optional

from config.settings import API_CONFIG, FOOD_CATEGORIES
from models.nutrition import NutritionInfo
from services.database_service import DatabaseService
from utils.food_categorizer import FoodCategorizer

class NutritionService:
    """ Handles nutrition data fetching from various sources """
    def __init__(self, db_service = None):
        if db_service is None:
            self.db_service = DatabaseService()
        else:
            self.db_service = db_service
        self.food_categorizer = FoodCategorizer(food_categories=FOOD_CATEGORIES)
        self._request_count = 0

    def get_food_nutrition(self, food_name: str) -> Optional[NutritionInfo]:
        """ Fetch nutritional information for a given food item """
        found_in_db = False
        found_in_api = False
        found_in_wikipedia = False
        user_provided_info = False

        #1. Check if food is already in the database
        nutrition_info = self.db_service.get_food_from_db(food_name)
        if nutrition_info:
            found_in_db = True
            self.db_service.log_user_query(food_name, found_in_db, found_in_api, found_in_wikipedia, user_provided_info)
            return nutrition_info
        
        #2.  Fetch from external API
        nutrition_info = self._search_usda_api(food_name)
        if nutrition_info:
            found_in_api = True
            self.db_service.save_food_to_db(nutrition_info)
            self.db_service.log_user_query(food_name, found_in_db, found_in_api, found_in_wikipedia, user_provided_info)
            return nutrition_info
        
        #3. Fallback to Wikipedia
        nutrition_info = self._search_wikipedia_fallback(food_name)
        if nutrition_info:
            found_in_wikipedia = True
            self.db_service.save_food_to_db(nutrition_info)
            self.db_service.log_user_query(food_name, found_in_db, found_in_api, found_in_wikipedia, user_provided_info)
            return nutrition_info
        #4. Ask user for nutritional information(for command line interface)
        nutrition_info = self._get_user_nutrition_input(food_name)
        if nutrition_info:
            user_provided_info = True
            self.db_service.save_food_to_db(nutrition_info)
            self.db_service.log_user_query(food_name, found_in_db, found_in_api, found_in_wikipedia, user_provided_info)
            return nutrition_info
        
    def _search_usda_api(self, food_name: str) -> Optional[NutritionInfo]:
        """ Search USDA FoodData Central API for food information """
        try:
            # Check if API key is available
            if not API_CONFIG.get('api_key'):
                print("⚠️ USDA API key not configured, skipping API call")
                return None
        
            self._request_count += 1
            print(f"📡 API Request #{self._request_count} for: {food_name}")
            
            # Check if we're approaching rate limits
            if self._request_count > 950:  # Conservative limit
                print("⚠️ Approaching API rate limit, skipping API call")
                return None
            #Search for food
            search_url = f"{API_CONFIG['base_url']}/foods/search"
            params = {
                'query': food_name,
                'api_key': API_CONFIG['api_key'],
                'pageSize': 1,
                'dataType': ["Survey (FNDDS)"]
            }

            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get('foods'):
                print(f"❌ No results found for '{food_name}' in API")
                return None
            
            food_item = data['foods'][0]

            #Get detailed nutrition info
            food_id = food_item['fdcId']
            detail_url = f"{API_CONFIG['base_url']}/food/{food_id}"
            detail_params = {'api_key': API_CONFIG['api_key']}

            detail_response = requests.get(detail_url, params=detail_params)
            detail_response.raise_for_status()
            detail_data = detail_response.json()

            # Extract nutrition data
            nutrients = {n['nutrient']['name'].lower(): n.get('amount', 0)
                        for n in detail_data.get('foodNutrients', [])}
            #Map nutrient names to our standardized format
            sugar = nutrients.get('sugars, total including nlea', 0) or nutrients.get('total sugars', 0)
            sat_fat = nutrients.get('fatty acids, total saturated', 0)
            sodium = nutrients.get('sodium, na', 0)
            calories = nutrients.get('energy', 0)

            #Determin category based on food description
            description = food_item.get('description', '').lower()
            category = self.food_categorizer.categorize(description)

            nutrition_info = NutritionInfo(
                food_name=food_item.get('description', food_name),
                calories_per_100g=calories,
                sugar_g=sugar,
                saturated_fat_g=sat_fat,
                sodium_mg=sodium,
                category=category,
                source='api'
            )

            return nutrition_info
        except Exception as e:
            print(f"❌ Error calling USDA API for '{food_name}': {e}")
            return None
        
    def _search_wikipedia_fallback(self, food_name: str) -> Optional[NutritionInfo]:
        """ Fallback to Wikipedia for food nutrition information """
        try:
            #Search Wikipedia
            search_results = wikipedia.search(f"{food_name} nutrition")
            if not search_results:
                print(f"❌ No Wikipedia results found for '{food_name}'")
                return None
            
            page = wikipedia.page(search_results[0])
            content = page.content.lower()

            #Simple pattern matching for nutrition info
            sugar_match = re.search(r'sugar[s]?\D*?(d+(?:\.\d+)?)\s*(?:g|gram)', content)
            fat_match = re.search(r'saturated fat\D*?(\d+(?:\.\d+)?)\s*(?:g|gram)', content)
            sodium_match = re.search(r'sodium\D*?(\d+(?:\.\d+)?)\s*(?:mg|milligram)', content)
            calories_match = re.search(r'calorie[s]?\D*?(\d+(?:\.\d+)?)', content)

            sugar = float(sugar_match.group(1)) if sugar_match else 0
            sat_fat = float(fat_match.group(1)) if fat_match else 0
            sodium = float(sodium_match.group(1)) if sodium_match else 0
            calories = float(calories_match.group(1)) if calories_match else 0

            #Categorize food item
            category = self.food_categorizer.categorize(food_name)

            nutrition_info = NutritionInfo(
                food_name=food_name,
                calories_per_100g=calories,
                sugar_g=sugar,
                saturated_fat_g=sat_fat,
                sodium_mg=sodium,
                category=category,
                source='wikipedia'
            )

            return nutrition_info
        except wikipedia.exceptions.PageError:
            return None
        except wikipedia.exceptions.DisambiguationError:
            return None
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return None
        
    def _get_user_nutrition_input(self, food_name: str) -> Optional[NutritionInfo]:
        """ Prompt user for nutritional information if not found in other sources """
        print(f"Please provide nutritional information for {food_name} (per 100g):")
        try:
            calories = float(input("Calories: ") or "0")
            sugar = float(input("Sugar (g): ") or "0")
            sat_fat = float(input("Saturated Fat (g): ") or "0")
            sodium = float(input("Sodium (mg): ") or "0")
            category = input("Food category: (fruits/vegetables/grains/proteins/dairy/snacks):") or "unknown"

            nutrition_info = NutritionInfo(
                food_name=food_name,
                calories_per_100g=calories,
                sugar_g=sugar,
                saturated_fat_g=sat_fat,
                sodium_mg=sodium,
                category=category,
                source='user'
            )

            return nutrition_info
        except ValueError:
            print("Invalid input. Please enter numeric values for nutrition data.")
            return None