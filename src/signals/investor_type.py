from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass, field
import logging

@dataclass
class InvestorTypeSignal:
    name: str = "INVESTOR_TYPE"
    value: str = "SUPPORTIVE"
    state: str = "SUPPORTIVE"
    score: int = 10
    bullish: bool = True
    color: str = "green"
    breakdown: Dict[str, float] = field(default_factory=dict)

class InvestorTypeAnalyzer:
    """
    Analyzes investor type breakdown and institutional support (formerly TOSM)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.default_score = config.get('default_score', 10)
        self.default_state = config.get('default_state', "SUPPORTIVE")

    def analyze(self, data: Dict) -> InvestorTypeSignal:
        """
        Analyze investor type breakdown
        """
        try:
            flow_df = data.get('flows')
            if flow_df is None or flow_df.empty:
                return InvestorTypeSignal(
                    breakdown={'PROP': 0, 'FOR': 0, 'INST': 0, 'RETAIL': 0}
                )
            
            # 5-day flows for each type
            # Assuming columns: prop_net, foreign_net, inst_net, retail_net
            breakdown = {
                'PROPRIETARY': round(float(flow_df['prop_net'].tail(5).sum()), 1),
                'FOREIGN': round(float(flow_df['foreign_net'].tail(5).sum()), 1),
                'INSTITUTIONAL': round(float(flow_df['inst_net'].tail(5).sum()), 1),
                'RETAIL': round(float(flow_df['retail_net'].tail(5).sum()), 1)
            }
            
            # Simple heuristic from blueprint: Most stocks are "SUPPORTIVE"
            # In a more advanced version, we could define logic for "WEAK" or "NEUTRAL"
            state = self.default_state
            score = self.default_score
            bullish = True
            color = "green"
            
            return InvestorTypeSignal(
                value=state,
                state=state,
                score=score,
                bullish=bullish,
                color=color,
                breakdown=breakdown
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing investor types: {e}")
            return InvestorTypeSignal()
