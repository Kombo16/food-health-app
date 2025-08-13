""" Risk Assessment service for food health analysis """

from typing import Dict, List
from config.settings import RISK_THRESHOLDS, FOOD_CATEGORIES
from models.nutrition import NutritionInfo, RiskAssessment
from services.database_service import DatabaseService

class RiskAssessmentService:
    """ Handles risk assessment for food items based on nutritional information """

    def __init__(self, db_service = None):
        if db_service is None:
            self.db_service = DatabaseService()
        else:
            self.db_service = db_service
        self.thresholds = RISK_THRESHOLDS
        self.food_categories = FOOD_CATEGORIES

    def calculate_risk_score(self, nutrition_info: NutritionInfo) -> RiskAssessment:
        """ Calculate risk score based on nutrition thresholds """
        risk_score = 0
        risk_factors = {}

        # Sugar risk assessment
        if nutrition_info.sugar_g > self.thresholds['sugar_high']:
            risk_score += 3
            risk_factors['sugar'] = 'high'
        elif nutrition_info.sugar_g > self.thresholds['sugar_medium']:
            risk_score += 1
            risk_factors['sugar'] = 'medium'
        
        # Saturated fat risk assessment
        if nutrition_info.saturated_fat_g > self.thresholds['sat_fat_high']:
            risk_score += 3
            risk_factors['saturated_fat'] = 'high'
        elif nutrition_info.saturated_fat_g > self.thresholds['sat_fat_medium']:
            risk_score += 1
            risk_factors['saturated_fat'] = 'medium'
        
        # Sodium risk assessment
        if nutrition_info.sodium_mg > self.thresholds['sodium_high']:
            risk_score += 3
            risk_factors['sodium'] = 'high'
        elif nutrition_info.sodium_mg > self.thresholds['sodium_medium']:
            risk_score += 1
            risk_factors['sodium'] = 'medium'

        # Determine if food is risky
        is_risky = risk_score >= 5

        #Get alternatives if risky
        alternatives = self._get_healthy_alternatives(nutrition_info.category) if is_risky else []

        assessment = RiskAssessment(
            food_name=nutrition_info.food_name,
            risk_score=risk_score,
            is_risky=is_risky,
            risk_factors=risk_factors,
            alternatives=alternatives
        )

        # Save risk assessment to database
        self.db_service.save_risk_assessment(assessment)

        return assessment
    
    def _get_healthy_alternatives(self, category: str) -> List[str]:
        """ Get healthy alternatives based on food category """
        return self.food_categories.get(category, [])

    def analyze_foods(self, food_list: List[str], nutrition_service) -> Dict[str, RiskAssessment]:
        """ Analyze food items and return risk assessments """
        results = {}

        for food_name in food_list:
            print(f"Analyzing {food_name}...")

            nutrition_info = nutrition_service.get_food_nutrition(food_name)
            if nutrition_info:
                risk_assessment = self.calculate_risk_score(nutrition_info)
                results[food_name] = risk_assessment
                # Print results
                print(f"✓ Found nutrition data (source: {nutrition_info.source})")
                print(f"  Nutrition (per 100g): {nutrition_info.calories_per_100g:.1f} cal, "
                      f"{nutrition_info.sugar_g:.1f}g sugar, {nutrition_info.saturated_fat_g:.1f}g sat fat, "
                      f"{nutrition_info.sodium_mg:.1f}mg sodium")
                print(f"  Risk Score: {risk_assessment.risk_score}")
                print(f"  Risky: {'Yes' if risk_assessment.is_risky else 'No'}")
                
                if risk_assessment.risk_factors:
                    print(f"  Risk Factors: {risk_assessment.risk_factors}")
                
                if risk_assessment.alternatives:
                    print(f"  Healthy Alternatives: {', '.join(risk_assessment.alternatives)}")
            else:
                print(f"Nutrition information for {food_name} not found.")

        return results
    def print_summary_report(self, results: Dict[str, RiskAssessment]):
        """Print a summary report of all analyzed foods"""
        print("\n" + "="*60)
        print("FOOD HEALTH RISK ASSESSMENT SUMMARY")
        print("="*60)
        
        risky_foods = [food for food, assessment in results.items() if assessment.is_risky]
        safe_foods = [food for food, assessment in results.items() if not assessment.is_risky]
        
        print(f"Total foods analyzed: {len(results)}")
        print(f"Risky foods: {len(risky_foods)}")
        print(f"Safe foods: {len(safe_foods)}")
        
        if risky_foods:
            print("\n🚨 RISKY FOODS:")
            for food in risky_foods:
                assessment = results[food]
                print(f"  • {food} (Risk Score: {assessment.risk_score})")
                if assessment.alternatives:
                    print(f"    Alternatives: {', '.join(assessment.alternatives)}")
        
        if safe_foods:
            print("\n✅ SAFE FOODS:")
            for food in safe_foods:
                print(f"  • {food}")