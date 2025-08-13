""" Nutrition-related data models """

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class NutritionInfo:
    """ Represents nutritional information of a food item """
    food_name: str
    calories_per_100g: float
    sugar_g: float
    saturated_fat_g: float
    sodium_mg: float
    category: str
    source: str

@dataclass
class RiskAssessment:
    """ Represents a risk assessment for a food item based on nutritional information """
    food_name: str
    risk_score: float
    is_risky: bool
    risk_factors: Dict[str, str]
    alternatives: List[str]

@dataclass
class DietaryPattern:
    """ Represents a user's dietary pattern """
    daily_foods: List[str]
    portion_sizes_g: List[float]
    meal_frequency: int
    days_tracked: int