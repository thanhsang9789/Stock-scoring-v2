from typing import List
import logging

class StockRanker:
    """
    Ranks stocks based on Final Score and Raw Score
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def rank(self, stocks: List) -> List:
        """
        Sort stocks by final_score (desc), then raw_score (desc), then ticker (asc)
        """
        # Primary: Final Score
        # Secondary: Raw Score
        # Tertiary: Ticker
        
        sorted_stocks = sorted(
            stocks, 
            key=lambda x: (-x.final_score, -x.raw_score, x.ticker)
        )
        
        # Assign ranks
        for i, stock in enumerate(sorted_stocks, start=1):
            stock.rank = i
            
        return sorted_stocks
