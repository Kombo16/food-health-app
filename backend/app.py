from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json 
import traceback
from datetime import datetime
from pathlib import Path
import os

#import modular components
from services.database_service import DatabaseService
from models.user import UserProfile
from models.nutrition import DietaryPattern
from services.nutrition_service import NutritionService
from services.risk_assessment_service import RiskAssessmentService
from services.disease_prediction_service import DiseasePredictionService
from utils.validators import InputValidator


BASE_DIR = Path(__file__).parent
# Define paths to templates and static folders
TEMPLATE_DIR = BASE_DIR.parent / 'frontend' / 'templates'
STATIC_DIR = BASE_DIR.parent / 'frontend' / 'static'

# Create folders if they don't exist
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Verify CSS and JS subdirectories exist
(STATIC_DIR / 'css').mkdir(exist_ok=True)
(STATIC_DIR / 'js').mkdir(exist_ok=True)

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
CORS(app)

#Initialize services
db_service = DatabaseService()
nutrition_service = NutritionService(db_service)
risk_service = RiskAssessmentService(db_service)
disease_service = DiseasePredictionService(nutrition_service, db_service)

#API Routs

@app.route('/')
def index():
    """ Serve the main HTML interface """
    try: 
        with open(TEMPLATE_DIR/'index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Food Health App</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                .result { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🍎 Food Health Risk Assessment</h1>
                <p>API is running! Use the endpoints to analyze foods and assess health risks.</p>
                <h3>Available Endpoints:</h3>
                <ul>
                    <li>POST /api/analyze-foods - Analyze food items</li>
                    <li>POST /api/lifestyle-assessment - Full lifestyle assessment</li>
                    <li>GET /api/health - Check API health</li>
                </ul>
            </div>
        </body>
        </html>
        """)
@app.route('/api/health', methods=['GET'])
def health_check():
    """ Check API health """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Food Health API is running'})

@app.route('/api/analyze-foods', methods=['POST'])
def analyze_foods_api():
    """ Analyze food items for nutritional information and risk assessment """
    try:
        data = request.get_json()

        if not data or 'foods' not in data:
            return jsonify({'error': 'Missing food parameter'}), 400
        
        is_valid, error_msg, cleaned_foods = InputValidator.validate_food_list(data['foods'])
        if not is_valid:
            return jsonify({'error': f'Validation error: {error_msg}'}), 400

        if not cleaned_foods:
            return jsonify({'error': 'No foods provided'}), 400
        
        results = []

        for food_name in cleaned_foods:
            #get nutrition information
            nutrition_info = nutrition_service.get_food_nutrition(food_name)
            if nutrition_info:
                risk_assessment = risk_service.calculate_risk_score(nutrition_info)
                results.append({
                    'food_name': food_name,
                    'nutrition': {
                        'name': nutrition_info.food_name,
                        'calories_per_100g': float(nutrition_info.calories_per_100g),
                        'sugar_g': float(nutrition_info.sugar_g),
                        'saturated_fat_g': float(nutrition_info.saturated_fat_g),
                        'sodium_mg': float(nutrition_info.sodium_mg),
                        'category': nutrition_info.category,
                        'source': nutrition_info.source
                    },
                    'risk_assessment': {
                        'risk_score': risk_assessment.risk_score,
                        'is_risky': risk_assessment.is_risky,
                        'risk_factors': risk_assessment.risk_factors,
                        'alternatives': risk_assessment.alternatives
                    }
                })
            else:
                results.append({
                    'food_name': food_name,
                    'nutrition': None,
                    'risk_assessment': None,
                    'error': 'Nutrition info not found'})

        return jsonify({
            'success': True,
            'results': results,
            'analyzed_at': datetime.now().isoformat()})

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()}), 500
@app.route('/api/lifestyle-assessment', methods=['POST'])
def lifestyle_assessent_api():
    """Perform lifestyle disease risk assessment"""
    try:
        data = request.get_json()
        
        # Validate user profile data
        is_valid, error_msg = InputValidator.validate_user_profile_data(data)
        if not is_valid:
            return jsonify({'error': f'Profile validation error: {error_msg}'}), 400
        
        # Validate dietary pattern data
        is_valid, error_msg = InputValidator.validate_dietary_pattern_data(data)
        if not is_valid:
            return jsonify({'error': f'Dietary validation error: {error_msg}'}), 400
        
        # Validate family history and current conditions
        family_history = data.get('family_history', [])
        is_valid, error_msg, clean_family_history = InputValidator.validate_health_conditions(family_history)
        if not is_valid:
            return jsonify({'error': f'Family history validation error: {error_msg}'}), 400
        
        current_conditions = data.get('current_conditions', [])
        is_valid, error_msg, clean_current_conditions = InputValidator.validate_health_conditions(current_conditions)
        if not is_valid:
            return jsonify({'error': f'Current conditions validation error: {error_msg}'}), 400
        
        # Create user profile
        user_profile = UserProfile(
            age=int(data['age']),
            gender=data['gender'],
            weight_kg=float(data['weight']),
            height_cm=float(data['height']),
            activity_level=data['activity_level'],
            family_history=data.get('family_history', []),
            current_conditions=data.get('current_conditions', [])
        )
        
        # Process and validate dietary pattern data
        is_valid, error_msg, cleaned_foods = InputValidator.validate_food_list(data['daily_foods'])
        if not is_valid:
            return jsonify({'error': f'Foods validation error: {error_msg}'}), 400
        
        portion_sizes = data['portion_sizes']
        if isinstance(portion_sizes, str):
            try:
                portion_sizes = [float(p.strip()) for p in portion_sizes.split(',') if p.strip()]
            except ValueError:
                return jsonify({'error': 'Invalid portion sizes format'}), 400
        elif isinstance(portion_sizes, list):
            try:
                portion_sizes = [float(p) for p in portion_sizes]
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid portion sizes values'}), 400
        # Ensure foods and portions match in length
        if len(cleaned_foods) != len(portion_sizes):
            # If lengths don't match, pad with default values or truncate
            min_length = min(len(cleaned_foods), len(portion_sizes))
            if min_length == 0:
                return jsonify({'error': 'No valid foods or portion sizes provided'}), 400
            
            cleaned_foods = cleaned_foods[:min_length]
            portion_sizes = portion_sizes[:min_length]
        
        # Remove any foods with zero or negative portion sizes
        valid_pairs = [(food, portion) for food, portion in zip(cleaned_foods, portion_sizes) 
                      if portion > 0 and food.strip()]
        
        if not valid_pairs:
            return jsonify({'error': 'No valid food and portion size pairs found'}), 400
        
        cleaned_foods, portion_sizes = zip(*valid_pairs)
        cleaned_foods = list(cleaned_foods)
        portion_sizes = list(portion_sizes)
        
        # Create dietary pattern using the DietaryPattern model structure
        dietary_pattern = DietaryPattern(
            daily_foods=cleaned_foods,
            portion_sizes_g=portion_sizes,
            meal_frequency=data.get('meal_frequency', 3),
            days_tracked=data.get('days_tracked', 1)
        )
        
        # Perform assessment
        assessment = disease_service.assess_lifestyle_disease_risk(user_profile, dietary_pattern)

        maintenance_calories = disease_service.health_calculator.calculate_daily_maintenance_calories(
            assessment.user_profile
        ) 
        # Analyze dietary intake
        dietary_analysis = disease_service.analyze_dietary_intake(dietary_pattern)
        
        # Format results with proper error handling
        result = {
            'success': True,
            'user_profile': {
                'age': assessment.user_profile.age,
                'gender': assessment.user_profile.gender,
                'weight_kg': assessment.user_profile.weight_kg,
                'height_cm': assessment.user_profile.height_cm,
                'activity_level': assessment.user_profile.activity_level,
                'family_history': assessment.user_profile.family_history,
                'current_conditions': assessment.user_profile.current_conditions,
                'maintenance_calories': maintenance_calories
            },
            'dietary_pattern': {
                'daily_foods': dietary_pattern.daily_foods,
                'portion_sizes_g': dietary_pattern.portion_sizes_g,
                'meal_frequency': dietary_pattern.meal_frequency,
                'days_tracked': dietary_pattern.days_tracked,
                'total_foods_analyzed': len(dietary_pattern.daily_foods)
            },
            'dietary_analysis': {
                'calories': dietary_analysis.get('calories', 0),
                'sugar_g': dietary_analysis.get('sugar_g', 0),
                'saturated_fat_g': dietary_analysis.get('saturated_fat_g', 0),
                'sodium_mg': dietary_analysis.get('sodium_mg', 0)
            },
            'disease_risks': [
                {
                    'disease_name': risk.disease_name,
                    'risk_percentage': risk.risk_percentage,
                    'risk_level': risk.risk_level,
                    'contributing_factors': risk.contributing_factors,
                    'recommendations': risk.recommendations
                }
                for risk in assessment.disease_risks
            ],
            'overall_risk_score': assessment.overall_risk_score,
            'key_dietary_factors': assessment.key_dietary_factors,
            'intervention_priority': assessment.intervention_priority,
            'assessed_at': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Data validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/get-food-info/<food_name>', methods=['GET'])
def get_food_info(food_name):
    """Get nutrition information for a specific food"""
    try:
        is_valid, error_msg = InputValidator.validate_food_name(food_name)
        if not is_valid:
            return jsonify({'success': False,
                            'error': f'Invalid food name: {error_msg}'}), 400
        nutrition_info = nutrition_service.get_food_nutrition(food_name.strip().lower())
        
        if nutrition_info:
            return jsonify({
                'success': True,
                'nutrition': {
                    'name': nutrition_info.food_name,
                    'calories_per_100g': float(nutrition_info.calories_per_100g),
                    'sugar_g': float(nutrition_info.sugar_g),
                    'saturated_fat_g': float(nutrition_info.saturated_fat_g),
                    'sodium_mg': float(nutrition_info.sodium_mg),
                    'category': nutrition_info.category,
                    'source': nutrition_info.source
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Nutrition data not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/demo/<demo_type>', methods=['GET'])
def demo_endpoint(demo_type):
    """Run demo scenarios"""
    try:
        if demo_type == 'healthy':
            foods = ['apple']
        elif demo_type == 'unhealthy':
            foods = ['pizza']
        elif demo_type == 'mixed':
            foods = ['apple', 'hamburger']
        elif demo_type == 'junk':
            foods = ['french fries', 'ice cream', 'coca cola']
        else:
            return jsonify({'error': 'Invalid demo type'}), 400
        
        # Analyze the demo foods
        results = risk_service.analyze_foods(foods, nutrition_service)
        
        demo_results = []
        for food_name, assessment in results.items():
            # Get nutrition info for this food
            nutrition_info = nutrition_service.get_food_nutrition(food_name)
            
            if nutrition_info:
                demo_results.append({
                    'food_name': food_name,
                    'nutrition': {
                        'name': nutrition_info.food_name,
                        'calories_per_100g': float(nutrition_info.calories_per_100g),
                        'sugar_g': float(nutrition_info.sugar_g),
                        'saturated_fat_g': float(nutrition_info.saturated_fat_g),
                        'sodium_mg': float(nutrition_info.sodium_mg),
                        'category': nutrition_info.category,
                        'source': nutrition_info.source
                    },
                    'risk_assessment': {
                        'risk_score': assessment.risk_score,
                        'is_risky': assessment.is_risky,
                        'risk_factors': assessment.risk_factors,
                        'alternatives': assessment.alternatives
                    }
                })
        
        return jsonify({
            'success': True,
            'demo_type': demo_type,
            'results': demo_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/api/nutrition-stats', methods=['GET'])
def nutrition_stats():
    stats = nutrition_service.get_stats()
    return jsonify(stats)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request - Please check your input data'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(422)
def validation_error(error):
    return jsonify({'error': 'Validation error - Invalid input format'}), 422

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    
    print("Food Health API Server Starting...")
    print("Available endpoints:")
    print("  - GET  /                    - Main interface")
    print("  - GET  /api/health          - Health check")
    print("  - POST /api/analyze-foods   - Analyze foods")
    print("  - POST /api/lifestyle-assessment - Lifestyle assessment")
    print("  - GET  /api/get-food-info/<food> - Get food info")
    print("  - GET  /api/demo/<type>     - Run demos")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)   