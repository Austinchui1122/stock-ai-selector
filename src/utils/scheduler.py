"""
自动化执行脚本
"""
import schedule
import time
import logging
from datetime import datetime
import os
import pandas as pd

from src.data.stock_data import StockDataFetcher
from src.models.stock_predictor import StockPredictor
from config.config import PATHS

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories():
    """创建必要的目录"""
    for path in PATHS.values():
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f'创建目录: {path}')

def save_results(filtered_symbols: list, predictions: dict):
    """保存选股和预测结果
    
    Args:
        filtered_symbols: 筛选出的股票列表
        predictions: 预测结果字典
    """
    # 保存筛选结果
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # 保存股票列表
    with open(os.path.join(PATHS['results'], f'filtered_stocks_{timestamp}.txt'), 'w') as f:
        for symbol in filtered_symbols:
            f.write(f'{symbol}\n')
    
    # 保存预测结果
    predictions_df = pd.DataFrame(predictions)
    predictions_df.to_csv(
        os.path.join(PATHS['results'], f'predictions_{timestamp}.csv')
    )
    
    logger.info(f'结果已保存到 {PATHS["results"]} 目录')

def run_analysis():
    """运行选股和预测分析"""
    logger.info('开始运行分析...')
    
    try:
        # 初始化
        data_fetcher = StockDataFetcher()
        predictor = StockPredictor()
        
        # 获取所有股票代码（示例）
        all_symbols = ['AAPL', 'MSFT', 'GOOGL']  # 这里应该从某个源获取
        
        # 筛选股票
        filtered_symbols = data_fetcher.filter_stocks(all_symbols)
        logger.info(f'筛选出 {len(filtered_symbols)} 支股票')
        
        # 对筛选出的股票进行预测
        predictions = {}
        for symbol in filtered_symbols:
            try:
                # 获取数据
                historical_data = data_fetcher.get_stock_price_history(symbol)
                technical_data = data_fetcher.get_technical_indicators(symbol)
                
                if not historical_data.empty:
                    # 预测
                    lstm_pred, xgb_pred = predictor.predict_next_month(
                        historical_data,
                        pd.DataFrame(technical_data)
                    )
                    
                    predictions[symbol] = {
                        'lstm_prediction': lstm_pred[-1],
                        'xgb_prediction': xgb_pred[-1],
                        'current_price': historical_data['Close'].iloc[-1],
                        'predicted_change_lstm': (lstm_pred[-1] / historical_data['Close'].iloc[-1] - 1) * 100,
                        'predicted_change_xgb': (xgb_pred[-1] / historical_data['Close'].iloc[-1] - 1) * 100
                    }
                    
                    logger.info(f'完成 {symbol} 的预测')
                    
            except Exception as e:
                logger.error(f'预测 {symbol} 时出错: {str(e)}')
                continue
        
        # 保存结果
        save_results(filtered_symbols, predictions)
        logger.info('分析完成')
        
    except Exception as e:
        logger.error(f'运行分析时出错: {str(e)}')

def schedule_jobs():
    """设置定时任务"""
    # 每月第一个交易日运行
    schedule.every().month.at("10:00").do(run_analysis)
    
    logger.info('定时任务已设置')
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    setup_directories()
    schedule_jobs() 