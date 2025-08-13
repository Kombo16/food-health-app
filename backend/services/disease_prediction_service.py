""" Disease prediction and lifestyle assessment service """

from typing import Dict, List

from config.settings import DISEASE_THRESHOLDS
from models.user import UserProfile
from models.nutrition import DietaryPattern
from models.disease import DiseaseRisk, LifestyleDiseaseAssessment
from services.database_service import DatabaseService
from utils.calculations import HealthCalculator

class DiseasePredictionService:
    """ Handles lifestyle disease predicirton and assessment """
    def __init__(self, nutrition_service, db_service = None):
        self.nutrition_service = nutrition_service
        if db_service is None:
            self.db_service = DatabaseService()
        else:
            self.db_service = db_service
        self.disease_thresholds = DISEASE_THRESHOLDS
        self.health_calculator = HealthCalculator()

    def assess_lifestyle_disease_risk(self, profile: UserProfile, dietary_pattern: DietaryPattern) -> LifestyleDiseaseAssessment:
        """ Assess the risk of lifestyle diseases based on user profile and dietary pattern """
        #save user profile and dietary pattern
        user_id = self.db_service.save_user_profile(profile)

        if user_id > 0:
            self.db_service.save_dietary_pattern(dietary_pattern, user_id)
        #Analyze dietary intake
        daily_intake = self.analyze_dietary_intake(dietary_pattern)
        #Predict individual disease risks
        disease_risks = [
            self._predict_diabetes_risk(profile, daily_intake),
            self._predict_hypertension_risk(profile, daily_intake),
            self._predict_heart_disease_risk(profile, daily_intake)
        ]
        #calculate overall risk score (weighted average)
        weights = {'Type 2 Diabetes': 0.3, 'Hypertension': 0.35, 'Heart Disease': 0.35}
        overall_risk_score = sum(risk.risk_percentage * weights.get(risk.disease_name, 0.33) for risk in disease_risks) * 100

        #indentify key dietary factors
        maintenance_calories = self.health_calculator.calculate_daily_maintenance_calories(profile)
        key_dietary_factors = {
            'excess_calories': max(0, daily_intake['calories'] - maintenance_calories),
            'excess_sugar': max(0, daily_intake['sugar_g'] - 50),
            'excess_saturated_fat': max(0, daily_intake['saturated_fat_g'] - 13),
            'excess_sodium': max(0, daily_intake['sodium_mg'] - 2300)
        }
        
        # Determine intervention priorities
        intervention_priority = []
        if key_dietary_factors['excess_sodium'] > 500:
            intervention_priority.append("Reduce sodium intake (high priority)")
        if key_dietary_factors['excess_saturated_fat'] > 5:
            intervention_priority.append("Reduce saturated fat intake")
        if key_dietary_factors['excess_sugar'] > 20:
            intervention_priority.append("Reduce sugar intake")
        if key_dietary_factors['excess_calories'] > 300:
            intervention_priority.append("Reduce caloric intake")

        # Save disease risk assessments
        if user_id > 0:
            for risk in disease_risks:
                self.db_service.save_disease_assessment(user_id, risk)

        return LifestyleDiseaseAssessment(
            user_profile=profile,
            dietary_pattern=dietary_pattern,
            disease_risks=disease_risks,
            overall_risk_score=overall_risk_score,
            key_dietary_factors=key_dietary_factors,
            intervention_priority=intervention_priority
        )
    
    def analyze_dietary_intake(self, dietary_pattern: DietaryPattern) -> Dict[str, float]:
        """Analyze total daily nutritional intake"""
        total_nutrition = {
            'calories': 0.0,
            'sugar_g': 0.0,
            'saturated_fat_g': 0.0,
            'sodium_mg': 0.0
        }
        
        for i, food in enumerate(dietary_pattern.daily_foods):
            nutrition_info = self.nutrition_service.get_food_nutrition(food)
            if nutrition_info:
                portion_factor = dietary_pattern.portion_sizes_g[i] / 100  # Convert to per portion
                
                calories = float(nutrition_info.calories_per_100g) if nutrition_info.calories_per_100g else 0.0
                sugars = float(nutrition_info.sugar_g) if nutrition_info.sugar_g else 0.0
                sat_fat = float(nutrition_info.saturated_fat_g) if nutrition_info.saturated_fat_g else 0.0
                sodium = float(nutrition_info.sodium_mg) if nutrition_info.sodium_mg else 0.0

                total_nutrition['calories'] += calories * portion_factor
                total_nutrition['sugar_g'] += sugars * portion_factor
                total_nutrition['saturated_fat_g'] += sat_fat * portion_factor
                total_nutrition['sodium_mg'] += sodium * portion_factor
        
        # Average per day
        days = dietary_pattern.days_tracked
        daily_intake = {k: v / days for k, v in total_nutrition.items()}
        
        return daily_intake
    
    def _predict_diabetes_risk(self, profile: UserProfile, daily_intake: Dict[str, float]) -> DiseaseRisk:
        """Predict Type 2 Diabetes risk"""
        risk_score = 0
        contributing_factors = []
        
        # BMI factor
        bmi = self.health_calculator.calculate_bmi(profile.weight_kg, profile.height_cm)
        if bmi >= 30:
            risk_score += 30
            contributing_factors.append("Obesity (BMI ≥ 30)")
        elif bmi >= 25:
            risk_score += 15
            contributing_factors.append("Overweight (BMI 25-29.9)")
        
        # Age factor
        if profile.age >= 45:
            risk_score += 10
            contributing_factors.append("Age ≥ 45 years")
        
        # Diet factors
        if daily_intake['sugar_g'] > self.disease_thresholds['diabetes']['daily_sugar_g']:
            excess_sugar = daily_intake['sugar_g'] - self.disease_thresholds['diabetes']['daily_sugar_g']
            risk_score += min(25, excess_sugar * 0.5)
            contributing_factors.append(f"High sugar intake ({daily_intake['sugar_g']:.1f}g/day)")
        
        # Family history
        if 'diabetes' in [fh.lower() for fh in profile.family_history]:
            risk_score *= self.disease_thresholds['diabetes']['family_history_multiplier']
            contributing_factors.append("Family history of diabetes")
        
        # Cap at 100%
        risk_percentage = min(100, risk_score)
        
        # Determine risk level
        if risk_percentage < 20:
            risk_level = 'low'
        elif risk_percentage < 40:
            risk_level = 'moderate'
        elif risk_percentage < 70:
            risk_level = 'high'
        else:
            risk_level = 'very_high'
        
        recommendations = [
            "Reduce daily sugar intake to <50g",
            "Maintain healthy weight (BMI 18.5-24.9)",
            "Exercise regularly (150+ minutes/week)",
            "Monitor blood glucose levels"
        ]
        
        return DiseaseRisk(
            disease_name='Type 2 Diabetes',
            risk_percentage=risk_percentage,
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations
        )
    
    def _predict_hypertension_risk(self, profile: UserProfile, daily_intake: Dict[str, float]) -> DiseaseRisk:
        """Predict Hypertension risk"""
        risk_score = 0
        contributing_factors = []
        
        # Age factor
        age_threshold = 45 if profile.gender == 'male' else 55
        if profile.age >= age_threshold:
            risk_score += 15
            contributing_factors.append(f"Age ≥ {age_threshold} years")
        
        # BMI factor
        bmi = self.health_calculator.calculate_bmi(profile.weight_kg, profile.height_cm)
        if bmi >= 25:
            risk_score += 20
            contributing_factors.append("Overweight/Obese")
        
        # Sodium intake
        if daily_intake['sodium_mg'] > self.disease_thresholds['hypertension']['daily_sodium_mg']:
            excess_sodium = daily_intake['sodium_mg'] - self.disease_thresholds['hypertension']['daily_sodium_mg']
            risk_score += min(30, excess_sodium * 0.01)
            contributing_factors.append(f"High sodium intake ({daily_intake['sodium_mg']:.0f}mg/day)")
        
        # Family history
        if 'hypertension' in [fh.lower() for fh in profile.family_history] or 'high blood pressure' in [fh.lower() for fh in profile.family_history]:
            risk_score += 15
            contributing_factors.append("Family history of hypertension")
        
        risk_percentage = min(100, risk_score)
        
        if risk_percentage < 25:
            risk_level = 'low'
        elif risk_percentage < 50:
            risk_level = 'moderate'
        elif risk_percentage < 75:
            risk_level = 'high'
        else:
            risk_level = 'very_high'
        
        recommendations = [
            "Reduce sodium intake to <2,300mg/day",
            "Maintain healthy weight",
            "Regular aerobic exercise",
            "Limit alcohol consumption",
            "Manage stress levels"
        ]
        
        return DiseaseRisk(
            disease_name='Hypertension',
            risk_percentage=risk_percentage,
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations
        )
    
    def _predict_heart_disease_risk(self, profile: UserProfile, daily_intake: Dict[str, float]) -> DiseaseRisk:
        """Predict Heart Disease risk"""
        risk_score = 0
        contributing_factors = []
        
        # Age and gender factors
        if (profile.gender == 'male' and profile.age >= 45) or (profile.gender == 'female' and profile.age >= 55):
            risk_score += 10
            contributing_factors.append("Advanced age")
        
        # BMI factor
        bmi = self.health_calculator.calculate_bmi(profile.weight_kg, profile.height_cm)
        if bmi >= 25:
            risk_score += 15
            contributing_factors.append("Overweight/Obese")
        
        # Saturated fat intake
        if daily_intake['saturated_fat_g'] > self.disease_thresholds['heart_disease']['daily_sat_fat_g']:
            excess_fat = daily_intake['saturated_fat_g'] - self.disease_thresholds['heart_disease']['daily_sat_fat_g']
            risk_score += min(25, excess_fat * 2)
            contributing_factors.append(f"High saturated fat intake ({daily_intake['saturated_fat_g']:.1f}g/day)")
        
        # Sodium factor
        if daily_intake['sodium_mg'] > self.disease_thresholds['heart_disease']['daily_sodium_mg']:
            risk_score += 10
            contributing_factors.append("High sodium intake")
        
        # Family history
        heart_conditions = ['heart disease', 'cardiac', 'heart attack', 'coronary']
        if any(condition in ' '.join(profile.family_history).lower() for condition in heart_conditions):
            risk_score *= self.disease_thresholds['heart_disease']['family_history_multiplier']
            contributing_factors.append("Family history of heart disease")
        
        risk_percentage = min(100, risk_score)
        
        if risk_percentage < 20:
            risk_level = 'low'
        elif risk_percentage < 40:
            risk_level = 'moderate'
        elif risk_percentage < 70:
            risk_level = 'high'
        else:
            risk_level = 'very_high'
        
        recommendations = [
            "Reduce saturated fat to <13g/day",
            "Increase omega-3 fatty acids",
            "Regular cardiovascular exercise",
            "Don't smoke",
            "Control cholesterol levels"
        ]
        
        return DiseaseRisk(
            disease_name='Heart Disease',
            risk_percentage=risk_percentage,
            risk_level=risk_level,
            contributing_factors=contributing_factors,
            recommendations=recommendations
        )
    
    def print_lifestyle_assessment_report(self, assessment: LifestyleDiseaseAssessment):
        """Print comprehensive lifestyle disease assessment report"""
        print("\n" + "="*70)
        print("🏥 LIFESTYLE DISEASE RISK ASSESSMENT REPORT")
        print("="*70)
        
        # User profile summary
        profile = assessment.user_profile
        bmi = self.health_calculator.calculate_bmi(profile.weight_kg, profile.height_cm)
        print(f"\n👤 USER PROFILE:")
        print(f"   Age: {profile.age} years | Gender: {profile.gender.title()}")
        print(f"   BMI: {bmi:.1f} | Activity: {profile.activity_level.replace('_', ' ').title()}")
        
        # Overall risk
        print(f"\n📊 OVERALL LIFESTYLE DISEASE RISK: {assessment.overall_risk_score:.1f}%")
        if assessment.overall_risk_score < 25:
            print("   Status: ✅ LOW RISK")
        elif assessment.overall_risk_score < 50:
            print("   Status: ⚠️ MODERATE RISK")
        elif assessment.overall_risk_score < 75:
            print("   Status: 🚨 HIGH RISK")
        else:
            print("   Status: 🔴 VERY HIGH RISK")
        
        # Individual disease risks
        print(f"\n🔍 INDIVIDUAL DISEASE RISKS:")
        for risk in assessment.disease_risks:
            risk_emoji = {"low": "✅", "moderate": "⚠️", "high": "🚨", "very_high": "🔴"}
            print(f"\n   {risk_emoji.get(risk.risk_level, '❓')} {risk.disease_name}: {risk.risk_percentage:.1f}% ({risk.risk_level.upper()} RISK)")
            
            if risk.contributing_factors:
                print(f"      Contributing factors: {', '.join(risk.contributing_factors)}")
            
            print(f"      Recommendations:")
            for rec in risk.recommendations[:3]:  # Show top 3 recommendations
                print(f"        • {rec}")
        
        # Key dietary factors
        print(f"\n🍽️ KEY DIETARY RISK FACTORS:")
        factors = assessment.key_dietary_factors
        if factors['excess_calories'] > 100:
            print(f"   • Excess calories: +{factors['excess_calories']:.0f} cal/day above maintenance")
        if factors['excess_sugar'] > 10:
            print(f"   • Excess sugar: +{factors['excess_sugar']:.1f}g/day above recommended")
        if factors['excess_saturated_fat'] > 2:
            print(f"   • Excess saturated fat: +{factors['excess_saturated_fat']:.1f}g/day above recommended")
        if factors['excess_sodium'] > 200:
            print(f"   • Excess sodium: +{factors['excess_sodium']:.0f}mg/day above recommended")
        
        # Intervention priorities
        if assessment.intervention_priority:
            print(f"\n🎯 INTERVENTION PRIORITIES:")
            for i, priority in enumerate(assessment.intervention_priority, 1):
                print(f"   {i}. {priority}")
        
        print("\n" + "="*70)