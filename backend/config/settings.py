""" Application settings and configuration constants """
import os
from dotenv import load_dotenv

load_dotenv()
#USDA API Configuration
API_CONFIG = {
    'api_key': os.getenv('USDA_API_KEY'),
    'base_url': "https://api.nal.usda.gov/fdc/v1"
}

#Risk threshholds (per 100g)
RISK_THRESHOLDS = {
    'sugar_high' : 15.0,  # >15g sugar per 100g
    'sugar_medium' : 5.0, # 5-15g sugar per 100g
    'sat_fat_high' : 5.0, # >5g saturated fat per 100g
    'sat_fat_medium' : 1.5, # 1.5-5g saturated fat per 100g
    'sodium_high' : 600.0, # >600mg sodium per 100g
    'sodium_medium' : 120.0, # 120-500mg sodium per 100g
}

# Food categories for alternatives
FOOD_CATEGORIES = {
    'fruits': ['apple', 'banana', 'orange', 'berries', 'grapes', 'watermelons'],
    'vegetables': ['broccoli', 'spinach', 'carrots', 'bell peppers', 'kales'],
    'grains': ['quinoa', 'brown rice', 'oats', 'whole wheat bread'],
    'proteins': ['chicken breast', 'salmon', 'tofu', 'lentils', 'eggs'],
    'dairy': ['Greek yogurt', 'cottage cheese', 'almond milk'],
    'snacks': ['nuts', 'seeds', 'air-popped popcorn', 'dark chocolate']
}

# Disease risk thresholds and weights
DISEASE_THRESHOLDS = {
    'diabetes': {
        'daily_sugar_g': 50,  # WHO recommendation
        'bmi_threshold': 25,
        'family_history_multiplier': 1.5
    },
    'hypertension': {
        'daily_sodium_mg': 2300,  # AHA recommendation
        'bmi_threshold': 25,
        'age_threshold': 45
    },
    'heart_disease': {
        'daily_sat_fat_g': 13,  # AHA recommendation for 2000 cal diet
        'daily_sodium_mg': 2300,
        'bmi_threshold': 25,
        'family_history_multiplier': 2.0
    },
    'obesity': {
        'daily_calories_excess': 500,  # Calories above maintenance
        'bmi_threshold': 30
    }
}

# Activity level multipliers for calorie calculation
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9
}