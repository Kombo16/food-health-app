# main.py
"""Main CLI interface for Food Health App using modular components"""

from services.nutrition_service import NutritionService
from services.risk_assessment_service import RiskAssessmentService
from services.disease_prediction_service import DiseasePredictionService
from models.user import UserProfile
from models.nutrition import DietaryPattern

class FoodHealthCLI:
    """Command Line Interface for Food Health App"""
    
    def __init__(self):
        self.nutrition_service = NutritionService()
        self.risk_service = RiskAssessmentService()
        self.disease_service = DiseasePredictionService(self.nutrition_service)
    
    def collect_user_profile(self) -> UserProfile:
        """Collect user profile information"""
        print("\n📋 USER PROFILE SETUP")
        print("-" * 30)
        
        age = int(input("Age: "))
        gender = input("Gender (male/female): ").lower()
        weight_kg = float(input("Weight (kg): "))
        height_cm = float(input("Height (cm): "))
        
        print("\nActivity levels:")
        print("1. Sedentary (little/no exercise)")
        print("2. Light (light exercise 1-3 days/week)")
        print("3. Moderate (moderate exercise 3-5 days/week)")
        print("4. Active (hard exercise 6-7 days/week)")
        print("5. Very Active (very hard exercise, physical job)")
        
        activity_map = {
            '1': 'sedentary', '2': 'light', '3': 'moderate', 
            '4': 'active', '5': 'very_active'
        }
        activity_choice = input("Select activity level (1-5): ")
        activity_level = activity_map.get(activity_choice, 'moderate')
        
        family_history_input = input("Family history of diseases (comma-separated, or 'none'): ")
        family_history = [d.strip() for d in family_history_input.split(',')] if family_history_input.lower() != 'none' else []
        
        current_conditions_input = input("Current health conditions (comma-separated, or 'none'): ")
        current_conditions = [c.strip() for c in current_conditions_input.split(',')] if current_conditions_input.lower() != 'none' else []
        
        return UserProfile(
            age=age,
            gender=gender,
            weight_kg=weight_kg,
            height_cm=height_cm,
            activity_level=activity_level,
            family_history=family_history,
            current_conditions=current_conditions
        )
    
    def collect_dietary_pattern(self) -> DietaryPattern:
        """Collect dietary pattern information"""
        print("\n🍽️ DIETARY PATTERN TRACKING")
        print("-" * 35)
        
        days_tracked = int(input("How many days of food data do you want to provide? (recommended: 3-7): "))
        all_daily_foods = []
        all_portion_sizes = []
        
        for day in range(days_tracked):
            print(f"\n--- Day {day + 1} ---")
            daily_foods_input = input(f"Foods consumed on day {day + 1} (comma-separated): ")
            daily_foods = [food.strip() for food in daily_foods_input.split(',')]
            
            portion_sizes = []
            for food in daily_foods:
                portion = float(input(f"Portion size of {food} (grams): ") or "100")
                portion_sizes.append(portion)
            
            all_daily_foods.extend(daily_foods)
            all_portion_sizes.extend(portion_sizes)
        
        meal_frequency = int(input("Average number of meals per day: ") or "3")
        
        return DietaryPattern(
            daily_foods=all_daily_foods,
            portion_sizes_g=all_portion_sizes,
            meal_frequency=meal_frequency,
            days_tracked=days_tracked
        )
    
    def run_lifestyle_assessment(self):
        """Run complete lifestyle disease assessment"""
        print("🏥 LIFESTYLE DISEASE RISK ASSESSMENT")
        print("="*50)
        
        # Collect user information
        user_profile = self.collect_user_profile()
        dietary_pattern = self.collect_dietary_pattern()
        
        print("\n🔄 Analyzing your data...")
        print("This may take a moment as we fetch nutrition information...")
        
        # Perform assessment
        assessment = self.disease_service.assess_lifestyle_disease_risk(user_profile, dietary_pattern)
        
        # Display results
        self.disease_service.print_lifestyle_assessment_report(assessment)
        
        return assessment

def demo_preview():
    """Preview demonstration with different food scenarios"""
    print("🍎 FOOD HEALTH APP - PREVIEW DEMONSTRATION")
    print("="*50)
    
    cli = FoodHealthCLI()
    
    # Scenario 1: One healthy food
    print("\n📍 SCENARIO 1: Healthy Food - 'apple'")
    print("-" * 40)
    results = cli.risk_service.analyze_foods(['apple'], cli.nutrition_service)
    cli.risk_service.print_summary_report(results)
    
    # Scenario 2: One unhealthy food
    print("\n📍 SCENARIO 2: Unhealthy Food - 'pizza'")
    print("-" * 40)
    results = cli.risk_service.analyze_foods(['pizza'], cli.nutrition_service)
    cli.risk_service.print_summary_report(results)
    
    # Scenario 3: Multiple unhealthy foods
    print("\n📍 SCENARIO 3: Multiple Unhealthy Foods")
    print("-" * 40)
    unhealthy_foods = ['french fries', 'ice cream', 'soda', 'hamburger']
    results = cli.risk_service.analyze_foods(unhealthy_foods, cli.nutrition_service)
    cli.risk_service.print_summary_report(results)

def main():
    """Main function to run the food health app"""
    cli = FoodHealthCLI()
    
    print("🍎 Food Health Risk Assessment App")
    print("="*40)
    
    while True:
        print("\nOptions:")
        print("1. Analyze individual foods")
        print("2. Run demo preview")
        print("3. Lifestyle Disease Risk Assessment")
        print("4. Quit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            user_input = input("\nEnter food(s) to analyze (comma-separated): ").strip()
            food_list = [food.strip() for food in user_input.split(',')]
            results = cli.risk_service.analyze_foods(food_list, cli.nutrition_service)
            
            if results:
                cli.risk_service.print_summary_report(results)
        
        elif choice == '2':
            demo_preview()
        
        elif choice == '3':
            cli.run_lifestyle_assessment()
        
        elif choice == '4':
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()