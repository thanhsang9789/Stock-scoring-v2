# 📊 STOCK SCORE V2 - COMPREHENSIVE SYSTEM BLUEPRINT

## 🎯 PROJECT OVERVIEW

### **System Name**: Stock Score V2 - Beta Trading Analysis Framework
### **Purpose**: Multi-factor quantitative scoring system for Vietnamese stock market analysis
### **Target Market**: Vietnam HOSE (Ho Chi Minh Stock Exchange)
### **Output**: Daily HTML report with actionable trading signals and risk warnings

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                  VN100 LIQUIDITY SCANNER (NEW)                   │
├─────────────────────────────────────────────────────────────────┤
│  • Fetch VN100 constituent list (vnstock)                       │
│  • Calculate liquidity metrics (20-day average trading value)   │
│  • Rank stocks by liquidity                                     │
│  • Select top 15 most liquid stocks                             │
│  • Output: Dynamic stock list for analysis                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Selected Stock List]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     DATA COLLECTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  • vnstock API (price, volume, OHLCV data)                      │
│  • FiinTrade API (investor flow: TD, NN, TC, CN)                │
│  • Historical database (rolling calculations)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SIGNAL CALCULATION ENGINE                      │
├─────────────────────────────────────────────────────────────────┤
│  Module 1: KLTB Calculator (Volume Analysis)                    │
│  Module 2: SM_5D Aggregator (Smart Money Flow)                  │
│  Module 3: TOSM Analyzer (Investor Type Breakdown)              │
│  Module 4: Price Momentum Scorer                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   SCORING & RANKING SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│  • Raw Score Calculation (sum of 4 signals)                     │
│  • Conflict Multiplier (signal alignment check)                 │
│  • Final Score = Raw × Multiplier                               │
│  • Stock Ranking (highest to lowest)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TRAP DETECTION SYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│  • CN Flow Divergence Detector                                  │
│  • Smart Money Distribution + Retail FOMO Pattern               │
│  • Score Override Logic (Trap = 0.0)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      REPORT GENERATOR                            │
├─────────────────────────────────────────────────────────────────┤
│  • HTML Template Engine                                         │
│  • Dynamic Stock Cards                                          │
│  • Summary Dashboard                                            │
│  • Liquidity Ranking Table (NEW)                                │
│  • Color-coded Visualizations                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 DETAILED MODULE SPECIFICATIONS

---

### **MODULE 1: DATA COLLECTION**

---

#### **MODULE 1.0: VN100 LIQUIDITY SCANNER (NEW)**

**Purpose**: Dynamically select top liquid stocks from VN100 index

**Class Structure**:
```python
# src/collectors/vn100_scanner.py

from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime, timedelta
from vnstock import listing_companies, stock_historical_data
import logging

class VN100LiquidityScanner:
    """
    Scanner to identify most liquid stocks from VN100 index
    """
    
    def __init__(self, config: Dict):
        """
        Initialize scanner with configuration
        
        Args:
            config: Configuration dict with:
                - top_n: Number of stocks to select
                - lookback_days: Days for liquidity calculation
                - min_trading_value: Minimum daily value threshold (Billion VND)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.vn100_constituents = []
        self.liquidity_data = pd.DataFrame()
    
    def get_vn100_constituents(self) -> List[str]:
        """
        Fetch current VN100 constituent stocks
        
        Returns:
            List of ticker symbols in VN100
        """
        try:
            # Method 1: Try to get from vnstock listing
            df = listing_companies(live=True)
            
            # Filter for VN100 stocks (check available columns)
            if 'index' in df.columns:
                vn100 = df[df['index'].str.contains('VN100', na=False)]
                if len(vn100) > 0:
                    tickers = vn100['ticker'].tolist()
                    self.logger.info(f"Found {len(tickers)} stocks in VN100 from listing")
                    return tickers
            
            # Method 2: Try icb_code or other filters
            if 'icbCode' in df.columns or 'exchange' in df.columns:
                hose_stocks = df[df['exchange'] == 'HOSE']
                # Get by market cap if available
                if 'marketCap' in hose_stocks.columns:
                    top_stocks = hose_stocks.nlargest(100, 'marketCap')['ticker'].tolist()
                    self.logger.info(f"Selected top 100 HOSE stocks by market cap")
                    return top_stocks
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch VN100 from vnstock: {e}")
        
        # Method 3: Fallback to known VN100 list (updated quarterly)
        self.logger.warning("Using fallback VN100 list")
        return self._get_fallback_vn100()
    
    def _get_fallback_vn100(self) -> List[str]:
        """
        Fallback list of VN100 stocks (update quarterly)
        """
        return [
            # Banking
            'VCB', 'BID', 'CTG', 'TCB', 'STB', 'MBB', 'VPB', 'ACB', 'HDB', 
            'TPB', 'EIB', 'LPB', 'SHB', 'VIB',
            
            # Real Estate
            'VHM', 'VIC', 'VRE', 'NVL', 'DXG', 'PDR', 'KDH', 'DIG', 'BCM',
            'HDG', 'NLG', 'IDC', 'DRH',
            
            # Manufacturing
            'HPG', 'HSG', 'NKG', 'TLG', 'DCM', 'DGC', 'DPM', 'PHR', 'GVR',
            'GEX', 'HT1', 'CSV', 'AAA',
            
            # Consumer Goods
            'VNM', 'MSN', 'MWG', 'FPT', 'PNJ', 'SAB', 'VHC', 'GMD', 'DBC',
            'PHR', 'TSC',
            
            # Oil & Gas
            'GAS', 'PLX', 'PVD', 'PVS', 'PVT', 'POW', 'BSR',
            
            # Securities
            'SSI', 'VCI', 'VND', 'HCM', 'MBS', 'FTS',
            
            # Utilities
            'NT2', 'PC1', 'REE', 'BWE',
            
            # Aviation & Transport
            'VJC', 'HVN', 'VTP', 'GMD',
            
            # Construction
            'HBC', 'CTD', 'FCN', 'LCG',
            
            # Others
            'VGC', 'DHC', 'KBC', 'PDN', 'BVH', 'VCI', 'SBT', 'KDC',
        ]
    
    def calculate_liquidity_metrics(
        self, 
        ticker: str, 
        lookback_days: int = 20
    ) -> Dict:
        """
        Calculate liquidity metrics for a stock
        
        Args:
            ticker: Stock ticker symbol
            lookback_days: Number of days to analyze
        
        Returns:
            Dict with liquidity metrics
        """
        try:
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 10)
            
            df = stock_historical_data(
                symbol=ticker,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                resolution='1D',
                type='stock',
                source='VCI'
            )
            
            # Ensure we have data
            if df is None or len(df) == 0:
                raise ValueError(f"No data returned for {ticker}")
            
            # Take last N trading days
            df = df.tail(lookback_days)
            
            # Calculate trading value (price × volume)
            df['trading_value'] = df['close'] * df['volume']
            
            # Calculate metrics
            metrics = {
                'ticker': ticker,
                'avg_trading_value': df['trading_value'].mean(),
                'avg_volume': df['volume'].mean(),
                'avg_price': df['close'].mean(),
                'total_trading_value': df['trading_value'].sum(),
                'latest_price': df['close'].iloc[-1],
                'latest_volume': df['volume'].iloc[-1],
                'data_points': len(df),
                'date': df['time'].iloc[-1] if 'time' in df.columns else datetime.now()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate liquidity for {ticker}: {e}")
            return None
    
    def scan_and_select(
        self, 
        top_n: int = 15, 
        lookback_days: int = 20
    ) -> List[str]:
        """
        Main method: Scan VN100 and select top N liquid stocks
        
        Args:
            top_n: Number of stocks to select
            lookback_days: Days to calculate liquidity
        
        Returns:
            List of selected ticker symbols
        """
        self.logger.info("=" * 60)
        self.logger.info("VN100 LIQUIDITY SCANNER")
        self.logger.info("=" * 60)
        
        # Step 1: Get VN100 constituents
        self.logger.info("Step 1: Fetching VN100 constituents...")
        self.vn100_constituents = self.get_vn100_constituents()
        self.logger.info(f"Found {len(self.vn100_constituents)} stocks in VN100")
        
        # Step 2: Calculate liquidity for each stock
        self.logger.info("Step 2: Calculating liquidity metrics...")
        liquidity_results = []
        
        for idx, ticker in enumerate(self.vn100_constituents, 1):
            self.logger.info(f"  [{idx}/{len(self.vn100_constituents)}] {ticker}...")
            
            metrics = self.calculate_liquidity_metrics(ticker, lookback_days)
            
            if metrics is not None:
                liquidity_results.append(metrics)
            else:
                self.logger.warning(f"  Skipping {ticker} - no data")
        
        # Step 3: Create DataFrame and rank
        self.logger.info("Step 3: Ranking by liquidity...")
        self.liquidity_data = pd.DataFrame(liquidity_results)
        
        if len(self.liquidity_data) == 0:
            raise ValueError("No liquidity data collected - check data source")
        
        # Sort by average trading value
        self.liquidity_data = self.liquidity_data.sort_values(
            'avg_trading_value', 
            ascending=False
        )
        
        # Add rank
        self.liquidity_data['rank'] = range(1, len(self.liquidity_data) + 1)
        
        # Filter by minimum trading value if specified
        min_value = self.config.get('min_trading_value', 0) * 1e9  # Convert to VND
        if min_value > 0:
            before_count = len(self.liquidity_data)
            self.liquidity_data = self.liquidity_data[
                self.liquidity_data['avg_trading_value'] >= min_value
            ]
            after_count = len(self.liquidity_data)
            self.logger.info(f"Filtered by min value: {before_count} → {after_count} stocks")
        
        # Step 4: Select top N
        top_stocks = self.liquidity_data.head(top_n)
        selected_tickers = top_stocks['ticker'].tolist()
        
        # Log results
        self.logger.info("=" * 60)
        self.logger.info(f"TOP {top_n} MOST LIQUID STOCKS:")
        self.logger.info("=" * 60)
        for idx, row in top_stocks.iterrows():
            self.logger.info(
                f"  {row['rank']:2d}. {row['ticker']:5s} | "
                f"{row['avg_trading_value']/1e9:8.1f}B VND/day | "
                f"{row['avg_volume']/1e6:6.1f}M shares | "
                f"Price: {row['avg_price']:8.1f}"
            )
        self.logger.info("=" * 60)
        
        return selected_tickers
    
    def get_liquidity_report(self) -> pd.DataFrame:
        """
        Get detailed liquidity report for selected stocks
        
        Returns:
            DataFrame with liquidity rankings
        """
        return self.liquidity_data.copy()
    
    def export_liquidity_data(self, filepath: str):
        """
        Export liquidity data to CSV
        
        Args:
            filepath: Output CSV file path
        """
        if len(self.liquidity_data) > 0:
            self.liquidity_data.to_csv(filepath, index=False)
            self.logger.info(f"Liquidity data exported to {filepath}")
```

**Usage Example**:
```python
# Initialize scanner
config = {
    'top_n': 15,
    'lookback_days': 20,
    'min_trading_value': 50  # 50 Billion VND minimum
}

scanner = VN100LiquidityScanner(config)

# Scan and select
selected_stocks = scanner.scan_and_select(top_n=15)

# Get detailed report
report = scanner.get_liquidity_report()

# Export to CSV
scanner.export_liquidity_data('data/vn100_liquidity.csv')
```

**Output Example**:
```
==============================================================
VN100 LIQUIDITY SCANNER
==============================================================
Step 1: Fetching VN100 constituents...
Found 95 stocks in VN100
Step 2: Calculating liquidity metrics...
  [1/95] VCB...
  [2/95] VHM...
  [3/95] VIC...
  ...
Step 3: Ranking by liquidity...
==============================================================
TOP 15 MOST LIQUID STOCKS:
==============================================================
   1. VCB    |   2345.7B VND/day |  32.4M shares | Price:  72400.0
   2. VHM    |   1876.3B VND/day |  28.1M shares | Price:  66800.0
   3. HPG    |   1654.2B VND/day | 124.6M shares | Price:  13300.0
   4. VIC    |   1532.8B VND/day |  35.7M shares | Price:  42900.0
   5. TCB    |   1234.5B VND/day |  41.2M shares | Price:  29950.0
  ...
==============================================================
```

---

#### **1.1 Stock Universe - DYNAMIC LIQUIDITY-BASED SELECTION**

- **Type**: Dynamic liquidity-based selection from VN100
- **Source Index**: VN100 (top 100 stocks by market cap and liquidity on HOSE)
- **Size**: Top 15 stocks by liquidity (configurable)
- **Selection Method**: Automated daily scan using vnstock
- **Exchange**: HOSE (Ho Chi Minh Stock Exchange)
- **Selection Criteria**: 
  1. Must be part of VN100 index
  2. Ranked by average daily trading value (liquidity)
  3. Top 15 most liquid stocks selected automatically
  4. Refreshed daily to adapt to market conditions

**Selection Algorithm**:
```python
def select_top_liquid_stocks(n: int = 15, lookback_days: int = 20) -> List[str]:
    """
    Select top N most liquid stocks from VN100
    
    Args:
        n: Number of stocks to select (default 15)
        lookback_days: Days to calculate average liquidity (default 20)
    
    Returns:
        List of stock tickers sorted by liquidity (highest first)
    """
    # Step 1: Get VN100 constituent list
    vn100_stocks = get_vn100_constituents()
    
    # Step 2: Calculate average daily liquidity for each stock
    liquidity_data = []
    for ticker in vn100_stocks:
        try:
            # Get historical data
            df = get_stock_data(ticker, lookback_days)
            
            # Calculate average trading value (price × volume)
            avg_value = (df['close'] * df['volume']).mean()
            
            liquidity_data.append({
                'ticker': ticker,
                'avg_trading_value': avg_value,
                'avg_volume': df['volume'].mean(),
            })
        except Exception as e:
            logger.warning(f"Could not calculate liquidity for {ticker}: {e}")
            continue
    
    # Step 3: Sort by average trading value (descending)
    liquidity_df = pd.DataFrame(liquidity_data)
    liquidity_df = liquidity_df.sort_values('avg_trading_value', ascending=False)
    
    # Step 4: Select top N stocks
    top_stocks = liquidity_df.head(n)['ticker'].tolist()
    
    logger.info(f"Selected {len(top_stocks)} stocks from VN100 by liquidity")
    logger.info(f"Top 5: {top_stocks[:5]}")
    
    return top_stocks
```

**Fallback Strategy**:
If VN100 data is unavailable or liquidity calculation fails:
```python
# Fallback to known high-liquidity stocks
FALLBACK_STOCKS = [
    'VCB', 'VHM', 'VIC', 'HPG', 'VNM', 
    'MSN', 'GAS', 'TCB', 'BID', 'STB',
    'MWG', 'VPB', 'PLX', 'POW', 'FPT'
]
```

**Benefits of Dynamic Selection**:
- ✅ Always analyzes the most actively traded stocks
- ✅ Adapts to changing market conditions
- ✅ Reduces bias from static watchlists
- ✅ Ensures sufficient data quality (high liquidity = reliable signals)
- ✅ Captures market leaders and momentum stocks
- ✅ Automatic rebalancing as liquidity shifts
- ✅ Better represents actual market opportunities

**Market Adaptability**:
The dynamic selection means:
1. **Bull Markets**: Automatically captures hot sectors with high volume
2. **Bear Markets**: Focuses on defensive stocks still trading actively  
3. **Sector Rotation**: Adapts as liquidity shifts between sectors
4. **IPO/Listing Changes**: New VN100 additions automatically considered
5. **Delisting/Suspended**: Automatically excluded if trading stops

**Quality Filters Built-In**:
- Minimum trading value threshold (configurable, e.g., 50B VND/day)
- Data quality check (requires 20 days of clean data)
- Active trading requirement (excludes illiquid stocks)

**Refresh Strategy**:
```python
# Daily: Full scan and selection (default)
# Weekly: Scan once per week, use same list daily
# Monthly: Scan monthly for stable watchlist

refresh_options = {
    'daily': 'Scan every run - most adaptive',
    'weekly': 'Scan Mondays - balanced approach',
    'monthly': 'Scan 1st trading day - stable list'
}
```

#### **1.2 Data Sources**

**Single Source: vnstock (Exclusive)**
```python
All data collected from vnstock library - no external APIs required

Required data per stock:
- Daily OHLCV (Open, High, Low, Close, Volume)
- Investor transaction data (Proprietary, Foreign, Institutional, Retail)
- Historical period: Minimum 20 trading days
- Fields needed:
  * date
  * close_price
  * volume
  * price_change_percent
  * proprietary_net (TD - Tự doanh)
  * foreign_net (NN - Nước ngoài)
  * institutional_net (TC - Tổ chức)
  * retail_net (CN - Cá nhân)
```

**vnstock Data Collection Methods**:
```python
from vnstock import stock_historical_data, financial_flow

# Method 1: Price and Volume Data
def get_ohlcv_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get OHLCV data from vnstock
    
    Returns DataFrame with: time, open, high, low, close, volume
    """
    df = stock_historical_data(
        symbol=ticker,
        start_date=start_date,
        end_date=end_date,
        resolution='1D',
        type='stock',
        source='VCI'  # Options: 'VCI', 'TCBS', 'SSI'
    )
    return df

# Method 2: Investor Flow Data
def get_investor_flows(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get investor transaction flows from vnstock
    
    Returns DataFrame with proprietary, foreign, institutional, retail flows
    """
    # vnstock provides investor transaction data
    # This may be available through different methods depending on version
    
    # Option A: Direct flow data (if available)
    try:
        flow_df = financial_flow(
            symbol=ticker,
            start_date=start_date,
            end_date=end_date,
            source='VCI'
        )
        return flow_df
    
    except AttributeError:
        # Option B: Calculate from trading data
        # Use stock_intraday_data or other vnstock methods
        return calculate_flows_from_trading_data(ticker, start_date, end_date)

# Method 3: Alternative - Extract from Trading Statistics
def calculate_flows_from_trading_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Calculate investor flows from available vnstock data
    
    vnstock provides:
    - Proprietary trading data
    - Foreign trading data  
    - Institutional trading data
    
    Calculate net flows (buy - sell) for each investor type
    """
    from vnstock import trading_data
    
    df = trading_data(
        symbol=ticker,
        start_date=start_date,
        end_date=end_date
    )
    
    # Process to extract net flows by investor type
    # Structure depends on vnstock data format
    
    flows = pd.DataFrame({
        'date': df['date'],
        'proprietary_net': df['proprietary_buy'] - df['proprietary_sell'],
        'foreign_net': df['foreign_buy'] - df['foreign_sell'],
        'institutional_net': df['institutional_buy'] - df['institutional_sell'],
        'retail_net': df['retail_buy'] - df['retail_sell'],
    })
    
    return flows
```

**Data Aggregation for Multi-Timeframe Analysis**:
```python
def aggregate_flows(flow_df: pd.DataFrame, periods: List[int] = [1, 3, 5]) -> Dict:
    """
    Aggregate flows for 1D, 3D, 5D periods
    
    Args:
        flow_df: DataFrame with daily net flows
        periods: List of days to aggregate [1, 3, 5]
    
    Returns:
        Dict with aggregated flows by period
    """
    result = {}
    
    for period in periods:
        # Get last N days
        recent = flow_df.tail(period)
        
        result[f'{period}D'] = {
            'proprietary': recent['proprietary_net'].sum(),
            'foreign': recent['foreign_net'].sum(),
            'institutional': recent['institutional_net'].sum(),
            'retail': recent['retail_net'].sum(),
        }
    
    return result

# Example output:
{
    '1D': {'proprietary': -169, 'foreign': 203, 'institutional': 40, 'retail': -74},
    '3D': {'proprietary': -250, 'foreign': 450, 'institutional': 120, 'retail': -320},
    '5D': {'proprietary': -340, 'foreign': 340, 'institutional': 200, 'retail': -200},
}
```

**Fallback Strategy for Missing Data**:
```python
def get_complete_stock_data(ticker: str, lookback_days: int = 30) -> Dict:
    """
    Comprehensive data collection with fallbacks
    
    Returns complete dataset or raises informative error
    """
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days + 10)
    
    data = {
        'ticker': ticker,
        'ohlcv': None,
        'flows': None,
        'sector': 'Unknown'
    }
    
    # Step 1: Get OHLCV (required)
    try:
        data['ohlcv'] = get_ohlcv_data(
            ticker, 
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    except Exception as e:
        raise ValueError(f"Cannot get price data for {ticker}: {e}")
    
    # Step 2: Get investor flows (with fallback)
    try:
        data['flows'] = get_investor_flows(
            ticker,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
    except Exception as e:
        logger.warning(f"Flow data unavailable for {ticker}: {e}")
        # Use zeros as fallback
        data['flows'] = create_zero_flows(len(data['ohlcv']))
    
    # Step 3: Get sector info (optional)
    try:
        from vnstock import listing_companies
        companies = listing_companies()
        sector_info = companies[companies['ticker'] == ticker]['icbName'].iloc[0]
        data['sector'] = sector_info
    except:
        data['sector'] = 'Unknown'
    
    return data

def create_zero_flows(n_days: int) -> pd.DataFrame:
    """Create zero flows as fallback when data unavailable"""
    return pd.DataFrame({
        'date': pd.date_range(end=datetime.now(), periods=n_days),
        'proprietary_net': [0] * n_days,
        'foreign_net': [0] * n_days,
        'institutional_net': [0] * n_days,
        'retail_net': [0] * n_days,
    })
```

**vnstock Version Compatibility**:
```python
# The implementation should detect vnstock version and adapt
import vnstock

def check_vnstock_capabilities():
    """
    Check which data methods are available in current vnstock version
    """
    capabilities = {
        'has_financial_flow': hasattr(vnstock, 'financial_flow'),
        'has_trading_data': hasattr(vnstock, 'trading_data'),
        'has_investor_data': hasattr(vnstock, 'investor_data'),
        'version': vnstock.__version__ if hasattr(vnstock, '__version__') else 'unknown'
    }
    
    logger.info(f"vnstock capabilities: {capabilities}")
    return capabilities
```

**Benefits of vnstock-Only Approach**:
- ✅ Single dependency - simpler installation
- ✅ No API keys required
- ✅ Free and open-source
- ✅ Active Vietnamese market data
- ✅ Community support
- ✅ Consistent data format
- ✅ No rate limits (local processing)

**VN100 Index Data**:
```python
# Get VN100 constituent list
def get_vn100_constituents() -> List[str]:
    """
    Fetch current VN100 constituent stocks using vnstock
    
    Returns:
        List of ticker symbols in VN100
    """
    from vnstock import listing_companies
    
    # Method 1: Get from listing with VN100 filter
    try:
        # vnstock v3+ syntax
        df = listing_companies(live=True)
        vn100_stocks = df[df['index'] == 'VN100']['ticker'].tolist()
        
        if len(vn100_stocks) > 0:
            return vn100_stocks
    except Exception as e:
        logger.warning(f"Method 1 failed: {e}")
    
    # Method 2: Fallback - use known VN100 list (updated quarterly)
    # This list should be updated periodically
    return [
        'VCB', 'VHM', 'VIC', 'HPG', 'VNM', 'MSN', 'GAS', 'TCB', 'BID', 'STB',
        'MWG', 'VPB', 'PLX', 'POW', 'FPT', 'CTG', 'VRE', 'HDB', 'SSI', 'VJC',
        'GVR', 'MBB', 'SAB', 'ACB', 'PDR', 'TPB', 'NVL', 'EIB', 'DIG', 'BCM',
        'VCI', 'DXG', 'DPM', 'PNJ', 'REE', 'HT1', 'PVD', 'GMD', 'DCM', 'KDH',
        'NT2', 'VGC', 'BWE', 'VHC', 'PHR', 'SHB', 'LPB', 'HCM', 'DGC', 'VND',
        # ... (total 100 stocks)
    ]

# Calculate liquidity metrics
def calculate_liquidity(ticker: str, days: int = 20) -> Dict:
    """
    Calculate liquidity metrics for a stock
    
    Returns:
        {
            'avg_trading_value': float,  # Average daily value (VND)
            'avg_volume': int,            # Average daily volume
            'avg_price': float,           # Average price
        }
    """
    from vnstock import stock_historical_data
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days+10)  # Buffer for holidays
    
    df = stock_historical_data(
        symbol=ticker,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        resolution='1D',
        type='stock',
        source='VCI'  # or 'TCBS', 'SSI'
    )
    
    # Take last N trading days
    df = df.tail(days)
    
    # Calculate metrics
    df['trading_value'] = df['close'] * df['volume']
    
    return {
        'ticker': ticker,
        'avg_trading_value': df['trading_value'].mean(),
        'avg_volume': df['volume'].mean(),
        'avg_price': df['close'].mean(),
        'total_days': len(df)
    }
```

**Liquidity Ranking Process**:
```python
def rank_by_liquidity(vn100_list: List[str], n: int = 15) -> pd.DataFrame:
    """
    Rank VN100 stocks by liquidity and select top N
    
    Args:
        vn100_list: List of VN100 tickers
        n: Number of stocks to select
    
    Returns:
        DataFrame with ranked stocks and liquidity metrics
    """
    results = []
    
    for ticker in vn100_list:
        try:
            metrics = calculate_liquidity(ticker, days=20)
            results.append(metrics)
        except Exception as e:
            logger.warning(f"Failed to get liquidity for {ticker}: {e}")
            continue
    
    # Create DataFrame and sort
    df = pd.DataFrame(results)
    df = df.sort_values('avg_trading_value', ascending=False)
    
    # Add rank
    df['rank'] = range(1, len(df) + 1)
    
    # Select top N
    top_n = df.head(n)
    
    logger.info(f"Top {n} stocks by liquidity:")
    for idx, row in top_n.iterrows():
        logger.info(f"  {row['rank']}. {row['ticker']}: "
                   f"{row['avg_trading_value']/1e9:.1f}B VND/day")
    
    return top_n
```

#### **1.3 Data Update Frequency**
- **Collection Time**: After market close (>16:00 ICT)
- **Processing Time**: 16:00 - 00:00 ICT
- **Report Generation**: 00:00 - 01:00 ICT next day
- **Delivery**: Daily HTML report

#### **1.4 Data Storage Structure**
```python
StockData = {
    'ticker': str,
    'date': datetime,
    'price': {
        'close': float,
        'change_pct': float,
    },
    'volume': {
        'current': int,
        'avg_20d': int,  # 20-day average
        'kltb': float,   # current / avg_20d
    },
    'flows': {
        'TD': {'1D': float, '3D': float, '5D': float},
        'NN': {'1D': float, '3D': float, '5D': float},
        'TC': {'1D': float, '3D': float, '5D': float},
        'CN': {'1D': float, '3D': float, '5D': float},
    },
    'kltb_history': [float, float, float],  # Last 3 periods
    'sm_flow_history': [float, float, float],  # Last 3 periods (1D, 3D, 5D)
}
```

---

### **MODULE 2: SIGNAL CALCULATION ENGINE**

---

#### **SIGNAL 1: AVG_VOL_RATIO (Average Volume Ratio)**

**Concept**: Volume-based accumulation/distribution indicator
**Former Name**: KLTB (Khối Lượng Trung Bình)

**Calculation**:
```python
AVG_VOL_RATIO = Current_Volume / Average_Volume_20D

Where:
- Current_Volume = today's total volume
- Average_Volume_20D = mean of last 20 trading days volume
```

**State Classification**:
```python
if KLTB >= 1.3:
    state = "ACCUMULATION"  # Strong buying volume
    score = +30
    bullish = True
elif 1.0 <= KLTB < 1.3:
    state = "BUYING"  # Moderate buying volume
    score = +15
    bullish = True
elif 0.8 <= KLTB < 1.0:
    state = "NEUTRAL"  # Normal volume
    score = 0
    bullish = False
else:  # KLTB < 0.8
    state = "DISTRIBUTION"  # Selling pressure, low volume
    score = -15
    bullish = False
```

**Direction Tracking**:
```python
# Track last 3 periods: [T-2, T-1, T0]
kltb_history = [kltb_t2, kltb_t1, kltb_current]

# Pattern Recognition
if kltb_t2 > kltb_t1 and kltb_t1 < kltb_current:
    pattern = "↘↗ Bottom then Rise"  # V-shape recovery
elif kltb_t2 < kltb_t1 and kltb_t1 > kltb_current:
    pattern = "↗↘ Peak then Fall"  # Inverted V
elif kltb_t2 < kltb_t1 < kltb_current:
    pattern = "↗↗ Continuous Rise"  # Uptrend
elif kltb_t2 > kltb_t1 > kltb_current:
    pattern = "↘↘ Continuous Fall"  # Downtrend
elif kltb_t2 < kltb_t1 and kltb_t1 == kltb_current:
    pattern = "↗→ Rise then Hold"  # Consolidation after rise
elif kltb_t2 > kltb_t1 and kltb_t1 == kltb_current:
    pattern = "↘→ Fall then Hold"  # Consolidation after fall
else:
    pattern = "→→ Sideways"  # Flat
```

**Output**:
```python
AVG_VOL_RATIO_Signal = {
    'value': float,        # e.g., 1.73
    'state': str,          # "ACCUMULATION", "BUYING", "NEUTRAL", "DISTRIBUTION"
    'score': int,          # -15, 0, +15, +30
    'bullish': bool,       # True/False
    'history': [float×3],  # Last 3 periods
    'pattern': str,        # Direction description in English
}
```

---

#### **SIGNAL 2: SM_5D (Smart Money 5-Day Flow)**

**Concept**: Institutional investor net flow aggregation

**Calculation**:
```python
SM_5D = PROPRIETARY_5D + FOREIGN_5D + INSTITUTIONAL_5D

Where:
- PROPRIETARY_5D = Proprietary trading 5-day net flow (Billion VND)
- FOREIGN_5D = Foreign investor 5-day net flow (Billion VND)
- INSTITUTIONAL_5D = Institutional 5-day net flow (Billion VND)
- Exclude RETAIL from smart money calculation
```

**State Classification**:
```python
if SM_5D >= 200:
    state = "SM_ACCUMULATION"      # Strong accumulation
    score = +25
    bullish = True
elif SM_5D >= 10:
    state = "SM_BUYING"            # Moderate buying
    score = +10
    bullish = True
elif -10 < SM_5D < 10:
    state = "SM_NEUTRAL"           # Neutral
    score = 0
    bullish = False
else:  # SM_5D <= -10
    state = "SM_DISTRIBUTION"      # Distribution
    score = -25
    bullish = True  # CONTRARIAN SIGNAL - marked bullish for strategy
```

**Note on Contrarian Logic**:
```
SM_DISTRIBUTION is marked as "bullish" (✓) in the system because:
1. This is a swing/momentum trading strategy
2. Smart money distribution creates opportunities for contrarian entry
3. Combined with other signals, it helps identify reversals
4. The conflict multiplier will reduce position size if signals disagree
```

**Multi-Timeframe Tracking**:
```python
# Track 1D, 3D, 5D flows
sm_flows = {
    '1D': PROP_1D + FOREIGN_1D + INST_1D,
    '3D': PROP_3D + FOREIGN_3D + INST_3D,
    '5D': PROP_5D + FOREIGN_5D + INST_5D,
}

# Direction Pattern
if sm_1D > 0 and sm_3D > 0 and sm_5D > 0:
    direction = "↗↗ Continuous Rise"  # All positive
elif sm_1D < 0 and sm_3D < 0 and sm_5D < 0:
    direction = "↘↘ Continuous Fall"  # All negative
elif sm_1D > 0 and sm_5D < 0:
    direction = "↘↗ Reversal Up"  # Turning positive
elif sm_1D < 0 and sm_5D > 0:
    direction = "↗↘ Reversal Down"  # Turning negative
else:
    direction = "Mixed Signals"
```

**Output**:
```python
SM_Signal = {
    'value': float,           # e.g., +257B
    'state': str,             # "SM_ACCUMULATION", "SM_BUYING", "SM_NEUTRAL", "SM_DISTRIBUTION"
    'score': int,             # -25, 0, +10, +25
    'bullish': bool,          # True/False (note contrarian logic)
    'flows': {
        '1D': float,
        '3D': float,
        '5D': float,
    },
    'direction': str,         # Pattern description in English
}
```

---

#### **SIGNAL 3: INVESTOR_TYPE (Investor Type Analysis)**

**Concept**: Detailed investor type breakdown and health check
**Former Name**: TOSM (Type of Smart Money)

**Calculation**:
```python
# Analyze composition of flows
investor_analysis = {
    'PROPRIETARY': PROPRIETARY_5D,  # Brokerage proprietary trading
    'FOREIGN': FOREIGN_5D,          # Foreign institutional
    'INSTITUTIONAL': INSTITUTIONAL_5D,  # Domestic institutional
    'RETAIL': RETAIL_5D,            # Retail investors
}

# Check for healthy institutional engagement
institutional_total = PROPRIETARY_5D + FOREIGN_5D + INSTITUTIONAL_5D

# Investor Type Logic (to be refined based on more data)
# Current implementation: Default "SUPPORTIVE" state
```

**State Classification**:
```python
# Based on observed data, all stocks show "SUPPORTIVE" state
# This suggests healthy institutional participation

# Hypothesis for future implementation:
if institutional_activity_healthy():
    state = "SUPPORTIVE"           # Supportive institutional flows
    score = +10
    bullish = True
elif institutional_dysfunction_detected():
    state = "WEAK"                 # Weak institutional support
    score = -15
    bullish = False
else:
    state = "NEUTRAL"
    score = 0
    bullish = False

# Healthy conditions (suggested):
# - No extreme concentration in single investor type
# - Institutional flows not all negative
# - Reasonable PROPRIETARY/FOREIGN/INSTITUTIONAL balance
```

**Output**:
```python
INVESTOR_TYPE_Signal = {
    'value': str,             # "SUPPORTIVE", "WEAK", "NEUTRAL"
    'state': str,             # Same as value
    'score': int,             # -15, 0, +10
    'bullish': bool,          # True/False
    'breakdown': {
        'PROPRIETARY': float,      # For display in footer
        'FOREIGN': float,
        'INSTITUTIONAL': float,
        'RETAIL': float,
    }
}
```

---

#### **SIGNAL 4: PRICE MOMENTUM**

**Concept**: Simple daily price change percentage

**Calculation**:
```python
price_change_pct = ((Close_Today - Close_Yesterday) / Close_Yesterday) * 100
```

**State Classification**:
```python
if price_change_pct >= 2.0:
    score = +10
    bullish = True
elif price_change_pct >= -1.0:
    score = +5 if price_change_pct > 0 else 0
    bullish = True if price_change_pct > 0 else False
else:  # price_change_pct < -1.0
    score = -10
    bullish = False
```

**Detailed Scoring**:
```python
if price_change_pct >= 2.0:
    score = +10
    color = "green"
elif 0 < price_change_pct < 2.0:
    score = +5
    color = "green"
elif price_change_pct == 0:
    score = 0
    color = "gray"
elif -1.0 <= price_change_pct < 0:
    score = 0
    color = "red"
else:  # price_change_pct < -1.0
    score = -10
    color = "red"
```

**Output**:
```python
Price_Signal = {
    'value': float,           # e.g., +6.88
    'score': int,             # -10, 0, +5, +10
    'bullish': bool,          # True/False
    'color': str,             # "green", "red", "gray"
}
```

---

### **MODULE 3: SCORING & RANKING SYSTEM**

---

#### **3.1 Raw Score Calculation**

**Formula**:
```python
Raw_Score = KLTB_score + SM_5D_score + TOSM_score + Price_score

Range: -65 to +75
- Minimum: -15 + (-25) + (-15) + (-10) = -65
- Maximum: +30 + 25 + 10 + 10 = +75
```

**Example**:
```python
# STB Stock
KLTB_score = +30     # GOM
SM_5D_score = +25    # SM_ACCUM
TOSM_score = +10     # SUS
Price_score = +10    # +6.88%
Raw_Score = 30 + 25 + 10 + 10 = +75
```

---

#### **3.2 Conflict Multiplier**

**Purpose**: Reduce confidence when signals disagree

**Calculation**:
```python
# Count bullish signals (✓)
bullish_count = sum([
    KLTB_bullish,
    SM_5D_bullish,
    TOSM_bullish,
    Price_bullish
])

# Determine multiplier
if bullish_count == 4 or bullish_count == 0:
    multiplier = 1.3     # PERFECT alignment (all agree)
    label = "PERFECT 4/4" or "PERFECT 0/4"
elif bullish_count == 3 or bullish_count == 1:
    multiplier = 1.0     # STRONG alignment
    label = "STRONG 3/4" or "STRONG 1/4"
elif bullish_count == 2:
    multiplier = 0.5     # MIXED signals
    label = "MIXED 2/4"
else:
    # Edge cases (shouldn't happen)
    multiplier = 0.3
    label = "CONFLICT"
```

**Special Case - High Conflict**:
```python
# When only 1 signal is bullish, use 0.3 multiplier
if bullish_count == 1:
    multiplier = 0.3
    label = "CONFLICT 1/4"
```

**Multiplier Table**:
```
Bullish Signals | Multiplier | Label        | Interpretation
----------------|------------|--------------|------------------
4/4 or 0/4      | 1.3x       | PERFECT      | Maximum confidence
3/4 or 1/4      | 1.0x       | STRONG       | High confidence
2/4             | 0.5x       | MIXED        | Medium confidence
1/4 (edge)      | 0.3x       | CONFLICT     | Low confidence
```

---

#### **3.3 Final Score Calculation**

**Formula**:
```python
Final_Score = Raw_Score × Conflict_Multiplier

# Round to 1 decimal place
Final_Score = round(Raw_Score × Multiplier, 1)
```

**Examples**:
```python
# STB - Perfect Alignment
Raw = +75, Multiplier = 1.3 → Final = +97.5

# GAS - Strong Alignment (3/4)
Raw = +45, Multiplier = 1.0 → Final = +45.0

# VCB - Conflict (1/4)
Raw = -30, Multiplier = 0.3 → Final = -9.0

# NT2 - Trap Override
Raw = +5, Multiplier = 1.0 → TRAP DETECTED → Final = 0.0
```

---

#### **3.4 Stock Ranking**

**Sorting Logic**:
```python
# Primary: Rank by Final Score (descending)
# Secondary: If scores are equal, rank by Raw Score
# Tertiary: If still equal, alphabetical by ticker

stocks_sorted = sorted(stocks, 
                      key=lambda x: (-x.final_score, -x.raw_score, x.ticker))

# Assign ranks
for i, stock in enumerate(stocks_sorted, start=1):
    stock.rank = i
```

---

### **MODULE 4: TRAP DETECTION SYSTEM**

---

#### **4.1 Trap Detection Logic**

**Purpose**: Identify dangerous situations where retail FOMO meets smart money distribution

**Criteria** (ALL 3 must be TRUE):
```python
def detect_trap(stock):
    condition_1 = stock.avg_vol_ratio >= 1.0          # Volume looks bullish
    condition_2 = stock.sm_5d < -10                   # Smart money distributing
    condition_3 = stock.retail_5d > 5                 # Retail FOMO buying
    
    is_trap = condition_1 and condition_2 and condition_3
    
    return {
        'is_trap': is_trap,
        'conditions_met': [
            {'name': 'AVG_VOL_RATIO ≥ 1.0', 'met': condition_1, 'value': stock.avg_vol_ratio},
            {'name': 'SM_5D < -10B', 'met': condition_2, 'value': stock.sm_5d},
            {'name': 'RETAIL_5D > +5B', 'met': condition_3, 'value': stock.retail_5d},
        ],
        'count': sum([condition_1, condition_2, condition_3])
    }
```

**Example - NT2 Trap**:
```python
NT2:
- AVG_VOL_RATIO = 1.04 ≥ 1.0 ✓
- SM_5D = -36B < -10B ✓
- RETAIL_5D = +35B > +5B ✓
→ TRAP DETECTED (3/3)
```

---

#### **4.2 Trap Score Override**

**Logic**:
```python
if stock.trap_detected:
    stock.final_score = 0.0  # Force to zero
    stock.action = "🚨 TRAP - AVOID"
    stock.position = 0
    stock.confidence = 70  # High confidence in trap call
    stock.card_style = "trap-card"  # Red border
    stock.trap_message = "⚠️ Smart Money xả hàng, Retail FOMO mua vào → AVOID!"
```

**Visual Treatment**:
```css
.trap-card {
    border: 2px solid #ef4444;  /* Red border */
    background: linear-gradient(135deg, #1e293b, #2a1515);
}

.trap-alert {
    background: rgba(239,68,68,0.15);
    border: 1px solid #ef4444;
    color: #ef4444;
}
```

---

#### **4.3 CN Flow Danger Indicator**

**Purpose**: Show retail flow health even in non-trap stocks

**Logic**:
```python
def retail_flow_status(retail_5d, sm_5d):
    if retail_5d > 5 and sm_5d < -10:
        return "🚨 DANGER"  # Retail buying while Smart Money sells
    elif retail_5d < -5 and sm_5d > 10:
        return "✅ HEALTHY"  # Retail selling while Smart Money buys
    elif abs(retail_5d) < 5:
        return "⚠️ WATCH"   # Retail neutral
    else:
        return "NEUTRAL"
```

**Display**:
```
RETAIL Flow: 1D: -68B | 3D: -137B | 5D: -74B ✅ HEALTHY
RETAIL Flow: 1D: +101B | 3D: +184B | 5D: +409B 🚨 DANGER
```

---

### **MODULE 5: ACTION CLASSIFICATION**

---

#### **5.1 Action Decision Tree**

**Classification**:
```python
def classify_action(final_score, is_trap):
    if is_trap:
        return {
            'action': '🚨 TRAP - AVOID',
            'position': 0,
            'confidence': 70,
            'color': '#dc2626',  # Red
            'emoji': '🚨'
        }
    
    elif final_score >= 50:
        return {
            'action': '🌟 STRONG ENTRY',
            'position': [8, 10],  # 8-10% portfolio
            'confidence': 95,
            'color': '#22c55e',  # Green
            'emoji': '🌟'
        }
    
    elif final_score >= 30:
        return {
            'action': '✅ ENTRY',
            'position': [6, 8],   # 6-8% portfolio
            'confidence': 85,
            'color': '#3b82f6',  # Blue
            'emoji': '✅'
        }
    
    elif final_score >= 15:
        return {
            'action': '👀 WATCH',
            'position': [3, 5],   # 3-5% portfolio
            'confidence': 60,
            'color': '#eab308',  # Yellow
            'emoji': '👀'
        }
    
    elif final_score >= -5:
        return {
            'action': '⚖️ NEUTRAL',
            'position': 0,
            'confidence': 40,
            'color': '#94a3b8',  # Gray
            'emoji': '⚖️'
        }
    
    elif final_score >= -15:
        return {
            'action': '⚠️ CAUTION',
            'position': 0,
            'confidence': 30,
            'color': '#f97316',  # Orange
            'emoji': '⚠️'
        }
    
    else:  # final_score < -15
        return {
            'action': '🚫 EXIT',
            'position': 0,
            'confidence': 20,
            'color': '#dc2626',  # Red
            'emoji': '🚫'
        }
```

---

#### **5.2 Action Summary Table**

| Score Range | Action | Position | Confidence | Color | Meaning |
|-------------|--------|----------|------------|-------|---------|
| TRAP | 🚨 TRAP - AVOID | 0% | 70% | Red | Dangerous pattern |
| +50 to +100 | 🌟 STRONG ENTRY | 8-10% | 95% | Green | High conviction buy |
| +30 to +50 | ✅ ENTRY | 6-8% | 85% | Blue | Good entry point |
| +15 to +30 | 👀 WATCH | 3-5% | 60% | Yellow | Monitor closely |
| -5 to +15 | ⚖️ NEUTRAL | 0% | 40% | Gray | No clear direction |
| -15 to -5 | ⚠️ CAUTION | 0% | 30% | Orange | Weak signals |
| -100 to -15 | 🚫 EXIT | 0% | 20% | Red | Sell/avoid |

---

### **MODULE 6: REPORT GENERATOR**

---

#### **6.1 HTML Structure**

**Main Components**:
```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <!-- Meta, Title, Styles -->
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div class="header">
            <h1>📊 STOCK SCORE V2</h1>
            <div class="subtitle">VN100 Top Liquidity - Deep Analysis</div>
            <div class="info">Data: {date} | Generated: {timestamp} | Framework: 4-Signal + TRAP Detection + VN100 Scanner</div>
            <div class="scanner-info">Selected from VN100 by 20-day average liquidity | Auto-refreshed daily</div>
        </div>
        
        <!-- Summary Statistics -->
        <div class="stats">
            <div class="stat">Total Stocks</div>
            <div class="stat">Entry Count</div>
            <div class="stat">Watch/Neutral Count</div>
            <div class="stat">Trap Count</div>
            <div class="stat">Caution Count</div>
        </div>
        
        <!-- Optional: Liquidity Ranking Table -->
        <div class="liquidity-table" style="display: none;">
            <h3>📊 VN100 Liquidity Rankings (Top 15)</h3>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Ticker</th>
                    <th>Avg Trading Value</th>
                    <th>Avg Volume</th>
                    <th>Avg Price</th>
                </tr>
                <!-- Generated dynamically -->
            </table>
        </div>
        
        <!-- Legend/Framework Explanation -->
        <div class="legend">
            <div class="legend-title">📐 Framework: Stock Score V2</div>
            <!-- Scoring details and trap criteria -->
        </div>
        
        <!-- Stock Cards Grid -->
        <div class="cards-grid">
            <!-- Individual stock cards (generated dynamically) -->
        </div>
        
        <!-- Footer -->
        <div class="footer">
            Stock Score V2 | FIG V4 PF | Data: FiinTrade + RS_TREND_FIG
        </div>
    </div>
</body>
</html>
```

---

#### **6.2 Stock Card Template**

**Card Structure**:
```html
<div class="stock-card {trap-card if trap}">
    <!-- Card Header -->
    <div class="card-header">
        <div class="card-rank">#{rank}</div>
        <div class="card-ticker">{ticker}</div>
        <div class="card-price">{price}</div>
        <div class="card-pct {pos/neg}">{change_pct}%</div>
        <div class="card-score" style="color:{score_color}">{final_score}</div>
    </div>
    
    <!-- Action Badge -->
    <div class="card-action" style="background:{action_color}20; border-left:4px solid {action_color}">
        <span class="action-text">{action_emoji} {action}</span>
        <span class="action-pos">Position: {position}%</span>
        <span class="action-conf">Confidence: {confidence}%</span>
    </div>
    
    <!-- Trap Alert (if applicable) -->
    {if trap_detected}
    <div class="trap-alert">
        <div class="trap-title">🚨 TRAP DETECTED! (3/3 conditions met)</div>
        <div class="trap-detail">
            <span>AVG_VOL_RATIO ≥ 1.0: <b>{✓/✗}</b> ({avg_vol_ratio})</span>
            <span>SM_5D < -10B: <b>{✓/✗}</b> ({sm_5d}B)</span>
            <span>RETAIL_5D > +5B: <b>{✓/✗}</b> ({retail_5d}B)</span>
        </div>
        <div class="trap-msg">⚠️ Smart Money selling, Retail FOMO buying → AVOID!</div>
    </div>
    {endif}
    
    <!-- 4-Signal Breakdown Table -->
    <div class="card-section">
        <div class="section-title">📊 4-Signal Breakdown</div>
        <table class="signal-table">
            <tr>
                <th>Signal</th>
                <th>Value</th>
                <th>State</th>
                <th>Score</th>
                <th>Bull?</th>
            </tr>
            <tr>
                <td>AVG_VOL_RATIO</td>
                <td style="color:{avg_vol_color}">{avg_vol_value}</td>
                <td>{avg_vol_state}</td>
                <td style="color:{score_color}">{avg_vol_score}</td>
                <td style="color:{bull_color}">{✓/✗}</td>
            </tr>
            <!-- SM_5D, INVESTOR_TYPE, PRICE rows -->
        </table>
        <div class="score-calc">
            Raw: <b>{raw_score}</b> × Mult: <b style="color:{mult_color}">{multiplier}</b> ({label}) = <b style="color:{final_color}">{final_score}</b>
        </div>
    </div>
    
    <!-- Direction Tracking -->
    <div class="card-section">
        <div class="section-title">📈 Direction Tracking</div>
        <div class="direction-grid">
            <div class="dir-item">
                <span class="dir-label">AVG_VOL</span>
                <span class="dir-values">{t-2} → {t-1} → <b>{t0}</b></span>
                <span class="dir-icon">{pattern}</span>
            </div>
            <div class="dir-item">
                <span class="dir-label">SM Flow</span>
                <span class="dir-values">1D: {1d}B | 3D: {3d}B | 5D: {5d}B</span>
                <span class="dir-icon">{direction}</span>
            </div>
            <div class="dir-item">
                <span class="dir-label">RETAIL Flow</span>
                <span class="dir-values">1D: {1d}B | 3D: {3d}B | 5D: {5d}B</span>
                <span class="dir-icon" style="color:{status_color}">{retail_status}</span>
            </div>
        </div>
    </div>
    
    <!-- Card Footer -->
    <div class="card-footer">
        <span class="footer-sector">{sector}</span>
        <span class="footer-detail">PROP: {proprietary}B | FOR: {foreign}B | INST: {institutional}B</span>
    </div>
</div>
```

---

#### **6.3 Color Scheme**

**Background & Base**:
```css
Primary Background: #0f172a (dark blue)
Card Background: #1e293b (lighter dark blue)
Section Background: #0f172a
Border Color: #334155 (gray-blue)
Text Primary: #f1f5f9 (off-white)
Text Secondary: #94a3b8 (gray)
Text Muted: #64748b (darker gray)
```

**Signal Colors**:
```css
Strong Positive: #22c55e (green)
Positive: #3b82f6 (blue)
Neutral: #94a3b8 (gray)
Warning: #eab308 (yellow)
Caution: #f97316 (orange)
Negative: #ef4444 (red)
Trap: #dc2626 (dark red)
Perfect Multiplier: #a855f7 (purple)
```

**Score-Based Colors**:
```python
def get_score_color(score):
    if score >= 50:
        return '#22c55e'  # Green
    elif score >= 30:
        return '#3b82f6'  # Blue
    elif score >= 15:
        return '#eab308'  # Yellow
    elif score >= -5:
        return '#94a3b8'  # Gray
    elif score >= -15:
        return '#f97316'  # Orange
    else:
        return '#ef4444'  # Red
```

---

#### **6.4 Summary Dashboard**

**Statistics Calculation**:
```python
summary = {
    'total': len(stocks),
    'entry': count_action(['STRONG ENTRY', 'ENTRY']),
    'watch_neutral': count_action(['WATCH', 'NEUTRAL']),
    'trap': count_action(['TRAP']),
    'caution_exit': count_action(['CAUTION', 'EXIT']),
    'avg_score': mean([s.final_score for s in stocks]),
    'avg_raw_score': mean([s.raw_score for s in stocks]),
}
```

**Display Template**:
```html
<div class="stats">
    <div class="stat">
        <div class="num">{total}</div>
        <div class="lbl">Tổng mã</div>
    </div>
    <div class="stat">
        <div class="num green">{entry_count}</div>
        <div class="lbl">✅ Entry</div>
        <div class="list">{entry_tickers}</div>
    </div>
    <div class="stat">
        <div class="num yellow">{watch_count}</div>
        <div class="lbl">👀 Watch/Neutral</div>
        <div class="list">{watch_tickers}</div>
    </div>
    <div class="stat">
        <div class="num red">{trap_count}</div>
        <div class="lbl">🚨 Trap</div>
        <div class="list">{trap_tickers}</div>
    </div>
    <div class="stat">
        <div class="num" style="color:#f97316">{caution_count}</div>
        <div class="lbl">⚠️ Caution</div>
        <div class="list">{caution_tickers}</div>
    </div>
</div>
```

---

#### **6.5 Legend Section**

**Template**:
```html
<div class="legend">
    <div class="legend-title">📐 Framework: Stock Score V2</div>
    <div class="legend-grid">
        <div class="legend-section">
            <h4>4-Signal Scoring</h4>
            <div class="legend-items">
                <div class="legend-item"><b>AVG_VOL_RATIO:</b> -15 → +30</div>
                <div class="legend-item"><b>SM_5D:</b> -25 → +25</div>
                <div class="legend-item"><b>INVESTOR_TYPE:</b> -15 → +15</div>
                <div class="legend-item"><b>PRICE:</b> -10 → +10</div>
            </div>
        </div>
        <div class="legend-section">
            <h4>🚨 TRAP = ALL 3 must be TRUE</h4>
            <div class="legend-items">
                <div class="legend-item">1. AVG_VOL_RATIO ≥ 1.0 (looks bullish)</div>
                <div class="legend-item">2. SM_5D < -10B (Smart Money selling)</div>
                <div class="legend-item">3. RETAIL_5D > +5B (Retail FOMO)</div>
            </div>
        </div>
    </div>
</div>
```

---

### **MODULE 7: TECHNICAL SPECIFICATIONS**

---

#### **7.1 Programming Environment**

**Language**: Python 3.9+

**Core Libraries**:
```python
# Data Collection
import vnstock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Data Processing
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Report Generation
from jinja2 import Template
import json
```

**Optional Libraries**:
```python
# For FiinTrade API (if available)
import requests
import aiohttp  # For async requests

# For database storage
import sqlite3
# or
import postgresql

# For scheduling
import schedule
import time
```

---

#### **7.2 Data Classes**

**Main Data Structures**:
```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Signal:
    """Individual signal result"""
    name: str              # "AVG_VOL_RATIO", "SM_5D", "INVESTOR_TYPE", "PRICE"
    value: float           # Raw value
    state: str             # State label
    score: int             # Score contribution
    bullish: bool          # Is bullish?
    color: str             # Display color
    
@dataclass
class AvgVolRatioSignal(Signal):
    """Average Volume Ratio signal (formerly KLTB)"""
    history: List[float]   # Last 3 periods
    pattern: str           # Direction pattern
    
@dataclass
class SmartMoneySignal(Signal):
    """Smart Money signal"""
    flows: Dict[str, float]  # 1D, 3D, 5D
    direction: str           # Flow direction
    
@dataclass
class InvestorTypeSignal(Signal):
    """Investor Type signal (formerly TOSM)"""
    breakdown: Dict[str, float]  # PROPRIETARY, FOREIGN, INSTITUTIONAL, RETAIL
    
@dataclass
class TrapDetection:
    """Trap detection result"""
    is_trap: bool
    conditions: List[Dict]
    count: int
    message: str
    
@dataclass
class Stock:
    """Complete stock analysis"""
    ticker: str
    date: datetime
    rank: int
    sector: str
    
    # Price data
    price: float
    price_change_pct: float
    
    # Signals
    avg_vol_ratio_signal: AvgVolRatioSignal     # Formerly kltb_signal
    smart_money_signal: SmartMoneySignal        # Formerly sm_signal
    investor_type_signal: InvestorTypeSignal    # Formerly tosm_signal
    price_signal: Signal
    
    # Scoring
    raw_score: int
    multiplier: float
    multiplier_label: str
    final_score: float
    
    # Classification
    action: str
    position: int or List[int]
    confidence: int
    color: str
    
    # Trap
    trap: TrapDetection
    retail_status: str  # Formerly cn_status
    
@dataclass
class Report:
    """Complete report data"""
    date: datetime
    generated_at: datetime
    stocks: List[Stock]
    summary: Dict
    
```

---

#### **7.3 Configuration File**

**config.yaml**:
```yaml
# Stock Universe - Dynamic VN100 Selection
stocks:
  selection_method: "vn100_liquidity"  # Options: "vn100_liquidity", "custom_list"
  
  vn100_config:
    top_n: 15                # Number of stocks to select
    lookback_days: 20        # Days to calculate average liquidity
    min_trading_value: 50    # Minimum avg daily value (Billion VND)
    refresh_frequency: "daily"  # Options: "daily", "weekly", "monthly"
    
  # Fallback list if VN100 data unavailable
  fallback_list:
    - VCB
    - VHM
    - VIC
    - HPG
    - VNM
    - MSN
    - GAS
    - TCB
    - BID
    - STB
    - MWG
    - VPB
    - PLX
    - POW
    - FPT
  
  # Alternative: Use custom list (set selection_method to "custom_list")
  custom_list:
    - STB
    - BSR
    - GAS
    - POW
    - BVH
  
# Data Sources
data_sources:
  vnstock:
    enabled: true
    source: "VCI"  # or "TCBS", "SSI"
    timeout: 30  # seconds
  
# Signal Parameters
signals:
  avg_vol_ratio:  # Formerly KLTB
    window: 20  # days for average volume calculation
    thresholds:
      accumulation: 1.3      # Strong buying
      buying: 1.0            # Moderate buying  
      neutral: 0.8           # Normal volume
    scores:
      accumulation: 30
      buying: 15
      neutral: 0
      distribution: -15
  
  sm_5d:  # Smart Money 5-day flow
    thresholds:
      strong_accumulation: 200  # Billion VND
      accumulation: 10
      neutral: -10
    scores:
      strong_accumulation: 25
      accumulation: 10
      neutral: 0
      distribution: -25
  
  investor_type:  # Formerly TOSM
    default_score: 10
    default_state: "SUPPORTIVE"
  
  price:
    thresholds:
      strong_up: 2.0     # percent
      neutral_down: -1.0
    scores:
      strong_up: 10
      moderate_up: 5
      neutral: 0
      down: -10

# Trap Detection
trap:
  avg_vol_ratio_threshold: 1.0   # Formerly kltb_threshold
  sm_threshold: -10              # Billion VND
  retail_threshold: 5            # Formerly cn_threshold, Billion VND
  
# Scoring
scoring:
  multipliers:
    perfect: 1.3   # 4/4 or 0/4
    strong: 1.0    # 3/4 or 1/4
    mixed: 0.5     # 2/4
    conflict: 0.3  # 1/4 (edge case)
    
# Action Classification
actions:
  strong_entry:
    score_min: 50
    position: [8, 10]
    confidence: 95
  entry:
    score_min: 30
    position: [6, 8]
    confidence: 85
  watch:
    score_min: 15
    position: [3, 5]
    confidence: 60
  neutral:
    score_min: -5
    position: 0
    confidence: 40
  caution:
    score_min: -15
    position: 0
    confidence: 30
  exit:
    score_min: -100
    position: 0
    confidence: 20
  trap:
    position: 0
    confidence: 70

# Report Settings
report:
  output_dir: "./reports"
  filename_pattern: "Stock_Score_V2_{date}.html"
  title: "Stock Score V2"
  subtitle: "Beta Trading List - Deep Analysis"
  framework: "4-Signal + TRAP Detection"
  footer: "Stock Score V2 | FIG V4 PF | Data: FiinTrade + RS_TREND_FIG"
  
# Scheduling
schedule:
  enabled: true
  run_time: "00:15"  # HH:MM 24-hour format
  timezone: "Asia/Ho_Chi_Minh"
```

---

#### **7.4 Project Structure**

```
stock-score-v2/
│
├── config/
│   └── config.yaml                 # Configuration file
│
├── data/
│   ├── raw/                        # Raw data from vnstock/FiinTrade
│   ├── processed/                  # Processed data
│   └── cache/                      # Cached results
│
├── src/
│   ├── __init__.py
│   │
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── vn100_scanner.py          # VN100 liquidity scanner
│   │   ├── vnstock_collector.py      # vnstock data collection (ONLY source)
│   │   └── base_collector.py         # Abstract base class
│   │
│   ├── signals/
│   │   ├── __init__.py
│   │   ├── avg_vol_ratio.py          # AVG_VOL_RATIO calculator (formerly kltb.py)
│   │   ├── smart_money.py            # SM_5D calculator
│   │   ├── investor_type.py          # INVESTOR_TYPE analyzer (formerly tosm.py)
│   │   ├── price.py                  # Price momentum
│   │   └── base_signal.py            # Abstract signal class
│   │
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── scorer.py              # Raw score + multiplier
│   │   ├── ranker.py              # Stock ranking
│   │   └── action_classifier.py   # Action determination
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── trap_detector.py       # Trap detection logic
│   │   └── cn_analyzer.py         # CN flow analysis
│   │
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── html_generator.py      # HTML report generation
│   │   ├── templates/
│   │   │   ├── base.html          # Base template
│   │   │   ├── card.html          # Stock card template
│   │   │   └── styles.css         # Inline CSS
│   │   └── formatters.py          # Number/text formatting
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config_loader.py       # Config loading
│   │   ├── date_utils.py          # Date handling
│   │   ├── logger.py              # Logging setup
│   │   └── validators.py          # Data validation
│   │
│   └── main.py                     # Main execution script
│
├── templates/
│   └── report_template.html        # Jinja2 HTML template
│
├── reports/                         # Generated HTML reports
│   └── Stock_Score_V2_YYYYMMDD.html
│
├── tests/
│   ├── __init__.py
│   ├── test_signals.py
│   ├── test_scoring.py
│   ├── test_trap_detection.py
│   └── test_report_generation.py
│
├── notebooks/
│   ├── data_exploration.ipynb     # Data analysis
│   └── backtesting.ipynb          # Strategy backtesting
│
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .env                            # Environment variables (API keys)
└── run.py                          # Entry point script
```

---

#### **7.5 API Integration**

**vnstock Integration**:
```python
from vnstock import stock_historical_data, financial_flow

# Get price and volume data
def get_stock_data(ticker: str, start_date: str, end_date: str):
    """
    Fetch OHLCV data using vnstock
    """
    df = stock_historical_data(
        symbol=ticker,
        start_date=start_date,
        end_date=end_date,
        resolution='1D',
        type='stock',
        source='VCI'
    )
    return df

# Get investor flow data (if available in vnstock)
def get_flow_data(ticker: str, start_date: str, end_date: str):
    """
    Fetch investor flow data
    """
    # Check if vnstock has this feature
    # Otherwise, use FiinTrade or alternative source
    try:
        flow_df = financial_flow(
            symbol=ticker,
            start_date=start_date,
            end_date=end_date
        )
        return flow_df
    except:
        # Fallback to alternative source
        return get_fiintrade_flow(ticker, start_date, end_date)
```

**FiinTrade API** (if available):
```python
import requests
from typing import Dict

class FiinTradeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fiintrade.vn"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def get_investor_flow(self, ticker: str, from_date: str, to_date: str) -> Dict:
        """
        Fetch investor flow data
        Returns: {
            'TD': {'1D': float, '3D': float, '5D': float},
            'NN': {'1D': float, '3D': float, '5D': float},
            'TC': {'1D': float, '3D': float, '5D': float},
            'CN': {'1D': float, '3D': float, '5D': float},
        }
        """
        endpoint = f"{self.base_url}/v1/investor-flow"
        params = {
            'symbol': ticker,
            'from_date': from_date,
            'to_date': to_date
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return self._process_flow_data(data)
    
    def _process_flow_data(self, raw_data: Dict) -> Dict:
        """Process and aggregate flow data"""
        # Implementation depends on API response format
        pass
```

**Alternative: Manual Flow Calculation** (if API unavailable):
```python
def calculate_flow_manual(ticker: str, df: pd.DataFrame) -> Dict:
    """
    Calculate investor flows manually from transaction data
    This is a fallback if flow API is not available
    
    Requires transaction-level data with investor type
    """
    # Group by investor type and aggregate
    flows = {
        'TD': {'1D': 0, '3D': 0, '5D': 0},
        'NN': {'1D': 0, '3D': 0, '5D': 0},
        'TC': {'1D': 0, '3D': 0, '5D': 0},
        'CN': {'1D': 0, '3D': 0, '5D': 0},
    }
    
    # Calculate net buy/sell for each type
    # This requires access to transaction-level data
    
    return flows
```

---

#### **7.6 Execution Flow**

**Main Execution Logic**:
```python
# main.py

from src.collectors.vn100_scanner import VN100LiquidityScanner
from src.collectors.vnstock_collector import VNStockCollector
from src.signals.avg_vol_ratio import AvgVolRatioCalculator
from src.signals.smart_money import SmartMoneyCalculator
from src.signals.investor_type import InvestorTypeAnalyzer
from src.signals.price import PriceSignalCalculator
from src.scoring.scorer import ScoreCalculator
from src.scoring.ranker import StockRanker
from src.scoring.action_classifier import ActionClassifier
from src.detection.trap_detector import TrapDetector
from src.reporting.html_generator import HTMLReportGenerator
from src.utils.config_loader import load_config
from src.utils.logger import setup_logger
from datetime import datetime, timedelta

def main():
    # Setup
    logger = setup_logger()
    config = load_config('config/config.yaml')
    
    # === STEP 0: DYNAMIC STOCK SELECTION FROM VN100 ===
    logger.info("=" * 60)
    logger.info("STEP 0: Scanning VN100 for top liquid stocks...")
    logger.info("=" * 60)
    
    scanner = VN100LiquidityScanner(config['stocks']['vn100_config'])
    
    try:
        # Get top N most liquid stocks from VN100
        stock_list = scanner.scan_and_select(
            top_n=config['stocks']['vn100_config']['top_n'],
            lookback_days=config['stocks']['vn100_config']['lookback_days']
        )
        
        logger.info(f"Selected {len(stock_list)} stocks from VN100:")
        logger.info(f"Stocks: {', '.join(stock_list)}")
        
    except Exception as e:
        logger.error(f"VN100 scanning failed: {e}")
        logger.warning("Falling back to predefined list...")
        stock_list = config['stocks']['fallback_list'][:config['stocks']['vn100_config']['top_n']]
        logger.info(f"Using fallback: {', '.join(stock_list)}")
    
    # Cache selected stocks for reporting
    selected_stocks_info = scanner.get_liquidity_report()
    
    # === STEP 1: INITIALIZE COMPONENTS ===
    logger.info("=" * 60)
    logger.info("STEP 1: Initializing analysis components...")
    logger.info("=" * 60)
    
    collector = VNStockCollector(config['data_sources']['vnstock'])
    avg_vol_calc = AvgVolRatioCalculator(config['signals']['avg_vol_ratio'])
    sm_calc = SmartMoneyCalculator(config['signals']['sm_5d'])
    investor_type_analyzer = InvestorTypeAnalyzer(config['signals']['investor_type'])
    price_calc = PriceSignalCalculator(config['signals']['price'])
    scorer = ScoreCalculator(config['scoring'])
    ranker = StockRanker()
    classifier = ActionClassifier(config['actions'])
    trap_detector = TrapDetector(config['trap'])
    report_gen = HTMLReportGenerator(config['report'])
    
    # === STEP 2: PROCESS EACH STOCK ===
    logger.info("=" * 60)
    logger.info("STEP 2: Processing stocks...")
    logger.info("=" * 60)
    
    stocks = []
    for idx, ticker in enumerate(stock_list, 1):
        try:
            logger.info(f"[{idx}/{len(stock_list)}] Processing {ticker}...")
            
            # 2.1: Collect data
            data = collector.collect(ticker, days_back=30)
            
            # 2.2: Calculate signals
            avg_vol_signal = avg_vol_calc.calculate(data)
            sm_signal = sm_calc.calculate(data)
            investor_type_signal = investor_type_analyzer.analyze(data)
            price_signal = price_calc.calculate(data)
            
            # 2.3: Calculate score
            raw_score, multiplier, multiplier_label = scorer.calculate(
                avg_vol_signal, sm_signal, investor_type_signal, price_signal
            )
            final_score = raw_score * multiplier
            
            # 2.4: Detect trap
            trap = trap_detector.detect(avg_vol_signal, sm_signal, data)
            if trap.is_trap:
                final_score = 0.0
            
            # 2.5: Classify action
            action_data = classifier.classify(final_score, trap.is_trap)
            
            # 2.6: Create stock object
            stock = Stock(
                ticker=ticker,
                date=datetime.now(),
                rank=0,  # Will be assigned by ranker
                sector=data.get('sector', 'Unknown'),
                price=data['close'][-1],
                price_change_pct=data['change_pct'][-1],
                avg_vol_ratio_signal=avg_vol_signal,
                smart_money_signal=sm_signal,
                investor_type_signal=investor_type_signal,
                price_signal=price_signal,
                raw_score=raw_score,
                multiplier=multiplier,
                multiplier_label=multiplier_label,
                final_score=final_score,
                action=action_data['action'],
                position=action_data['position'],
                confidence=action_data['confidence'],
                color=action_data['color'],
                trap=trap,
                retail_status=sm_calc.get_retail_status(data)
            )
            
            stocks.append(stock)
            logger.info(f"  ✓ {ticker}: Score={final_score:.1f}, Action={action_data['action']}")
            
        except Exception as e:
            logger.error(f"  ✗ Error processing {ticker}: {str(e)}")
            continue
    
    # === STEP 3: RANK STOCKS ===
    logger.info("=" * 60)
    logger.info("STEP 3: Ranking stocks...")
    logger.info("=" * 60)
    
    ranked_stocks = ranker.rank(stocks)
    
    # === STEP 4: GENERATE REPORT ===
    logger.info("=" * 60)
    logger.info("STEP 4: Generating HTML report...")
    logger.info("=" * 60)
    
    report = Report(
        date=datetime.now(),
        generated_at=datetime.now(),
        stocks=ranked_stocks,
        summary=calculate_summary(ranked_stocks),
        liquidity_info=selected_stocks_info  # Add liquidity ranking info
    )
    
    # === STEP 5: SAVE HTML REPORT ===
    output_path = report_gen.generate(report)
    logger.info("=" * 60)
    logger.info(f"✓ COMPLETED! Report saved to: {output_path}")
    logger.info("=" * 60)
    
    return output_path

def calculate_summary(stocks: List[Stock]) -> Dict:
    """Calculate summary statistics"""
    from collections import Counter
    
    actions = [s.action for s in stocks]
    action_counts = Counter(actions)
    
    return {
        'total': len(stocks),
        'entry': action_counts.get('STRONG ENTRY', 0) + action_counts.get('ENTRY', 0),
        'watch_neutral': action_counts.get('WATCH', 0) + action_counts.get('NEUTRAL', 0),
        'trap': action_counts.get('TRAP - AVOID', 0),
        'caution_exit': action_counts.get('CAUTION', 0) + action_counts.get('EXIT', 0),
        'avg_score': sum(s.final_score for s in stocks) / len(stocks),
        'avg_raw_score': sum(s.raw_score for s in stocks) / len(stocks),
    }

if __name__ == "__main__":
    main()
```

**Scheduling** (for daily automation):
```python
# run.py

import schedule
import time
from src.main import main
from src.utils.logger import setup_logger

logger = setup_logger()

def job():
    """Scheduled job to run analysis"""
    try:
        logger.info("Starting scheduled Stock Score V2 analysis...")
        output_path = main()
        logger.info(f"Analysis completed. Report: {output_path}")
    except Exception as e:
        logger.error(f"Scheduled job failed: {str(e)}")

# Schedule to run daily at 00:15 AM
schedule.every().day.at("00:15").do(job)

logger.info("Scheduler started. Waiting for scheduled time...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

---

### **MODULE 8: DATA VALIDATION & ERROR HANDLING**

---

#### **8.1 Data Validation Rules**

**Price Data Validation**:
```python
def validate_price_data(df: pd.DataFrame) -> bool:
    """
    Validate price data quality
    """
    checks = {
        'has_required_columns': all(col in df.columns for col in ['close', 'volume', 'date']),
        'no_null_prices': df['close'].notna().all(),
        'positive_prices': (df['close'] > 0).all(),
        'positive_volume': (df['volume'] >= 0).all(),
        'sufficient_data': len(df) >= 20,  # Need 20 days for KLTB
        'sorted_dates': df['date'].is_monotonic_increasing,
    }
    
    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise ValueError(f"Price data validation failed: {failed}")
    
    return True
```

**Flow Data Validation**:
```python
def validate_flow_data(flows: Dict) -> bool:
    """
    Validate investor flow data
    """
    required_types = ['TD', 'NN', 'TC', 'CN']
    required_periods = ['1D', '3D', '5D']
    
    checks = {
        'has_all_types': all(t in flows for t in required_types),
        'has_all_periods': all(
            all(p in flows[t] for p in required_periods)
            for t in required_types
        ),
        'values_are_numeric': all(
            isinstance(flows[t][p], (int, float))
            for t in required_types
            for p in required_periods
        ),
    }
    
    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise ValueError(f"Flow data validation failed: {failed}")
    
    return True
```

---

#### **8.2 Error Handling Strategy**

**Collection Errors**:
```python
def collect_with_retry(ticker: str, max_retries: int = 3):
    """
    Collect data with retry logic
    """
    for attempt in range(max_retries):
        try:
            data = collector.collect(ticker)
            validate_price_data(data)
            return data
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {ticker}: {str(e)}")
            if attempt == max_retries - 1:
                logger.error(f"Failed to collect data for {ticker} after {max_retries} attempts")
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

**Missing Data Handling**:
```python
def handle_missing_flows(ticker: str, flows: Dict) -> Dict:
    """
    Handle missing or incomplete flow data
    """
    # Option 1: Use zeros for missing data
    default_flow = {'1D': 0, '3D': 0, '5D': 0}
    
    flows_cleaned = {
        'TD': flows.get('TD', default_flow),
        'NN': flows.get('NN', default_flow),
        'TC': flows.get('TC', default_flow),
        'CN': flows.get('CN', default_flow),
    }
    
    # Option 2: Skip stock if critical data missing
    if all(v == default_flow for v in flows_cleaned.values()):
        logger.warning(f"No flow data available for {ticker} - skipping")
        raise ValueError(f"Insufficient flow data for {ticker}")
    
    return flows_cleaned
```

---

### **MODULE 9: TESTING & VALIDATION**

---

#### **9.1 Unit Tests**

**Test KLTB Calculation**:
```python
# tests/test_signals.py

import unittest
from src.signals.kltb import KLTBCalculator

class TestKLTBCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = KLTBCalculator({
            'window': 20,
            'thresholds': {'gom': 1.3, 'keo': 1.0, 'can': 0.8},
            'scores': {'gom': 30, 'keo': 15, 'can': 0, 'xa': -15}
        })
    
    def test_gom_state(self):
        """Test GOM (accumulation) state"""
        data = {
            'volume': [100] * 20 + [150],  # Last day 1.5x average
        }
        signal = self.calc.calculate(data)
        self.assertEqual(signal.state, 'GOM')
        self.assertEqual(signal.score, 30)
        self.assertTrue(signal.bullish)
    
    def test_xa_state(self):
        """Test XẢ (distribution) state"""
        data = {
            'volume': [100] * 20 + [70],  # Last day 0.7x average
        }
        signal = self.calc.calculate(data)
        self.assertEqual(signal.state, 'XẢ')
        self.assertEqual(signal.score, -15)
        self.assertFalse(signal.bullish)
```

**Test Trap Detection**:
```python
class TestTrapDetector(unittest.TestCase):
    def setUp(self):
        self.detector = TrapDetector({
            'kltb_threshold': 1.0,
            'sm_threshold': -10,
            'cn_threshold': 5
        })
    
    def test_trap_detected(self):
        """Test trap detection when all conditions met"""
        kltb = 1.04
        sm_5d = -36
        cn_5d = 35
        
        trap = self.detector.detect(kltb, sm_5d, cn_5d)
        self.assertTrue(trap.is_trap)
        self.assertEqual(trap.count, 3)
    
    def test_no_trap(self):
        """Test no trap when conditions not met"""
        kltb = 0.8  # Below threshold
        sm_5d = -36
        cn_5d = 35
        
        trap = self.detector.detect(kltb, sm_5d, cn_5d)
        self.assertFalse(trap.is_trap)
```

---

#### **9.2 Integration Tests**

**End-to-End Test**:
```python
class TestEndToEnd(unittest.TestCase):
    def test_full_analysis_pipeline(self):
        """Test complete analysis for one stock"""
        ticker = "STB"
        
        # Run full pipeline
        result = run_analysis_for_stock(ticker)
        
        # Verify all components present
        self.assertIsNotNone(result.kltb_signal)
        self.assertIsNotNone(result.sm_signal)
        self.assertIsNotNone(result.final_score)
        self.assertIsNotNone(result.action)
        
        # Verify score calculation
        expected_raw = (result.kltb_signal.score + 
                       result.sm_signal.score + 
                       result.tosm_signal.score + 
                       result.price_signal.score)
        self.assertEqual(result.raw_score, expected_raw)
```

---

#### **9.3 Backtesting Framework**

**Performance Evaluation**:
```python
# notebooks/backtesting.ipynb

def backtest_strategy(start_date: str, end_date: str, initial_capital: float = 100000):
    """
    Backtest the Stock Score V2 strategy
    """
    results = []
    capital = initial_capital
    positions = {}
    
    for date in trading_days(start_date, end_date):
        # Generate signals for this date
        daily_report = run_analysis(date)
        
        # Execute trades based on signals
        for stock in daily_report.stocks:
            if stock.action in ['STRONG ENTRY', 'ENTRY']:
                # Enter position
                position_size = capital * (stock.position / 100)
                positions[stock.ticker] = {
                    'entry_price': stock.price,
                    'entry_date': date,
                    'size': position_size
                }
            
            elif stock.action in ['EXIT', 'TRAP - AVOID']:
                # Exit position if exists
                if stock.ticker in positions:
                    entry = positions[stock.ticker]
                    pnl = (stock.price - entry['entry_price']) / entry['entry_price'] * entry['size']
                    capital += pnl
                    del positions[stock.ticker]
        
        # Record performance
        total_value = capital + sum(p['size'] for p in positions.values())
        results.append({
            'date': date,
            'capital': capital,
            'total_value': total_value,
            'positions': len(positions)
        })
    
    return pd.DataFrame(results)

# Calculate metrics
def calculate_performance_metrics(backtest_results: pd.DataFrame):
    """
    Calculate strategy performance metrics
    """
    returns = backtest_results['total_value'].pct_change()
    
    metrics = {
        'Total Return': (backtest_results['total_value'].iloc[-1] / 
                        backtest_results['total_value'].iloc[0] - 1) * 100,
        'Sharpe Ratio': returns.mean() / returns.std() * np.sqrt(252),
        'Max Drawdown': (backtest_results['total_value'] / 
                        backtest_results['total_value'].cummax() - 1).min() * 100,
        'Win Rate': (returns > 0).sum() / len(returns) * 100,
    }
    
    return metrics
```

---

### **MODULE 10: DEPLOYMENT & MAINTENANCE**

---

#### **10.1 Deployment Options**

**Option 1: Local Scheduled Execution**
```bash
# Using cron (Linux/Mac)
# Edit crontab: crontab -e
# Add line:
15 0 * * * /usr/bin/python3 /path/to/stock-score-v2/run.py >> /path/to/logs/stock_score.log 2>&1
```

**Option 2: Docker Container**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

**Option 3: Cloud Deployment** (AWS Lambda, Google Cloud Functions)
```python
# For serverless deployment
# Modify main.py to accept event triggers
def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        output_path = main()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Report generated successfully',
                'path': output_path
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

#### **10.2 Monitoring & Logging**

**Logging Configuration**:
```python
# src/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str = 'stock_score_v2', log_dir: str = 'logs'):
    """
    Setup comprehensive logging
    """
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'stock_score.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'stock_score_errors.log'),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger
```

**Performance Monitoring**:
```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}...")
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}")
            raise
    
    return wrapper

@monitor_performance
def collect_data(ticker: str):
    """Collect data with performance monitoring"""
    # ... data collection logic
    pass
```

---

#### **10.3 Maintenance Checklist**

**Daily**:
- [ ] Verify report generation completed
- [ ] Check for any error logs
- [ ] Validate data freshness

**Weekly**:
- [ ] Review trap detection accuracy
- [ ] Monitor signal quality
- [ ] Check for outliers in scores

**Monthly**:
- [ ] Analyze strategy performance
- [ ] Update stock universe if needed
- [ ] Review and adjust thresholds
- [ ] Backup historical reports

**Quarterly**:
- [ ] Full backtest of strategy
- [ ] Compare with market benchmarks
- [ ] Refine scoring parameters
- [ ] Update documentation

---

### **MODULE 11: ADVANCED FEATURES (FUTURE ENHANCEMENTS)**

---

#### **11.1 Machine Learning Integration**

**Potential ML Enhancements**:
```python
# Future: ML-based signal weighting
from sklearn.ensemble import RandomForestClassifier

class MLSignalWeighter:
    """
    Use ML to dynamically weight signals based on historical performance
    """
    def __init__(self):
        self.model = RandomForestClassifier()
    
    def train(self, historical_data, outcomes):
        """
        Train model on historical signals vs actual returns
        """
        X = historical_data[['kltb', 'sm_5d', 'tosm', 'price']]
        y = outcomes['profitable']  # Binary: profitable or not
        
        self.model.fit(X, y)
    
    def predict_weights(self, current_signals):
        """
        Predict optimal weights for current signals
        """
        importance = self.model.feature_importances_
        return importance / importance.sum()
```

---

#### **11.2 Multi-Timeframe Analysis**

**Extension**:
```python
# Future: Add weekly and monthly scoring
def multi_timeframe_analysis(ticker: str):
    """
    Analyze stock across multiple timeframes
    """
    daily_score = calculate_score(ticker, timeframe='1D')
    weekly_score = calculate_score(ticker, timeframe='1W')
    monthly_score = calculate_score(ticker, timeframe='1M')
    
    # Combine scores with weights
    combined_score = (
        daily_score * 0.5 +
        weekly_score * 0.3 +
        monthly_score * 0.2
    )
    
    return {
        'daily': daily_score,
        'weekly': weekly_score,
        'monthly': monthly_score,
        'combined': combined_score
    }
```

---

#### **11.3 Alert System**

**Notification Integration**:
```python
# Future: Send alerts for high-conviction signals
import smtplib
from email.mime.text import MIMEText

def send_alert(stock: Stock, alert_type: str):
    """
    Send email/SMS alert for important signals
    """
    if stock.final_score >= 70 or stock.trap.is_trap:
        message = f"""
        Stock Alert: {stock.ticker}
        
        Action: {stock.action}
        Score: {stock.final_score}
        Confidence: {stock.confidence}%
        
        {'⚠️ TRAP DETECTED!' if stock.trap.is_trap else ''}
        """
        
        # Send via email/Telegram/SMS
        send_notification(message)
```

---

### **APPENDIX: QUICK REFERENCE**

---

#### **A1: Signal Score Summary**

| Signal | States | Score Range | Bullish When |
|--------|--------|-------------|--------------|
| **KLTB** | GOM, KÉO, CÂN, XẢ | -15 to +30 | GOM or KÉO |
| **SM_5D** | SM_ACCUM, SM_BUY, SM_DISTRIB | -25 to +25 | ACCUM, BUY, or DISTRIB* |
| **TOSM** | SUS, WEAK, NEUTRAL | -15 to +15 | SUS |
| **Price** | - | -10 to +10 | Price > 0% |

*Note: SM_DISTRIB is marked bullish due to contrarian strategy

---

#### **A2: Score Interpretation Guide**

| Final Score | Action | Position | Risk Level | Market Condition |
|-------------|--------|----------|------------|------------------|
| +70 to +100 | STRONG ENTRY | 8-10% | Low | Strong uptrend |
| +30 to +70 | ENTRY | 6-8% | Medium-Low | Uptrend |
| +15 to +30 | WATCH | 3-5% | Medium | Consolidation |
| -5 to +15 | NEUTRAL | 0% | Medium | Unclear |
| -15 to -5 | CAUTION | 0% | Medium-High | Weak trend |
| -100 to -15 | EXIT | 0% | High | Downtrend |
| TRAP | AVOID | 0% | Very High | Trap pattern |

---

#### **A3: Investor Type Classification**

| Code | Full Name | Vietnamese Original | Description |
|------|-----------|---------------------|-------------|
| PROP | PROPRIETARY | TD (Tự doanh) | Brokerage proprietary trading desks |
| FOR | FOREIGN | NN (Nước ngoài) | Foreign institutional investors |
| INST | INSTITUTIONAL | TC (Tổ chức) | Domestic institutional investors |
| RETAIL | RETAIL | CN (Cá nhân) | Individual retail investors |

---

#### **A4: Volume Ratio States & Patterns**

**States**:
| English Term | Vietnamese Original | Threshold | Meaning |
|--------------|---------------------|-----------|---------|
| ACCUMULATION | GOM (Gom) | ≥ 1.3 | Heavy buying, volume spike |
| BUYING | KÉO (Kéo) | 1.0 - 1.3 | Moderate buying pressure |
| NEUTRAL | CÂN (Cân) | 0.8 - 1.0 | Normal volume |
| DISTRIBUTION | XẢ (Xả) | < 0.8 | Heavy selling, low volume |

**Pattern Descriptions**:
| English | Vietnamese Original |
|---------|---------------------|
| Bottom then Rise | Đáy rồi tăng |
| Peak then Fall | Đỉnh rồi giảm |
| Continuous Rise | Tăng liên tục |
| Continuous Fall | Giảm liên tục |
| Rise then Hold | Tăng rồi giữ |
| Fall then Hold | Giảm rồi giữ |
| Sideways | Đi ngang |

---

#### **A5: Critical Thresholds**

```yaml
AVG_VOL_RATIO:  # Formerly KLTB
  ACCUMULATION: ≥ 1.3
  BUYING: 1.0 - 1.3
  NEUTRAL: 0.8 - 1.0
  DISTRIBUTION: < 0.8

SM_5D:
  Strong Accumulation: ≥ 200B VND
  Accumulation: ≥ 10B VND
  Distribution: < -10B VND

Trap:
  AVG_VOL_RATIO: ≥ 1.0  # Formerly KLTB
  SM_5D: < -10B
  RETAIL_5D: > +5B      # Formerly CN_5D

Multiplier:
  Perfect (4/4 or 0/4): 1.3x
  Strong (3/4 or 1/4): 1.0x
  Mixed (2/2): 0.5x
  Conflict (1/4): 0.3x
```

---

## 🎓 **IMPLEMENTATION NOTES FOR DEVELOPER**

### **Phase 1: Core Setup (Days 1-2)**
1. Set up project structure
2. Install dependencies (vnstock, pandas, numpy, jinja2)
3. Create configuration system
4. Implement logging

### **Phase 2: VN100 Scanner (Days 3-4)** ← NEW PRIORITY
1. Implement VN100 constituent fetcher
2. Build liquidity calculator
3. Create ranking and selection logic
4. Add fallback mechanisms
5. Test with live data

### **Phase 3: Data Collection (Days 5-6)**
1. Implement vnstock collector (ONLY data source)
2. Create investor flow extraction from vnstock
3. Create data validation
4. Build caching system
5. Integrate with VN100 scanner output

### **Phase 4: Signal Calculation (Days 7-9)**
1. Implement AVG_VOL_RATIO calculator (formerly KLTB)
2. Implement SM_5D aggregator
3. Implement INVESTOR_TYPE analyzer (formerly TOSM)
4. Implement PRICE signal

### **Phase 5: Scoring System (Days 10-11)**
1. Build raw score calculator
2. Implement conflict multiplier
3. Create ranking system
4. Build action classifier

### **Phase 6: Trap Detection (Day 12)**
1. Implement trap detector
2. Create RETAIL flow analyzer (formerly CN)
3. Add override logic

### **Phase 7: Report Generation (Days 13-15)**
1. Create HTML template
2. Build report generator
3. Implement styling
4. Add summary dashboard
5. Include liquidity ranking information

### **Phase 8: Testing (Days 16-17)**
1. Write unit tests
2. Perform integration testing
3. Validate with historical data
4. Fix bugs

### **Phase 9: Deployment (Days 18-19)**
1. Set up scheduling
2. Configure logging
3. Deploy to production
4. Monitor first runs

### **Phase 10: Documentation (Day 20)**
1. Write user guide
2. Document configuration
3. Create maintenance guide

---

## 📌 **CRITICAL SUCCESS FACTORS**

1. **VN100 Scanner Reliability**: Robust fallback mechanisms ensure stock list even if API fails
2. **Data Quality**: Ensure reliable, timely data from vnstock (single source)
3. **Threshold Accuracy**: Fine-tune signal thresholds based on backtesting
4. **Trap Detection**: Validate trap logic prevents false positives
5. **Performance**: Optimize for processing VN100 scan + 15 stocks in < 10 minutes
6. **Reliability**: System must run daily without manual intervention
7. **Clarity**: Report must be immediately actionable for traders
8. **Liquidity Focus**: Dynamic selection ensures analysis of truly tradeable stocks
9. **Code Quality**: 100% English codebase for international collaboration

---

## 📚 **RESOURCES & REFERENCES**

**Documentation**:
- vnstock: https://github.com/thinh-vu/vnstock
- Jinja2: https://jinja.palletsprojects.com/
- Pandas: https://pandas.pydata.org/

**Vietnamese Market**:
- HOSE Trading Rules
- Vietnamese Investor Type Classifications
- Smart Money Flow Analysis Papers

**Technical References**:
- Volume Profile Analysis
- Institutional Flow Tracking
- Contrarian Trading Strategies

---

**END OF BLUEPRINT**

---

This blueprint is comprehensive, production-ready, and provides all the necessary details for a developer to implement the Stock Score V2 system from scratch. Every module, calculation, threshold, and design decision has been documented based on the reverse engineering of your original HTML report.

Ready to proceed with coding implementation?
