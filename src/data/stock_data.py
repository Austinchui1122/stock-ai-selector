"""
股票数据获取模块
"""
import os
from typing import List, Dict, Any

import yfinance as yf
import pandas as pd
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.techindicators import TechIndicators

from config.config import STOCK_DATA, STOCK_FILTERS

class StockDataFetcher:
    def __init__(self):
        """初始化数据获取器"""
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        print(f"API Key 前4位: {self.alpha_vantage_key[:4] if self.alpha_vantage_key else 'None'}")  # 只打印前4位，保護密鑰安全
        
        if not self.alpha_vantage_key:
            raise ValueError("未設置 ALPHA_VANTAGE_API_KEY 環境變量")
            
        try:
            self.fd = FundamentalData(key=self.alpha_vantage_key)
            self.ti = TechIndicators(key=self.alpha_vantage_key)
            print("Alpha Vantage API 初始化成功")
        except Exception as e:
            print(f"Alpha Vantage API 初始化失敗: {str(e)}")
            raise

    def get_stock_price_history(self, symbol: str) -> pd.DataFrame:
        """获取股票历史价格数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            DataFrame包含OHLCV数据
        """
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=f"{STOCK_DATA['lookback_period']}d")
            return df
        except Exception as e:
            print(f"获取{symbol}历史数据失败: {str(e)}")
            return pd.DataFrame()

    def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本面数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            包含基本面数据的字典
        """
        try:
            overview, _ = self.fd.get_company_overview(symbol)
            return {
                'MarketCap': float(overview.get('MarketCapitalization', 0)),
                'ROE': float(overview.get('ReturnOnEquityTTM', 0)),
                'EPS': float(overview.get('EPS', 0)),
                'DebtToEquity': float(overview.get('DebtToEquityRatio', 0)),
                'PE': float(overview.get('PERatio', 0))
            }
        except Exception as e:
            print(f"获取{symbol}基本面数据失败: {str(e)}")
            return {}

    def get_technical_indicators(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """获取技术指标数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            包含各种技术指标的字典
        """
        try:
            # RSI
            rsi_data, _ = self.ti.get_rsi(symbol=symbol, interval='daily')
            
            # MACD
            macd_data, _ = self.ti.get_macd(symbol=symbol)
            
            # SMA
            sma_short, _ = self.ti.get_sma(symbol=symbol, time_period=50)
            sma_long, _ = self.ti.get_sma(symbol=symbol, time_period=200)
            
            return {
                'RSI': rsi_data,
                'MACD': macd_data,
                'SMA_50': sma_short,
                'SMA_200': sma_long
            }
        except Exception as e:
            print(f"获取{symbol}技术指标失败: {str(e)}")
            return {}

    def filter_stocks(self, symbols: List[str]) -> List[str]:
        """根据条件筛选股票
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            符合条件的股票代码列表
        """
        filtered_symbols = []
        for symbol in symbols:
            try:
                fundamental_data = self.get_fundamental_data(symbol)
                if not fundamental_data:
                    continue
                    
                if (fundamental_data['MarketCap'] >= STOCK_DATA['market_cap_min'] and
                    fundamental_data['ROE'] >= STOCK_FILTERS['roe_min'] and
                    fundamental_data['PE'] <= STOCK_FILTERS['pe_max'] and
                    fundamental_data['DebtToEquity'] <= STOCK_FILTERS['debt_equity_max']):
                    filtered_symbols.append(symbol)
            except Exception as e:
                print(f"篩選{symbol}時出錯: {str(e)}")
                continue
                
        return filtered_symbols 