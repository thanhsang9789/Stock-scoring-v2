from typing import Dict, List, Tuple, Optional
import pandas as pd
from dataclasses import dataclass, field
import logging

@dataclass
class SmartMoneySignal:
    """Individual signal result for Smart Money Flow"""
    name: str = "SM_5D"
    value: float = 0.0
    state: str = "SM_NEUTRAL"
    score: int = 0
    bullish: bool = False
    color: str = "gray"
    flows: Dict[str, float] = field(default_factory=lambda: {'1D': 0.0, '3D': 0.0, '5D': 0.0})
    direction: str = "Neutral"

class SmartMoneyCalculator:
    """
    Calculates Smart Money Flow (Proprietary + Foreign + Institutional)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.thresholds = config.get('thresholds', {
            'strong_accumulation': 200,
            'accumulation': 10,
            'neutral': -10
        })
        self.scores = config.get('scores', {
            'strong_accumulation': 25,
            'accumulation': 10,
            'neutral': 0,
            'distribution': -25
        })

    def calculate(self, data: Dict) -> SmartMoneySignal:
        """
        Calculate SM_5D signal
        """
        try:
            flow_df = data.get('flows')
            if flow_df is None or flow_df.empty:
                return SmartMoneySignal()
                
            # Aggregate flows: SM = PRO + FOREIGN + INST
            # Assuming columns are 'prop_net', 'foreign_net', 'inst_net', 'retail_net' 
            # as defined in our collector fallback
            cols = ['prop_net', 'foreign_net', 'inst_net']
            for col in cols:
                if col not in flow_df.columns:
                    flow_df[col] = 0.0
            
            flow_df['sm_net'] = flow_df['prop_net'] + flow_df['foreign_net'] + flow_df['inst_net']
            
            # Calculate 1D, 3D, 5D
            v_1d = float(flow_df['sm_net'].tail(1).sum())
            v_3d = float(flow_df['sm_net'].tail(3).sum())
            v_5d = float(flow_df['sm_net'].tail(5).sum())
            
            flows = {
                '1D': round(v_1d, 1),
                '3D': round(v_3d, 1),
                '5D': round(v_5d, 1)
            }
            
            # Primary signal is 5D flow
            val = v_5d
            
            # Classification
            state = "SM_NEUTRAL"
            score = 0
            bullish = False
            color = "gray"
            
            if val >= self.thresholds['strong_accumulation']:
                state = "SM_ACCUMULATION"
                score = self.scores['strong_accumulation']
                bullish = True
                color = "green"
            elif val >= self.thresholds['accumulation']:
                state = "SM_BUYING"
                score = self.scores['accumulation']
                bullish = True
                color = "blue"
            elif val > self.thresholds['neutral']:
                state = "SM_NEUTRAL"
                score = self.scores['neutral']
                bullish = False
                color = "gray"
            else:
                state = "SM_DISTRIBUTION"
                score = self.scores['distribution']
                # CONTRARIAN LOGIC (from blueprint): Marked bullish=True for strategy
                bullish = True
                color = "red"
                
            # Direction Pattern
            direction = self._get_direction(v_1d, v_3d, v_5d)
            
            return SmartMoneySignal(
                value=round(val, 1),
                state=state,
                score=score,
                bullish=bullish,
                color=color,
                flows=flows,
                direction=direction
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating smart money flow: {e}")
            return SmartMoneySignal()

    def _get_direction(self, v1, v3, v5) -> str:
        if v1 > 0 and v3 > 0 and v5 > 0:
            return "↗↗ Continuous Rise"
        elif v1 < 0 and v3 < 0 and v5 < 0:
            return "↘↘ Continuous Fall"
        elif v1 > 0 and v5 < 0:
            return "↘↗ Reversal Up"
        elif v1 < 0 and v5 > 0:
            return "↗↘ Reversal Down"
        else:
            return "Mixed Signals"

    def get_retail_status(self, data: Dict) -> str:
        """Helper to get retail flow status for reporting"""
        try:
            flow_df = data.get('flows')
            if flow_df is None or 'retail_net' not in flow_df.columns:
                return "NEUTRAL"
                
            retail_5d = flow_df['retail_net'].tail(5).sum()
            sm_5d = (flow_df['prop_net'] + flow_df['foreign_net'] + flow_df['inst_net']).tail(5).sum()
            
            if retail_5d > 5 and sm_5d < -10:
                return "🚨 DANGER"
            elif retail_5d < -5 and sm_5d > 10:
                return "✅ HEALTHY"
            elif abs(retail_5d) < 5:
                return "⚠️ WATCH"
            else:
                return "NEUTRAL"
        except:
            return "NEUTRAL"
