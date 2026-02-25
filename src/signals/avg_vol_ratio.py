from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging

@dataclass
class AvgVolRatioSignal:
    """Individual signal result for Volume Ratio"""
    name: str = "AVG_VOL_RATIO"
    value: float = 0.0
    state: str = "NEUTRAL"
    score: int = 0
    bullish: bool = False
    color: str = "gray"
    history: List[float] = None
    pattern: str = "Sideways"

class AvgVolRatioCalculator:
    """
    Calculates Volume-based accumulation/distribution indicator (formerly KLTB)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.window = config.get('window', 20)
        self.thresholds = config.get('thresholds', {
            'accumulation': 1.3,
            'buying': 1.0,
            'neutral': 0.8
        })
        self.scores = config.get('scores', {
            'accumulation': 30,
            'buying': 15,
            'neutral': 0,
            'distribution': -15
        })

    def calculate(self, data: Dict) -> AvgVolRatioSignal:
        """
        Calculate AVG_VOL_RATIO signal
        
        Args:
            data: Dictionary containing 'ohlcv' DataFrame or 'volume' list
            
        Returns:
            AvgVolRatioSignal object
        """
        try:
            volumes = data.get('volume', [])
            if len(volumes) < self.window:
                self.logger.warning(f"Insufficient data for volume ratio: {len(volumes)} < {self.window}")
                return AvgVolRatioSignal()
                
            # Current Volume (T0)
            current_vol = volumes[-1]
            
            # Average Volume (Last 20D excluding T0)
            avg_vol_20d = np.mean(volumes[-(self.window+1):-1])
            
            if avg_vol_20d == 0:
                return AvgVolRatioSignal()
                
            ratio = current_vol / avg_vol_20d
            
            # History (Last 3 periods)
            # To get accurate historical ratios, we need more data
            h_ratios = []
            for i in range(3):
                idx = -1 - i
                if len(volumes) > abs(idx) + self.window:
                    v_curr = volumes[idx]
                    v_avg = np.mean(volumes[idx - self.window : idx])
                    h_ratios.append(round(v_curr / v_avg if v_avg > 0 else 0, 2))
                else:
                    h_ratios.append(0.0)
            
            h_ratios.reverse() # [T-2, T-1, T0]
            
            # State classification
            state = "NEUTRAL"
            score = 0
            bullish = False
            color = "gray"
            
            if ratio >= self.thresholds['accumulation']:
                state = "ACCUMULATION"
                score = self.scores['accumulation']
                bullish = True
                color = "green"
            elif ratio >= self.thresholds['buying']:
                state = "BUYING"
                score = self.scores['buying']
                bullish = True
                color = "green"
            elif ratio >= self.thresholds['neutral']:
                state = "NEUTRAL"
                score = self.scores['neutral']
                bullish = False
                color = "gray"
            else:
                state = "DISTRIBUTION"
                score = self.scores['distribution']
                bullish = False
                color = "red"
                
            # Pattern Recognition
            pattern = self._recognize_pattern(h_ratios)
            
            return AvgVolRatioSignal(
                value=round(ratio, 2),
                state=state,
                score=score,
                bullish=bullish,
                color=color,
                history=h_ratios,
                pattern=pattern
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating volume ratio: {e}")
            return AvgVolRatioSignal()

    def _recognize_pattern(self, history: List[float]) -> str:
        """Recognize direction pattern from last 3 ratios"""
        if not history or len(history) < 3:
            return "Stable"
            
        t2, t1, t0 = history
        
        if t2 > t1 and t1 < t0:
            return "↘↗ Bottom then Rise"
        elif t2 < t1 and t1 > t0:
            return "↗↘ Peak then Fall"
        elif t2 < t1 < t0:
            return "↗↗ Continuous Rise"
        elif t2 > t1 > t0:
            return "↘↘ Continuous Fall"
        elif t2 < t1 and t1 == t0:
            return "↗→ Rise then Hold"
        elif t2 > t1 and t1 == t0:
            return "↘→ Fall then Hold"
        else:
            return "→→ Sideways"
