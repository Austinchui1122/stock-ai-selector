"""
配置文件
"""

# 数据获取配置
STOCK_DATA = {
    'market_cap_min': 5_000_000_000,  # 最小市值（50亿美元）
    'lookback_period': 60,  # 历史数据回溯天数
    'prediction_days': 30,  # 预测天数
}

# 选股条件
STOCK_FILTERS = {
    'roe_min': 0.15,  # 最小ROE（15%）
    'pe_max': 25,  # 最大PE
    'debt_equity_max': 0.5,  # 最大负债权益比
}

# 技术指标参数
TECHNICAL_INDICATORS = {
    'ma_short': 50,   # 短期均线
    'ma_long': 200,   # 长期均线
    'rsi_period': 14, # RSI周期
    'rsi_min': 50,    # RSI最小值
    'rsi_max': 70,    # RSI最大值
    'macd': {
        'fast': 12,
        'slow': 26,
        'signal': 9
    }
}

# AI模型参数
MODEL_PARAMS = {
    'lstm': {
        'units': [64, 32],
        'dropout': 0.2,
        'epochs': 100,
        'batch_size': 32
    },
    'xgboost': {
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100
    }
}

# Web应用配置
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 8501,
    'debug': True
}

# 数据存储路径
PATHS = {
    'data': 'data/',
    'models': 'models/',
    'results': 'results/'
}

# API配置
API_CONFIG = {
    'alpha_vantage': {
        'api_key': '',  # 从环境变量获取
        'output_size': 'full',
        'output_format': 'pandas'
    }
} 