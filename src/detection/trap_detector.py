from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

@dataclass
class TrapDetection:
    is_trap: bool = False
    conditions: List[Dict] = field(default_factory=list)
    count: int = 0
    message: str = ""

class TrapDetector:
    """
    Identifies dangerous situations: retail FOMO meets smart money distribution
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.avg_vol_threshold = config.get('avg_vol_ratio_threshold', 1.0)
        self.sm_threshold = config.get('sm_threshold', -10)
        self.retail_threshold = config.get('retail_threshold', 5)

    def detect(self, avg_vol_signal, sm_signal, data: Dict) -> TrapDetection:
        """
        Detect TRAP pattern
        """
        try:
            flow_df = data.get('flows')
            if flow_df is None or 'retail_net' not in flow_df.columns:
                return TrapDetection()
            
            # Criteria (ALL 3 must be TRUE)
            # 1. Volume looks bullish
            c1_val = avg_vol_signal.value
            c1 = c1_val >= self.avg_vol_threshold
            
            # 2. Smart money distributing
            c2_val = sm_signal.value
            c2 = c2_val < self.sm_threshold
            
            # 3. Retail FOMO buying
            c3_val = float(flow_df['retail_net'].tail(5).sum())
            c3 = c3_val > self.retail_threshold
            
            is_trap = c1 and c2 and c3
            count = sum([c1, c2, c3])
            
            conditions = [
                {'name': 'AVG_VOL_RATIO ≥ 1.0', 'met': c1, 'value': c1_val},
                {'name': 'SM_5D < -10B', 'met': c2, 'value': c2_val},
                {'name': 'RETAIL_5D > +5B', 'met': c3, 'value': round(c3_val, 1)}
            ]
            
            msg = "⚠️ Smart Money selling, Retail FOMO buying → AVOID!" if is_trap else ""
            
            return TrapDetection(
                is_trap=is_trap,
                conditions=conditions,
                count=count,
                message=msg
            )
            
        except Exception as e:
            self.logger.error(f"Error in trap detection: {e}")
            return TrapDetection()
