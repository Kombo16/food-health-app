const API_BASE_URL = 'http://localhost:5000/api';

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
            
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
            
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
            
    // Add active class to corresponding nav button
    event.target.classList.add('active');
}

function setDemoFoods(foods) {
    document.getElementById('food-input').value = foods;
}

function updateDietaryDays() {
    const daysTracked = parseInt(document.getElementById('days-tracked').value);
    const container = document.getElementById('daily-tracking-container');
            
    let html = '';
    for (let day = 1; day <= daysTracked; day++) {
        html += `
            <div class="day-tracking" style="margin: 20px 0; padding: 20px; background: var(--bg); border-radius: 4px; border-left: 4px solid var(--primary); box-shadow: var(--shadow);">
                <h4 style="color: var(--primary-dark); margin-bottom: 15px; font-weight: 600;">Day ${day}</h4>
                <div class="form-group">
                    <label for="day-${day}-foods" style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--primary-dark);">Foods consumed (comma-separated):</label>
                    <textarea id="day-${day}-foods" rows="2" style="width: 100%; padding: 12px 15px; border: 1px solid var(--border); border-radius: 4px; font-size: 1rem; font-family: 'Merriweather', Georgia, serif; min-height: 80px; resize: vertical;" placeholder="rice, chicken breast, broccoli, apple, milk"></textarea>
                </div>
                <div class="form-group">
                    <label for="day-${day}-portions" style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--primary-dark);">Portion sizes in grams (comma-separated):</label>
                    <input type="text" id="day-${day}-portions" style="width: 100%; padding: 12px 15px; border: 1px solid var(--border); border-radius: 4px; font-size: 1rem; font-family: 'Merriweather', Georgia, serif;" placeholder="200, 150, 100, 120, 250">
                </div>
            </div>
        `;
    }        
    container.innerHTML = html;
}

function showError(container, message) {
    container.innerHTML = `
        <div class="error-message">
            <h4>❌ Error</h4>
            <p>${message}</p>
        </div>
    `;
}

function showLoading(container, message) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
    `;
}

async function analyzeFoods() {
    const input = document.getElementById('food-input').value.trim();
    if (!input) {
        alert('Please enter foods to analyze');
        return;
    }
            
    const resultsContainer = document.getElementById('food-results');
    const foods = input.split(',').map(f => f.trim());
            
    showLoading(resultsContainer, 'Analyzing your foods...');
            
    try {
        const response = await fetch(`${API_BASE_URL}/analyze-foods`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ foods: foods })
        });        
        const data = await response.json();
                
        if (data.success) {
            displayFoodResults(data.results);
        } else {
            showError(resultsContainer, data.error || 'Failed to analyze foods');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(resultsContainer, 'Failed to connect to the server. Please make sure the Flask backend is running.');
    }
}

// Update the displayFoodResults function to use artisan style classes
function displayFoodResults(results) {
    const resultsContainer = document.getElementById('food-results');
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No results to display.</p>';
        return;
    }

    // Define risk level styles based on artisan theme
    const riskStyles = {
        low: {
            class: 'risk-low',
            color: '#2a9d8f', // success color
            bg: 'rgba(42, 157, 143, 0.1)'
        },
        medium: {
            class: 'risk-medium',
            color: '#e9c46a', // warning color
            bg: 'rgba(233, 196, 106, 0.1)'
        },
        high: {
            class: 'risk-high',
            color: '#e76f51', // danger color
            bg: 'rgba(231, 111, 81, 0.1)'
        }
    };

    let html = `
        <div class="results-container">
            <h3 style="text-align: center; font-style: italic; color: var(--primary-dark); border-bottom: 1px dashed var(--border); padding-bottom: 10px; margin-bottom: 25px;">
                Analysis Results
            </h3>
    `;
            
    results.forEach(result => {
        if (result.nutrition) {
            const riskLevel = getRiskLevel(result.risk_assessment.risk_score);
            const style = riskStyles[riskLevel.class.replace('risk-', '')];
            
            html += `
                <div class="food-result" style="margin-bottom: 25px; padding: 20px; background: white; border-radius: 4px; border: 1px solid var(--border); box-shadow: var(--shadow);">
                    <div class="food-name" style="font-size: 1.3rem; font-weight: 600; color: var(--primary-dark); margin-bottom: 15px;">
                        ${result.nutrition.name}
                    </div>        
                    
                    <div class="nutrition-info" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.calories_per_100g.toFixed(0)}
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Calories
                            </div>
                        </div>
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.sugar_g.toFixed(1)}g
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Sugar
                            </div>
                        </div>
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.saturated_fat_g.toFixed(1)}g
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Sat Fat
                            </div>
                        </div>
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.sodium_mg.toFixed(0)}mg
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Sodium
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin: 15px 0; padding: 10px; background: ${style.bg}; border-radius: 4px; border-left: 4px solid ${style.color};">
                        <span style="font-weight: 600; color: ${style.color};">
                            ${riskLevel.level.toUpperCase()} Risk (Score: ${result.risk_assessment.risk_score})
                        </span>
                        <span style="margin-left: 10px; color: var(--text-light); font-size: 0.9rem;">
                            Source: ${result.nutrition.source}
                        </span>
                    </div>
                    
                    ${Object.keys(result.risk_assessment.risk_factors).length > 0 ? `
                        <div style="margin: 15px 0; padding: 15px; background: var(--bg); border-radius: 4px;">
                            <strong style="color: var(--primary-dark);">Risk Factors:</strong> 
                            <ul style="margin-top: 8px; list-style-type: disc; padding-left: 20px;">
                                ${Object.entries(result.risk_assessment.risk_factors).map(([factor, level]) => 
                                    `<li style="margin-bottom: 5px;">${factor}: <span style="font-weight: 600;">${level}</span></li>`
                                ).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${result.risk_assessment.alternatives.length > 0 ? `
                        <div class="alternatives" style="margin: 20px 0 10px; padding: 15px; background: rgba(42, 157, 143, 0.1); border-radius: 4px; border-left: 4px solid var(--success);">
                            <h4 style="color: var(--success); font-weight: 600; margin-bottom: 10px;">
                                🌱 Healthier Alternatives:
                            </h4>
                            <div class="alternatives-list" style="display: flex; flex-wrap: wrap; gap: 8px;">
                                ${result.risk_assessment.alternatives.map(alt => `
                                    <span class="alternative-item" style="padding: 6px 12px; background: white; border-radius: 4px; border: 1px solid var(--success); color: var(--success); font-size: 0.9rem;">
                                        ${alt}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        } else {
            html += `
                <div class="food-result" style="margin-bottom: 25px; padding: 20px; background: white; border-radius: 4px; border: 1px solid var(--border); box-shadow: var(--shadow);">
                    <div class="food-name" style="font-size: 1.3rem; font-weight: 600; color: var(--danger);">
                        ${result.food_name}
                    </div>
                    <p style="color: var(--text-light); margin-top: 10px;">
                        ❌ ${result.error || 'Nutrition data not found for this food item.'}
                    </p>
                </div>
            `;
        }
    });
            
    // Add summary
    const foundResults = results.filter(r => r.nutrition);
    const riskyFoods = foundResults.filter(r => r.risk_assessment && r.risk_assessment.is_risky);
    const safeFoods = foundResults.filter(r => r.risk_assessment && !r.risk_assessment.is_risky);
            
    html += `
        <div style="margin-top: 30px; padding: 20px; background: var(--bg); border-radius: 4px; border: 1px solid var(--border);">
            <h4 style="color: var(--primary-dark); font-weight: 600; margin-bottom: 15px; text-align: center;">
                📊 Summary
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; text-align: center;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">${foundResults.length}</div>
                    <div style="color: var(--text-light);">Total foods</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: var(--danger);">${riskyFoods.length}</div>
                    <div style="color: var(--text-light);">Risky foods</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: var(--success);">${safeFoods.length}</div>
                    <div style="color: var(--text-light);">Safe foods</div>
                </div>
            </div>
        </div>
    `;
            
    html += '</div>';
    resultsContainer.innerHTML = html;
}
function getRiskLevel(riskScore) {
    if (riskScore === 0) return { level: 'low', class: 'risk-low' };
    if (riskScore < 3) return { level: 'medium', class: 'risk-medium' };
    return { level: 'high', class: 'risk-high' };
}

async function assessLifestyleRisk() {
    // Get basic form values
    const age = parseInt(document.getElementById('age').value);
    const gender = document.getElementById('gender').value;
    const weight = parseFloat(document.getElementById('weight').value);
    const height = parseFloat(document.getElementById('height').value);
    const activity = document.getElementById('activity').value;
    const familyHistoryInput = document.getElementById('family-history').value.trim();
    const currentConditionsInput = document.getElementById('current-conditions').value.trim();
    const daysTracked = parseInt(document.getElementById('days-tracked').value);
    const mealFrequency = parseInt(document.getElementById('meal-frequency').value);
    
    // Basic validation
    if (!age || !weight || !height) {
        alert('Please fill in age, weight, and height');
        return;
    }
    
    // Collect daily dietary data
    const dailyDiets = [];
    let hasValidData = false;
    
    for (let day = 1; day <= daysTracked; day++) {
        const foodsInput = document.getElementById(`day-${day}-foods`);
        const portionsInput = document.getElementById(`day-${day}-portions`);
        
        if (!foodsInput || !portionsInput) {
            alert(`Missing input fields for day ${day}`);
            return;
        }
        
        const foodsText = foodsInput.value.trim();
        const portionsText = portionsInput.value.trim();
        
        if (foodsText && portionsText) {
            const foods = foodsText.split(',').map(f => f.trim()).filter(f => f);
            const portions = portionsText.split(',').map(p => parseFloat(p.trim())).filter(p => !isNaN(p) && p > 0);
            
            if (foods.length > 0 && portions.length > 0) {
                // Ensure equal length by padding or truncating
                const minLength = Math.min(foods.length, portions.length);
                dailyDiets.push({
                    day: day,
                    foods: foods.slice(0, minLength),
                    portions: portions.slice(0, minLength)
                });
                hasValidData = true;
            }
        }
    }
    
    if (!hasValidData) {
        alert('Please enter food and portion data for at least one day');
        return;
    }
    
    // Flatten all foods and portions into single arrays (as expected by the backend)
    const allFoods = [];
    const allPortions = [];
    
    dailyDiets.forEach(dayData => {
        allFoods.push(...dayData.foods);
        allPortions.push(...dayData.portions);
    });
    
    const familyHistory = familyHistoryInput ? familyHistoryInput.split(',').map(s => s.trim()).filter(s => s) : [];
    const currentConditions = currentConditionsInput ? currentConditionsInput.split(',').map(s => s.trim()).filter(s => s) : [];
    
    const resultsContainer = document.getElementById('lifestyle-results');
    showLoading(resultsContainer, 'Assessing your health risks...');
    
    try {
        const requestData = {
            age: age,
            gender: gender,
            weight: weight,
            height: height,
            activity_level: activity,
            family_history: familyHistory,
            current_conditions: currentConditions,
            daily_foods: allFoods,
            portion_sizes: allPortions,
            meal_frequency: mealFrequency,
            days_tracked: daysTracked
        };
        
        console.log('Sending request data:', requestData); // Debug log
        
        const response = await fetch(`${API_BASE_URL}/lifestyle-assessment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayLifestyleResults(data);
        } else {
            showError(resultsContainer, data.error || 'Failed to assess health risks');
            console.error('Backend error:', data);
        }
    } catch (error) {
        console.error('Error:', error);
        showError(resultsContainer, 'Failed to connect to the server. Please make sure the Flask backend is running.');
    }
}

function displayLifestyleResults(assessment) {
    const resultsContainer = document.getElementById('lifestyle-results');
    
    const overallRisk = assessment.overall_risk_score * 100;
    const overallRiskClass = getRiskLevelFromPercentage(overallRisk);
    
    // Define risk level styles
    const riskStyles = {
        low: {
            color: '#2a9d8f', // success
            bg: 'rgba(42, 157, 143, 0.1)',
            emoji: '✅'
        },
        moderate: {
            color: '#e9c46a', // warning
            bg: 'rgba(233, 196, 106, 0.1)',
            emoji: '⚠️'
        },
        high: {
            color: '#e76f51', // danger
            bg: 'rgba(231, 111, 81, 0.1)',
            emoji: '🚨'
        },
        very_high: {
            color: '#c53030', // darker red
            bg: 'rgba(197, 48, 48, 0.1)',
            emoji: '🔴'
        }
    };
    
    const currentRiskStyle = riskStyles[overallRiskClass];
    
    let html = `
        <div class="results-container">
            <div class="profile-summary" style="padding: 20px; background: white; border-radius: 4px; border: 1px solid var(--border); box-shadow: var(--shadow);">
                <h3 style="color: var(--primary-dark); font-weight: 600; margin-bottom: 15px; text-align: center; border-bottom: 1px dashed var(--border); padding-bottom: 10px;">
                    👤 Your Health Profile
                </h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; text-align: center;">
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">${assessment.user_profile.age}</div>
                        <div style="color: var(--text-light);">Age</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">${(assessment.user_profile.weight_kg / Math.pow(assessment.user_profile.height_cm / 100, 2)).toFixed(1)}</div>
                        <div style="color: var(--text-light);">BMI</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">${assessment.user_profile.activity_level.replace('_', ' ')}</div>
                        <div style="color: var(--text-light);">Activity</div>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 25px 0; padding: 25px; background: ${currentRiskStyle.bg}; border-radius: 4px; border-left: 4px solid ${currentRiskStyle.color};">
                <h3 style="color: var(--primary-dark); font-weight: 600; margin-bottom: 15px;">
                    Overall Lifestyle Disease Risk
                </h3>
                <div style="font-size: 3rem; font-weight: 900; margin: 10px 0; color: ${currentRiskStyle.color};">
                    ${currentRiskStyle.emoji} ${overallRisk.toFixed(1)}%
                </div>
                <div style="font-size: 1.2rem; text-transform: uppercase; color: ${currentRiskStyle.color}; font-weight: 600;">
                    ${overallRiskClass.replace('_', ' ')} Risk
                </div>
            </div>
            
            <h3 style="color: var(--primary-dark); font-weight: 600; margin: 25px 0 15px; text-align: center; border-bottom: 1px dashed var(--border); padding-bottom: 10px;">
                🔍 Individual Disease Risks
            </h3>
    `;
    
    assessment.disease_risks.forEach(risk => {
        const riskStyle = riskStyles[risk.risk_level];
        
        html += `
            <div class="disease-risk-card" style="margin-bottom: 20px; padding: 20px; background: white; border-radius: 4px; border: 1px solid var(--border); box-shadow: var(--shadow);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 1.2rem; font-weight: 600; color: ${riskStyle.color};">
                        ${riskStyle.emoji} ${risk.disease_name}
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: ${riskStyle.color};">
                        ${risk.risk_percentage.toFixed(1)}%
                    </div>
                </div>
                <div style="text-transform: uppercase; font-weight: 600; color: ${riskStyle.color}; margin-bottom: 15px; text-align: center;">
                    ${risk.risk_level.replace('_', ' ')} Risk
                </div>
                
                ${risk.contributing_factors.length > 0 ? `
                    <div style="margin-bottom: 15px;">
                        <strong style="color: var(--primary-dark);">Contributing Factors:</strong>
                        <ul style="margin-top: 8px; list-style-type: disc; padding-left: 20px;">
                            ${risk.contributing_factors.map(factor => `<li style="margin-bottom: 5px;">${factor}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div>
                    <strong style="color: var(--primary-dark);">Recommendations:</strong>
                    <ul style="margin-top: 8px; list-style-type: disc; padding-left: 20px;">
                        ${risk.recommendations.slice(0, 3).map(rec => `<li style="margin-bottom: 5px;">${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    });
    
    // Daily intake summary
    html += `
        <div style="margin-top: 30px; padding: 20px; background: var(--bg); border-radius: 4px; border: 1px solid var(--border);">
            <h4 style="color: var(--primary-dark); font-weight: 600; margin-bottom: 15px; text-align: center; border-bottom: 1px dashed var(--border); padding-bottom: 10px;">
                🍽️ Your Daily Intake vs Recommendations
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 15px;">
                <div style="background: white; padding: 15px; border-radius: 4px; text-align: center; border: 1px solid var(--border);">
                    <div style="font-size: 1.3rem; font-weight: bold; color: ${assessment.dietary_analysis.calories > assessment.user_profile.maintenance_calories + 200 ? 'var(--danger)' : 'var(--success)'};">
                        ${assessment.dietary_analysis.calories.toFixed(0)}
                    </div>
                    <div style="color: var(--text-light);">Calories</div>
                    <div style="font-size: 0.9rem; color: var(--text-light);">
                        Target: ${assessment.user_profile.maintenance_calories.toFixed(0)}
                    </div>
                </div>
                <div style="background: white; padding: 15px; border-radius: 4px; text-align: center; border: 1px solid var(--border);">
                    <div style="font-size: 1.3rem; font-weight: bold; color: ${assessment.dietary_analysis.sugar_g > 50 ? 'var(--danger)' : 'var(--success)'};">
                        ${assessment.dietary_analysis.sugar_g.toFixed(1)}g
                    </div>
                    <div style="color: var(--text-light);">Sugar</div>
                    <div style="font-size: 0.9rem; color: var(--text-light);">
                        Limit: <50g
                    </div>
                </div>
                <div style="background: white; padding: 15px; border-radius: 4px; text-align: center; border: 1px solid var(--border);">
                    <div style="font-size: 1.3rem; font-weight: bold; color: ${assessment.dietary_analysis.saturated_fat_g > 13 ? 'var(--danger)' : 'var(--success)'};">
                        ${assessment.dietary_analysis.saturated_fat_g.toFixed(1)}g
                    </div>
                    <div style="color: var(--text-light);">Sat Fat</div>
                    <div style="font-size: 0.9rem; color: var(--text-light);">
                        Limit: <13g
                    </div>
                </div>
                <div style="background: white; padding: 15px; border-radius: 4px; text-align: center; border: 1px solid var(--border);">
                    <div style="font-size: 1.3rem; font-weight: bold; color: ${assessment.dietary_analysis.sodium_mg > 2300 ? 'var(--danger)' : 'var(--success)'};">
                        ${assessment.dietary_analysis.sodium_mg.toFixed(0)}mg
                    </div>
                    <div style="color: var(--text-light);">Sodium</div>
                    <div style="font-size: 0.9rem; color: var(--text-light);">
                        Limit: <2300mg
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Dietary tracking summary
    html += `
        <div style="margin-top: 25px; padding: 20px; background: white; border-radius: 4px; border: 1px solid var(--border);">
            <h4 style="color: var(--primary-dark); font-weight: 600; margin-bottom: 15px; text-align: center; border-bottom: 1px dashed var(--border); padding-bottom: 10px;">
                📊 Dietary Tracking Summary
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; text-align: center;">
                <div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: var(--primary);">${assessment.dietary_pattern.days_tracked}</div>
                    <div style="color: var(--text-light);">Days Tracked</div>
                </div>
                <div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: var(--primary);">${assessment.dietary_pattern.total_foods_analyzed}</div>
                    <div style="color: var(--text-light);">Foods Analyzed</div>
                </div>
                <div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: var(--primary);">${assessment.dietary_pattern.meal_frequency}</div>
                    <div style="color: var(--text-light);">Meals/Day</div>
                </div>
            </div>
        </div>
    `;
    
    // Intervention priorities
    if (assessment.intervention_priority && assessment.intervention_priority.length > 0) {
        html += `
            <div style="margin-top: 25px; padding: 20px; background: rgba(231, 111, 81, 0.1); border-radius: 4px; border-left: 4px solid var(--danger);">
                <h4 style="color: var(--danger); font-weight: 600; margin-bottom: 15px;">
                    🎯 Priority Actions
                </h4>
                <ul style="margin-top: 15px;">
                    ${assessment.intervention_priority.map(intervention => `
                        <li style="margin: 8px 0; padding: 8px 0; border-bottom: 1px solid rgba(231, 111, 81, 0.3);">
                            🔹 ${intervention}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

function getRiskLevelFromPercentage(percentage) {
    if (percentage < 20) return 'low';
    if (percentage < 40) return 'moderate';
    if (percentage < 70) return 'high';
    return 'very_high';
}

async function runDemo(type) {
    const demoContainer = document.getElementById('demo-results');
    showLoading(demoContainer, `Running ${type} demo...`);
    
    try {
        const response = await fetch(`${API_BASE_URL}/demo/${type}`);
        const data = await response.json();
        
        if (data.success) {
            displayDemoResults(data);
        } else {
            showError(demoContainer, data.error || 'Failed to run demo');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(demoContainer, 'Failed to connect to the server.');
    }
}

function displayDemoResults(data) {
    const demoContainer = document.getElementById('demo-results');
    
    // Define the same risk styles as in displayFoodResults
    const riskStyles = {
        low: {
            class: 'risk-low',
            color: '#2a9d8f',
            bg: 'rgba(42, 157, 143, 0.1)'
        },
        medium: {
            class: 'risk-medium',
            color: '#e9c46a',
            bg: 'rgba(233, 196, 106, 0.1)'
        },
        high: {
            class: 'risk-high',
            color: '#e76f51',
            bg: 'rgba(231, 111, 81, 0.1)'
        }
    };

    let html = `
        <div class="results-container">
            <h3 style="text-align: center; font-style: italic; color: var(--primary-dark); border-bottom: 1px dashed var(--border); padding-bottom: 10px; margin-bottom: 25px;">
                ${data.demo_type.charAt(0).toUpperCase() + data.demo_type.slice(1)} Demo Results
            </h3>
    `;
    
    data.results.forEach(result => {
        if (result.nutrition) {
            const riskLevel = getRiskLevel(result.risk_assessment.risk_score);
            const style = riskStyles[riskLevel.class.replace('risk-', '')];
            
            html += `
                <div class="food-result" style="margin-bottom: 25px; padding: 20px; background: white; border-radius: 4px; border: 1px solid var(--border); box-shadow: var(--shadow);">
                    <div class="food-name" style="font-size: 1.3rem; font-weight: 600; color: var(--primary-dark); margin-bottom: 15px;">
                        ${result.nutrition.name}
                    </div>
                    
                    <div class="nutrition-info" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.calories_per_100g.toFixed(0)}
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Calories
                            </div>
                        </div>
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.sugar_g.toFixed(1)}g
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Sugar
                            </div>
                        </div>
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.saturated_fat_g.toFixed(1)}g
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Sat Fat
                            </div>
                        </div>
                        <div class="nutrition-item" style="text-align: center; padding: 10px; background: var(--bg); border-radius: 4px;">
                            <div class="nutrition-value" style="font-size: 1.2rem; font-weight: 700; color: var(--primary);">
                                ${result.nutrition.sodium_mg.toFixed(0)}mg
                            </div>
                            <div class="nutrition-label" style="font-size: 0.9rem; color: var(--text-light);">
                                Sodium
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin: 15px 0; padding: 10px; background: ${style.bg}; border-radius: 4px; border-left: 4px solid ${style.color};">
                        <span style="font-weight: 600; color: ${style.color};">
                            ${riskLevel.level.toUpperCase()} Risk (Score: ${result.risk_assessment.risk_score})
                        </span>
                    </div>
                    
                    ${Object.keys(result.risk_assessment.risk_factors).length > 0 ? `
                        <div style="margin: 15px 0; padding: 15px; background: var(--bg); border-radius: 4px;">
                            <strong style="color: var(--primary-dark);">Risk Factors:</strong> 
                            <ul style="margin-top: 8px; list-style-type: disc; padding-left: 20px;">
                                ${Object.entries(result.risk_assessment.risk_factors).map(([factor, level]) => 
                                    `<li style="margin-bottom: 5px;">${factor}: <span style="font-weight: 600;">${level}</span></li>`
                                ).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${result.risk_assessment.alternatives.length > 0 ? `
                        <div class="alternatives" style="margin: 20px 0 10px; padding: 15px; background: rgba(42, 157, 143, 0.1); border-radius: 4px; border-left: 4px solid var(--success);">
                            <h4 style="color: var(--success); font-weight: 600; margin-bottom: 10px;">
                                🌱 Healthier Alternatives:
                            </h4>
                            <div class="alternatives-list" style="display: flex; flex-wrap: wrap; gap: 8px;">
                                ${result.risk_assessment.alternatives.map(alt => `
                                    <span class="alternative-item" style="padding: 6px 12px; background: white; border-radius: 4px; border: 1px solid var(--success); color: var(--success); font-size: 0.9rem;">
                                        ${alt}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
    });
    
    html += '</div>';
    demoContainer.innerHTML = html;
}

// Check if server is running on page load
window.addEventListener('load', async function() {
    updateDietaryDays();
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Connected to Flask backend successfully');
        } else {
            console.warn('⚠️ Flask backend responded with error');
        }
    } catch (error) {
        console.warn('⚠️ Could not connect to Flask backend. Make sure it\'s running on http://localhost:5000');
    }
});