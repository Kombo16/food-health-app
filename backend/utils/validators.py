""" Input validation utilities for Food Health App """

import re
from typing import Union, Tuple, List, Dict, Any
from models.user import UserProfile
from models.nutrition import DietaryPattern

class InputValidator:
    """ Handles input validation for the Food Health App """
    @staticmethod
    def validate_food_name(food_name: str) -> Tuple[bool, str]:
        """ Validate food name input """
        if not food_name:
            return False, "Food name cannot be empty."
        
        food_name = food_name.strip()

        if len(food_name) < 2 or len(food_name) > 100:
            return False, "Food name must be between 2 and 100 characters."
        
        pattern = r'^[a-zA-Z0-9\s\-\(\)\.,\'&]+$'
        if not re.match(pattern, food_name):
            return False, "Food name contains invalid characters. Use only letters, numbers, spaces, and common punctuation."
        
        return True, "Valid"
    
    @staticmethod
    def validate_food_list(foods: Union[str, List[str]]) -> Tuple[bool, str, List[str]]:
        """Validate and clean a list of foods"""
        if isinstance(foods, str):
            foods = [f.strip() for f in foods.split(',') if f.strip()]
        
        if not foods:
            return False, "At least one food item must be provided", []
        
        if len(foods) > 20:
            return False, "Cannot analyze more than 20 foods at once", []
        
        cleaned_foods = []
        for food in foods:
            is_valid, error_msg = InputValidator.validate_food_name(food)
            if not is_valid:
                return False, f"Invalid food '{food}': {error_msg}", []
            cleaned_foods.append(food.strip().lower())
        
        return True, "Valid", cleaned_foods
    
    @staticmethod
    def validate_user_profile_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate user profile data"""
        required_fields = ['age', 'gender', 'weight', 'height', 'activity_level']
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                return False, f"Missing required field: {field}"
        
        # Validate age
        try:
            age = int(data['age'])
            if not (1 <= age <= 120):
                return False, "Age must be between 1 and 120 years"
        except (ValueError, TypeError):
            return False, "Age must be a valid number"
        
        # Validate gender
        valid_genders = ['male', 'female', 'other']
        if data['gender'].lower() not in valid_genders:
            return False, f"Gender must be one of: {', '.join(valid_genders)}"
        
        # Validate weight
        try:
            weight = float(data['weight'])
            if not (20 <= weight <= 500):
                return False, "Weight must be between 20 and 500 kg"
        except (ValueError, TypeError):
            return False, "Weight must be a valid number"
        
        # Validate height
        try:
            height = float(data['height'])
            if not (50 <= height <= 250):
                return False, "Height must be between 50 and 250 cm"
        except (ValueError, TypeError):
            return False, "Height must be a valid number"
        
        # Validate activity level
        valid_activities = ['sedentary', 'light', 'moderate', 'active', 'very_active']
        if data['activity_level'] not in valid_activities:
            return False, f"Activity level must be one of: {', '.join(valid_activities)}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_dietary_pattern_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate dietary pattern data"""
        required_fields = ['daily_foods', 'portion_sizes']
        
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate foods
        is_valid, error_msg, cleaned_foods = InputValidator.validate_food_list(data['daily_foods'])
        if not is_valid:
            return False, error_msg
        
        # Validate portion sizes
        portion_sizes = data['portion_sizes']
        if isinstance(portion_sizes, str):
            try:
                portion_sizes = [float(p.strip()) for p in portion_sizes.split(',') if p.strip()]
            except ValueError:
                return False, "Portion sizes must be valid numbers"
        
        if not portion_sizes:
            return False, "Portion sizes cannot be empty"
        
        if len(cleaned_foods) != len(portion_sizes):
            return False, "Number of foods must match number of portion sizes"
        
        for i, portion in enumerate(portion_sizes):
            try:
                portion = float(portion)
                if not (1 <= portion <= 2000):
                    return False, f"Portion size for '{cleaned_foods[i]}' must be between 1 and 2000 grams"
            except (ValueError, TypeError):
                return False, f"Invalid portion size for '{cleaned_foods[i]}'"
        
        # Validate optional fields
        if 'meal_frequency' in data:
            try:
                meal_freq = int(data['meal_frequency'])
                if not (1 <= meal_freq <= 10):
                    return False, "Meal frequency must be between 1 and 10"
            except (ValueError, TypeError):
                return False, "Meal frequency must be a valid number"
        
        if 'days_tracked' in data:
            try:
                days = int(data['days_tracked'])
                if not (1 <= days <= 30):
                    return False, "Days tracked must be between 1 and 30"
            except (ValueError, TypeError):
                return False, "Days tracked must be a valid number"
        
        return True, "Valid"
    
    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not input_string:
            return ""
        
        # Remove potential HTML/script tags
        input_string = re.sub(r'<[^>]*>', '', input_string)
        
        # Remove excessive whitespace
        input_string = ' '.join(input_string.split())
        
        # Truncate if too long
        return input_string[:max_length]
    
    @staticmethod
    def validate_health_conditions(conditions: Union[str, List[str]]) -> Tuple[bool, str, List[str]]:
        """Validate health conditions/family history"""
        if isinstance(conditions, str):
            if conditions.lower().strip() in ['none', 'n/a', '']:
                return True, "Valid", []
            conditions = [c.strip() for c in conditions.split(',') if c.strip()]
        
        if not conditions:
            return True, "Valid", []
        
        if len(conditions) > 10:
            return False, "Cannot specify more than 10 conditions", []
        
        cleaned_conditions = []
        valid_conditions = [
            'diabetes', 'type 1 diabetes', 'type 2 diabetes',
            'hypertension', 'high blood pressure',
            'heart disease', 'cardiac', 'coronary heart disease',
            'obesity', 'stroke', 'cancer', 'kidney disease',
            'liver disease', 'thyroid', 'arthritis', 'asthma'
        ]
        
        for condition in conditions:
            condition = InputValidator.sanitize_string(condition.lower(), 50)
            if len(condition) < 2:
                return False, f"Condition '{condition}' is too short", []
            
            # Check if it's a reasonable health condition
            if not any(valid_cond in condition for valid_cond in valid_conditions):
                # Allow it but sanitize it
                pass
            
            cleaned_conditions.append(condition)
        
        return True, "Valid", cleaned_conditions

