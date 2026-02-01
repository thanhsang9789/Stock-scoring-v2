from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from datetime import datetime

@dataclass
class Stock:
    """Complete stock analysis results"""
    ticker: str
    date: datetime
    rank: int = 0
    sector: str = "Unknown"
    
    # Price data
    price: float = 0.0
    price_change_pct: float = 0.0
    
    # Signals
    avg_vol_ratio_signal: any = None
    smart_money_signal: any = None
    investor_type_signal: any = None
    price_signal: any = None
    
    # Scoring
    raw_score: int = 0
    multiplier: float = 1.0
    multiplier_label: str = ""
    final_score: float = 0.0
    
    # Classification
    action: str = ""
    position: Union[int, List[int]] = 0
    confidence: int = 0
    color: str = "#94a3b8"
    
    # Trap
    trap: any = None
    retail_status: str = "NEUTRAL"

@dataclass
class ReportData:
    """Complete report data for rendering"""
    date: datetime
    generated_at: datetime
    stocks: List[Stock]
    summary: Dict
