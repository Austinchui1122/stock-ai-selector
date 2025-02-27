"""
Web應用界面模块
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

try:
    from config import STOCK_DATA, STOCK_FILTERS, WEB_CONFIG
    print("成功導入配置")
except Exception as e:
    print(f"導入配置時出錯: {str(e)}")
    st.error("配置導入失敗，請檢查配置文件")
    raise

from src.data.stock_data import StockDataFetcher
from src.models.stock_predictor import StockPredictor

def create_stock_chart(historical_data: pd.DataFrame, predictions: list, symbol: str) -> go.Figure:
    """创建股票图表
    
    Args:
        historical_data: 历史数据
        predictions: 预测数据
        symbol: 股票代码
        
    Returns:
        Plotly图表对象
    """
    fig = go.Figure()
    
    # 添加历史数据
    fig.add_trace(go.Candlestick(
        x=historical_data.index,
        open=historical_data['Open'],
        high=historical_data['High'],
        low=historical_data['Low'],
        close=historical_data['Close'],
        name='历史数据'
    ))
    
    # 添加预测数据
    future_dates = pd.date_range(
        start=historical_data.index[-1] + timedelta(days=1),
        periods=len(predictions),
        freq='D'
    )
    
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        mode='lines',
        name='预测数据',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title=f'{symbol} 股价预测',
        yaxis_title='价格',
        xaxis_title='日期',
        template='plotly_dark'
    )
    
    return fig

def main():
    st.set_page_config(page_title='AI股票选择器', layout='wide')
    st.title('AI股票自动选择系统')
    
    # 初始化数据获取器和预测器
    try:
        data_fetcher = StockDataFetcher()
        predictor = StockPredictor()
    except ValueError as e:
        st.error(str(e))
        return
    
    # 侧边栏
    st.sidebar.title('选股条件')
    market_cap = st.sidebar.number_input(
        '最小市值（十亿美元）',
        min_value=1.0,
        value=5.0
    )
    
    roe = st.sidebar.number_input(
        '最小ROE（%）',
        min_value=0.0,
        value=15.0
    )
    
    pe = st.sidebar.number_input(
        '最大PE',
        min_value=0.0,
        value=25.0
    )
    
    # 更新筛选条件
    STOCK_DATA['market_cap_min'] = market_cap * 1_000_000_000  # 转换为美元
    STOCK_FILTERS['roe_min'] = roe / 100  # 转换为小数
    STOCK_FILTERS['pe_max'] = pe
    
    # 主界面
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('股票筛选结果')
        if st.button('开始筛选'):
            with st.spinner('正在筛选股票...'):
                try:
                    # 这里应该从某个源获取所有股票代码
                    all_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  # 示例
                    filtered_symbols = data_fetcher.filter_stocks(all_symbols)
                    
                    if filtered_symbols:
                        st.write('符合条件的股票：')
                        for symbol in filtered_symbols:
                            st.write(f'- {symbol}')
                    else:
                        st.write('没有找到符合条件的股票')
                except Exception as e:
                    st.error(f'筛选过程中出错: {str(e)}')
    
    with col2:
        st.subheader('股价预测')
        symbol = st.text_input('输入股票代码')
        
        if symbol and st.button('预测'):
            with st.spinner('正在获取数据并预测...'):
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
                        
                        # 显示图表
                        fig = create_stock_chart(historical_data, lstm_pred, symbol)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 显示预测结果
                        st.write('### 预测结果')
                        st.write(f'LSTM模型预测30天后价格: ${lstm_pred[-1]:.2f}')
                        st.write(f'XGBoost模型预测30天后价格: ${xgb_pred[-1]:.2f}')
                    else:
                        st.error('获取数据失败，请检查股票代码是否正确')
                except Exception as e:
                    st.error(f'预测过程中出错: {str(e)}')

if __name__ == '__main__':
    main() 