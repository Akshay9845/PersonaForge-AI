"""
Enhanced Persona Schema
Defines the structure for rich, visualization-ready persona data.
Based on the Lucas Mellor example with Reddit-specific enhancements.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class PersonaMotivations:
    """Motivation scores for different aspects."""
    convenience: int = 0
    wellness: int = 0
    speed: int = 0
    preferences: int = 0
    comfort: int = 0
    dietary_needs: int = 0
    privacy: int = 0
    community: int = 0
    learning: int = 0
    entertainment: int = 0

@dataclass
class PersonaPersonality:
    """MBTI-style personality spectrum scores."""
    introvert: int = 50
    extrovert: int = 50
    intuition: int = 50
    sensing: int = 50
    feeling: int = 50
    thinking: int = 50
    perceiving: int = 50
    judging: int = 50

class EnhancedPersona:
    """Enhanced persona with rich, structured data for visualization."""
    
    def __init__(self, username: str):
        self.username = username
        self.name = self._generate_name(username)
        self.age = None
        self.gender = None
        self.occupation = None
        self.status = None
        self.location = None
        self.tier = "Reddit User"
        self.archetype = None
        self.traits = []
        self.motivations = PersonaMotivations()
        self.personality = PersonaPersonality()
        self.behavior_habits = []
        self.frustrations = []
        self.goals = []
        self.quote = ""
        self.avatar_url = None
        self.personality_type = "XXXX"
        self.reddit_user = f"u/{username}"
        self.analysis_score = 0
        self.data_sources = []
        self.interests = []
        self.writing_style = {}
        self.social_views = []
        self.activity_patterns = {}
        self.citations = []
        self.metadata = {
            "generated_at": datetime.now().isoformat(),
            "source": "reddit",
            "confidence_overall": 0.0
        }
    
    def _generate_name(self, username: str) -> str:
        """Use the Reddit username as the name."""
        return username
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "occupation": self.occupation,
            "status": self.status,
            "location": self.location,
            "tier": self.tier,
            "archetype": self.archetype,
            "traits": self.traits,
            "motivations": {
                "convenience": self.motivations.convenience,
                "wellness": self.motivations.wellness,
                "speed": self.motivations.speed,
                "preferences": self.motivations.preferences,
                "comfort": self.motivations.comfort,
                "dietary_needs": self.motivations.dietary_needs,
                "privacy": self.motivations.privacy,
                "community": self.motivations.community,
                "learning": self.motivations.learning,
                "entertainment": self.motivations.entertainment
            },
            "personality": {
                "introvert": self.personality.introvert,
                "extrovert": self.personality.extrovert,
                "intuition": self.personality.intuition,
                "sensing": self.personality.sensing,
                "feeling": self.personality.feeling,
                "thinking": self.personality.thinking,
                "perceiving": self.personality.perceiving,
                "judging": self.personality.judging
            },
            "behavior_habits": self.behavior_habits,
            "frustrations": self.frustrations,
            "goals": self.goals,
            "quote": self.quote,
            "avatar_url": self.avatar_url,
            "personality_type": self.personality_type,
            "reddit_user": self.reddit_user,
            "analysis_score": self.analysis_score,
            "data_sources": self.data_sources,
            "interests": self.interests,
            "writing_style": self.writing_style,
            "social_views": self.social_views,
            "activity_patterns": self.activity_patterns,
            "citations": self.citations,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def calculate_analysis_score(self) -> float:
        """Calculate overall analysis confidence score."""
        factors = []
        
        # Data availability
        if self.data_sources:
            factors.append(min(len(self.data_sources) / 10, 1.0))
        else:
            factors.append(0.1)
        
        # Personality completeness
        if self.personality_type != "XXXX":
            factors.append(0.8)
        else:
            factors.append(0.3)
        
        # Trait richness
        if self.traits:
            factors.append(min(len(self.traits) / 5, 1.0))
        else:
            factors.append(0.2)
        
        # Quote quality
        if self.quote and len(self.quote) > 20:
            factors.append(0.9)
        else:
            factors.append(0.3)
        
        # Motivation completeness
        motivation_scores = [
            self.motivations.convenience,
            self.motivations.wellness,
            self.motivations.speed,
            self.motivations.preferences,
            self.motivations.comfort,
            self.motivations.dietary_needs
        ]
        if any(score > 0 for score in motivation_scores):
            factors.append(0.7)
        else:
            factors.append(0.2)
        
        self.analysis_score = sum(factors) / len(factors) * 100
        return self.analysis_score

def create_sample_persona() -> EnhancedPersona:
    """Create a sample persona for testing."""
    persona = EnhancedPersona("lucas_mellor")
    persona.age = 31
    persona.gender = "Male"
    persona.occupation = "Content Manager"
    persona.status = "Single"
    persona.location = "London, UK"
    persona.tier = "Early Adopter"
    persona.archetype = "The Creator"
    persona.traits = ["Practical", "Adaptable", "Spontaneous", "Active"]
    persona.motivations = PersonaMotivations(
        convenience=80,
        wellness=65,
        speed=60,
        preferences=40,
        comfort=50,
        dietary_needs=85
    )
    persona.personality = PersonaPersonality(
        introvert=60,
        extrovert=40,
        intuition=30,
        sensing=70,
        feeling=15,
        thinking=85,
        perceiving=60,
        judging=40
    )
    persona.behavior_habits = [
        "Prefers ready meals or takeaways",
        "Technology-savvy, orders meals online",
        "Began HIIT workouts during lockdown",
        "Tries to balance work and healthy lifestyle"
    ]
    persona.frustrations = [
        "Wasting time Googling menus",
        "Hard to find healthy categories",
        "Menus lack transparency"
    ]
    persona.goals = [
        "Enjoy healthy lifestyle",
        "Get full info on takeaway meals",
        "Filter by dietary needs",
        "Quick & convenient delivery"
    ]
    persona.quote = "I want to spend less time ordering a healthy takeaway and more time enjoying my meal."
    persona.personality_type = "INTJ"
    persona.analysis_score = 93
    
    persona.calculate_analysis_score()
    return persona 