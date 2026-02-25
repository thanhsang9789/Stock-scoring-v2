from typing import Dict, List, Union
import logging

class ActionClassifier:
    """
    Classifies the final action based on score and trap presence
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def classify(self, final_score: float, is_trap: bool) -> Dict:
        """
        Decision tree for actions
        """
        if is_trap:
            return {
                'action': '🚨 TRAP - AVOID',
                'position': 0,
                'confidence': 70,
                'color': '#dc2626',
                'emoji': '🚨'
            }
        
        # Ranges based on config or blueprint
        if final_score >= self.config.get('strong_entry', {}).get('score_min', 50):
            return {
                'action': '🌟 STRONG ENTRY',
                'position': self.config.get('strong_entry', {}).get('position', [8, 10]),
                'confidence': self.config.get('strong_entry', {}).get('confidence', 95),
                'color': '#22c55e',
                'emoji': '🌟'
            }
        
        elif final_score >= self.config.get('entry', {}).get('score_min', 30):
            return {
                'action': '✅ ENTRY',
                'position': self.config.get('entry', {}).get('position', [6, 8]),
                'confidence': self.config.get('entry', {}).get('confidence', 85),
                'color': '#3b82f6',
                'emoji': '✅'
            }
        
        elif final_score >= self.config.get('watch', {}).get('score_min', 15):
            return {
                'action': '👀 WATCH',
                'position': self.config.get('watch', {}).get('position', [3, 5]),
                'confidence': self.config.get('watch', {}).get('confidence', 60),
                'color': '#eab308',
                'emoji': '👀'
            }
        
        elif final_score >= self.config.get('neutral', {}).get('score_min', -5):
            return {
                'action': '⚖️ NEUTRAL',
                'position': 0,
                'confidence': self.config.get('neutral', {}).get('confidence', 40),
                'color': '#94a3b8',
                'emoji': '⚖️'
            }
        
        elif final_score >= self.config.get('caution', {}).get('score_min', -15):
            return {
                'action': '⚠️ CAUTION',
                'position': 0,
                'confidence': self.config.get('caution', {}).get('confidence', 30),
                'color': '#f97316',
                'emoji': '⚠️'
            }
        
        else: # EXIT
            return {
                'action': '🚫 EXIT',
                'position': 0,
                'confidence': self.config.get('exit', {}).get('confidence', 20),
                'color': '#dc2626',
                'emoji': '🚫'
            }
