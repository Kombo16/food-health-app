""" Database operations """
import json
from typing import Optional
from mysql.connector import Error

from config.database import get_db_connection, DB_CONFIG
from models.nutrition import NutritionInfo, RiskAssessment, DietaryPattern
from models.disease import DiseaseRisk
from models.user import UserProfile


class DatabaseService:
    """ Handles database operations for the Food Health App """
    def __init__(self):
        self.init_database() 

    def _safe_execute(self, cursor, query):
        """ Execute SQL query while handling errors """
        try:
            cursor.execute("SET sql_notes = 0;")
            cursor.execute(query)
            cursor.execute("SET sql_notes = 1;")
        except Error as e:
            if e.errno != 1050 or e.errno != 1007:
                raise

    def init_database(self):
        """ Initializes the database connection """
        connection = get_db_connection(use_database=False)
        if not connection:
            return
    
        cursor = connection.cursor()

        try:
            # Check if database exists
            cursor.execute(f"SHOW DATABASES LIKE '{DB_CONFIG['database']}'")
            if not cursor.fetchone():
                #Create database if it does not exist
                self._safe_execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            #Create all tables
            self._create_foods_table(cursor)
            self._create_risk_assessments_table(cursor)
            self._create_user_queries_table(cursor) 
            self._create_user_profiles_table(cursor)
            self._create_dietary_patterns_table(cursor)
            self._create_disease_assessments_table(cursor)
            connection.commit()
            print("Database initialized successfully!")

        except Error as e:
            if e.errno != 1007:
                print(f"Error initializing database: {e}")
        finally:
            cursor.close()
            connection.close()

    def _create_foods_table(self, cursor):
        """Create foods table"""
        self._safe_execute(cursor, '''
            CREATE TABLE IF NOT EXISTS foods (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                calories_per_100g DECIMAL(8,2),
                sugar_g DECIMAL(8,2),
                saturated_fat_g DECIMAL(8,2),
                sodium_mg DECIMAL(8,2),
                category VARCHAR(100),
                source VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_risk_assessments_table(self, cursor):
        """Create risk assessments table"""
        self._safe_execute(cursor, '''
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                food_name VARCHAR(255),
                risk_score DECIMAL(5,2),
                is_risky BOOLEAN,
                risk_factors TEXT,
                alternatives TEXT,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_user_queries_table(self, cursor):
        """Create user queries table"""
        self._safe_execute(cursor, '''
            CREATE TABLE IF NOT EXISTS user_queries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query VARCHAR(255),
                found_in_db BOOLEAN,
                found_in_api BOOLEAN,
                found_in_wikipedia BOOLEAN,
                user_provided_info BOOLEAN,
                queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_user_profiles_table(self, cursor):
        """Create user profiles table"""
        self._safe_execute(cursor, '''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age INT,
                gender VARCHAR(10),
                weight_kg DECIMAL(5,2),
                height_cm DECIMAL(5,2),
                activity_level VARCHAR(20),
                family_history TEXT,
                current_conditions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_dietary_patterns_table(self, cursor):
        """Create dietary patterns table"""
        self._safe_execute(cursor, '''
            CREATE TABLE IF NOT EXISTS dietary_patterns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                daily_foods TEXT,
                portion_sizes TEXT,
                meal_frequency INT,
                days_tracked INT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles(id)
            )
        ''')
    
    def _create_disease_assessments_table(self, cursor):
        """Create disease assessments table"""
        self._safe_execute(cursor, '''
            CREATE TABLE IF NOT EXISTS disease_assessments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                disease_name VARCHAR(100),
                risk_percentage DECIMAL(5,2),
                risk_level VARCHAR(20),
                contributing_factors TEXT,
                recommendations TEXT,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles(id)
            )
        ''')
    
    def get_food_from_db(self, food_name: str) -> Optional[NutritionInfo]:
        """Get food from database"""
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                SELECT name, calories_per_100g, sugar_g, saturated_fat_g, 
                       sodium_mg, category, source
                FROM foods 
                WHERE LOWER(name) = LOWER(%s)
            ''', (food_name,))
            
            result = cursor.fetchone()
            if result:
                return NutritionInfo(*result)
            return None
            
        except Error as e:
            print(f"Error querying database: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    def save_food_to_db(self, nutrition_info: NutritionInfo):
        """Save nutrition information to database"""
        connection = get_db_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO foods 
                (name, calories_per_100g, sugar_g, saturated_fat_g, sodium_mg, category, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                AS new
                ON DUPLICATE KEY UPDATE
                calories_per_100g = new.calories_per_100g,
                sugar_g = new.sugar_g,
                saturated_fat_g = new.saturated_fat_g,
                sodium_mg = new.sodium_mg,
                category = new.category,
                source = new.source;
            ''', (
                nutrition_info.food_name,
                nutrition_info.calories_per_100g,
                nutrition_info.sugar_g,
                nutrition_info.saturated_fat_g,
                nutrition_info.sodium_mg,
                nutrition_info.category,
                nutrition_info.source
            ))
            
            connection.commit()
            
        except Error as e:
            print(f"Error saving to database: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def save_risk_assessment(self, assessment: RiskAssessment):
        """Save risk assessment to database"""
        connection = get_db_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO risk_assessments 
                (food_name, risk_score, is_risky, risk_factors, alternatives)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                assessment.food_name,
                assessment.risk_score,
                assessment.is_risky,
                json.dumps(assessment.risk_factors),
                json.dumps(assessment.alternatives)
            ))
            
            connection.commit()
            
        except Error as e:
            print(f"Error saving risk assessment: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def save_user_profile(self, profile: UserProfile) -> int:
        """Save user profile to database and return user ID"""
        connection = get_db_connection()
        if not connection:
            return 0
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_profiles 
                (age, gender, weight_kg, height_cm, activity_level, family_history, current_conditions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                profile.age, profile.gender, profile.weight_kg, profile.height_cm,
                profile.activity_level, json.dumps(profile.family_history), 
                json.dumps(profile.current_conditions)
            ))
            
            connection.commit()
            return cursor.lastrowid
            
        except Error as e:
            print(f"Error saving user profile: {e}")
            return 0
        finally:
            cursor.close()
            connection.close()
    
    def save_dietary_pattern(self, pattern: DietaryPattern, user_id: int) -> bool:
        """Save dietary pattern for a specific user"""
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO dietary_patterns 
                (user_id, daily_foods, portion_sizes, meal_frequency, days_tracked)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                user_id, json.dumps(pattern.daily_foods), 
                json.dumps(pattern.portion_sizes_g), 
                pattern.meal_frequency, pattern.days_tracked
            ))
            
            connection.commit()
            return True
            
        except Error as e:
            print(f"Error saving dietary pattern: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def save_disease_assessment(self, user_id: int, risk: DiseaseRisk) -> bool:
        """Save disease assessment for a specific user"""
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO disease_assessments 
                (user_id, disease_name, risk_percentage, risk_level, contributing_factors, recommendations)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                user_id, risk.disease_name, risk.risk_percentage, risk.risk_level,
                json.dumps(risk.contributing_factors), json.dumps(risk.recommendations)
            ))
            
            connection.commit()
            return True
            
        except Error as e:
            print(f"Error saving disease assessment: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    def log_user_query(self, query: str, found_in_db: bool, found_in_api: bool, 
                      found_in_wikipedia: bool, user_provided_info: bool):
        """Log user query for learning purposes"""
        connection = get_db_connection()
        if not connection:
            return
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_queries 
                (query, found_in_db, found_in_api, found_in_wikipedia, user_provided_info)
                VALUES (%s, %s, %s, %s, %s)
            ''', (query, found_in_db, found_in_api, found_in_wikipedia, user_provided_info))
            
            connection.commit()
            
        except Error as e:
            print(f"Error logging query: {e}")
        finally:
            cursor.close()
            connection.close()