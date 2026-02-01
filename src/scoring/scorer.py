from typing import Dict, List, Tuple
import logging

class ScoreCalculator:
    """
    Calculates Raw Score, Conflict Multiplier and Final Score
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.multipliers = config.get('multipliers', {
            'perfect': 1.3,
            'strong': 1.0,
            'mixed': 0.5,
            'conflict': 0.3
        })

    def calculate(
        self, 
        avg_vol_signal, 
        sm_signal, 
        investor_type_signal, 
        price_signal
    ) -> Tuple[int, float, str]:
        """
        Calculate total score and multiplier
        
        Returns:
            Tuple of (raw_score, multiplier, label)
        """
        try:
            # 1. Raw Score Calculation
            raw_score = (
                avg_vol_signal.score + 
                sm_signal.score + 
                investor_type_signal.score + 
                price_signal.score
            )
            
            # 2. Conflict Multiplier logic
            bullish_count = sum([
                1 if avg_vol_signal.bullish else 0,
                1 if sm_signal.bullish else 0,
                1 if investor_type_signal.bullish else 0,
                1 if price_signal.bullish else 0
            ])
            
            # Determine multiplier
            if bullish_count == 4:
                multiplier = self.multipliers['perfect']
                label = "PERFECT 4/4"
            elif bullish_count == 0:
                multiplier = self.multipliers['perfect']
                label = "PERFECT 0/4"
            elif bullish_count == 3:
                multiplier = self.multipliers['strong']
                label = "STRONG 3/4"
            elif bullish_count == 1:
                # Blueprint says 3/4 or 1/4 is STRONG 1.0, but also mentions 0.3 for conflict 1/4?
                # Looking at multiplier table: 3/4 or 1/4 = 1.0x STRONG.
                # But looking at another section: "When only 1 signal is bullish, use 0.3 multiplier".
                # I'll follow the specific rule for 1/4 = 0.3.
                multiplier = self.multipliers['conflict']
                label = "CONFLICT 1/4"
            elif bullish_count == 2:
                multiplier = self.multipliers['mixed']
                label = "MIXED 2/4"
            else:
                multiplier = 1.0
                label = "UNKNOWN"
                
            return raw_score, multiplier, label
            
        except Exception as e:
            self.logger.error(f"Error calculating score: {e}")
            return 0, 1.0, "ERROR"
