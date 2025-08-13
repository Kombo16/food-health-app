# Food Health Risk Assessment System

A comprehensive system for analyzing food nutritional content, assessing health risks, and predicting lifestyle disease risks based on dietary patterns and user profiles.

## Features

- **Food Analysis**: Get detailed nutritional information for any food item
- **Risk Assessment**: Calculate health risk scores for individual foods
- **Lifestyle Assessment**: Predict risks for common lifestyle diseases (diabetes, hypertension, heart disease)
- **Dietary Recommendations**: Get personalized dietary recommendations
- **Database Integration**: Store and retrieve nutritional data efficiently
- **Multiple Data Sources**: USDA API and Wikipedia fallback for nutrition data

## System Architecture
   ```
   food-health-app/
    ├── backend/
    │   ├── app.py
    │   ├── main.py
    │   ├── config/
    │   │   ├── __init__.py
    │   │   ├── database.py
    │   │   └── settings.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── disease.py
    │   │   ├── nutrition.py
    │   │   └── user.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── database_service.py
    │   │   ├── disease_prediction_service.py
    │   │   ├── nutrition_service.py
    │   │   └── risk_assessment_service.py
    │   └── utils/
    │       ├── __init__.py
    │       ├── calculations.py
    │       ├── food_categorizer.py
    │       └── validators.py
    ├── frontend/
    │   ├── static/
    │   │   ├── css/
    │   │   │   └── organic2.css
    │   │   └── js/
    │   │       └── script.js
    │   └── templates/
    │       └── index.html
    ├── requirements.txt
    └── README.md
   ```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/food-health-app.git
   cd food-health-app
   ```

2. **Set up a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Set up environment variables**:

    - Create a .env file in the project root

        - Add your database credentials and USDA API key to the .env file:

        ```text
        DB_HOST=localhost
        DB_NAME=your_database_name
        DB_USER=your_database_username
        DB_PASSWORD=your_database_password
        DB_PORT=3306
        USDA_API_KEY=your_usda_api_key
        ```
5. **Initialize the database**:

    ```bash
    python app.py
    ```
## Usage:
### API Endpoints
- POST /api/analyze-foods - Analyze food items

- POST /api/lifestyle-assessment - Full lifestyle assessment

- GET /api/health - Check API health

- GET /api/get-food-info/<food_name> - Get food info

- GET /api/demo/<type> - Run demos

## Running the Application
1. Start the Flask development server:

    ```bash
    python app.py
    ```
The application will be available at http://localhost:5000

- Command Line Interface - For testing and development, you can use the CLI interface:

```bash
python main.py
```
## Technologies Used
- Python 3.1

- Flask (Web framework)

- MySQL (Database)

- USDA FoodData Central API (Nutrition data)

- Wikipedia API (Fallback nutrition data)



## Final Notes
Make sure to:

1. Create a proper .env file with your database credentials

2. Obtain a USDA API key from https://fdc.nal.usda.gov/api-key-signup.html

3. Set up your MySQL database before running the application

### For production deployment:

1. Consider using a production-grade WSGI server like Gunicorn

2. Set up proper database connection pooling

3. Implement proper security measures (HTTPS, input validation, etc.)

The project is now complete and ready for deployment or further development!
