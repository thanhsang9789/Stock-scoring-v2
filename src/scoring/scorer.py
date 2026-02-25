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
        price_signal,
        data_confidence: float = 1.0
    ) -> Tuple[int, float, str]:
        """
        Calculate total score and multiplier with dynamic re-weighting
        
        Returns:
            Tuple of (raw_score, multiplier, label)
        """
        try:
            # 1. Raw Score Calculation with Dynamic Re-weighting
            if data_confidence < 0.7:
                # Re-weight to Price (50%) and Volume (50%)
                raw_score = (avg_vol_signal.score * 2) + (price_signal.score * 2)
                self.logger.info("Dynamic re-weighting applied due to low data confidence.")
            else:
                raw_score = (
                    avg_vol_signal.score + 
                    sm_signal.score + 
                    investor_type_signal.score + 
                    price_signal.score
                )
            
            # 2. Conflict Multiplier logic
            # Use only signals that have meaningful data
            active_signals = [avg_vol_signal, price_signal]
            if data_confidence >= 0.7:
                active_signals.extend([sm_signal, investor_type_signal])
            
            bullish_count = sum([1 for s in active_signals if s.bullish])
            total_active = len(active_signals)
            
            # Determine multiplier
            if bullish_count == total_active:
                multiplier = self.multipliers['perfect']
                label = f"PERFECT {bullish_count}/{total_active}"
            elif bullish_count == 0:
                multiplier = self.multipliers['perfect']
                label = f"PERFECT 0/{total_active}"
            elif bullish_count == total_active - 1 or (total_active > 2 and bullish_count == 1):
                multiplier = self.multipliers['strong']
                label = f"STRONG {bullish_count}/{total_active}"
            elif bullish_count / total_active == 0.5:
                multiplier = self.multipliers['mixed']
                label = f"MIXED {bullish_count}/{total_active}"
            else:
                multiplier = self.multipliers['conflict']
                label = f"CONFLICT {bullish_count}/{total_active}"
                
            return int(raw_score), multiplier, label
            
        except Exception as e:
            self.logger.error(f"Error calculating score: {e}")
            return 0, 1.0, "ERROR"
