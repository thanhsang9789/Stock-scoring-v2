from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class PriceSignal:
    name: str = "PRICE"
    value: float = 0.0
    score: int = 0
    bullish: bool = False
    color: str = "gray"

class PriceSignalCalculator:
    """
    Calculates Price Momentum based on daily percentage change
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.thresholds = config.get('thresholds', {
            'strong_up': 2.0,
            'neutral_down': -1.0
        })
        self.scores = config.get('scores', {
            'strong_up': 10,
            'moderate_up': 5,
            'neutral': 0,
            'down': -10
        })

    def calculate(self, data: Dict) -> PriceSignal:
        """
        Calculate Price signal
        """
        try:
            # Last price change pct
            changes = data.get('change_pct', [])
            if not changes:
                return PriceSignal()
                
            val = changes[-1]
            
            score = 0
            bullish = False
            color = "gray"
            
            if val >= self.thresholds['strong_up']:
                score = self.scores['strong_up']
                bullish = True
                color = "green"
            elif val > 0:
                score = self.scores['moderate_up']
                bullish = True
                color = "green"
            elif val >= self.thresholds['neutral_down']:
                score = self.scores['neutral']
                bullish = False
                color = "gray"
            else:
                score = self.scores['down']
                bullish = False
                color = "red"
                
            return PriceSignal(
                value=round(val, 2),
                score=score,
                bullish=bullish,
                color=color
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating price signal: {e}")
            return PriceSignal()
