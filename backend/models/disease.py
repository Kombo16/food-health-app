""" Disease-related data models """

from dataclasses import dataclass
from typing import List, Dict
from .user import UserProfile
from .nutrition import DietaryPattern

@dataclass
class DiseaseRisk:
    """ Represents the risk of a disease based on user profile and dietary pattern """
    disease_name: str
    risk_percentage: float
    risk_level: str
    contributing_factors: List[str]
    recommendations: List[str]

@dataclass
class LifestyleDiseaseAssessment:
    """ Represents a comprehensive assessment of lifestyle diseases """
    user_profile: UserProfile
    dietary_pattern: DietaryPattern
    disease_risks: List[DiseaseRisk]
    overall_risk_score: float
    key_dietary_factors: Dict[str, float]
    intervention_priority: List[str]
