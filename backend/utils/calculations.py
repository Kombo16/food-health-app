""" Health calculation utilities """

from config.settings import ACTIVITY_MULTIPLIERS
from models.user import UserProfile

class HealthCalculator:
    """ Utility class for health-related calculations """

    def calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """ Calculate Body Mass Index (BMI) """
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def calculate_daily_maintenance_calories(self, profile: UserProfile) -> float:
        """ Calculate daily maintenance calories using Mifflin-St Jeor equation """
        if profile.gender == 'male':
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
        else:
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161 

        return bmr * ACTIVITY_MULTIPLIERS.get(profile.activity_level, 1.55)

    def get_bmi_category(self, bmi: float) -> str:
        """ Determine BMI category """
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi < 24.9:
            return 'Normal weight'
        elif 25 <= bmi < 29.9:
            return 'Overweight'
        else:
            return 'Obesity'
