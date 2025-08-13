""" User-related data models """

from dataclasses import dataclass
from typing import List

@dataclass
class UserProfile:
    """ Represents a user's profile including personal and health information """
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    activity_level: str
    family_history: List[str] 
    current_conditions: List[str]