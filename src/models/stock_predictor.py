"""
股票预测模型模块
"""
import numpy as np
import pandas as pd
from typing import Tuple, List
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import xgboost as xgb
from config.config import MODEL_PARAMS

class StockPredictor:
    def __init__(self):
        """初始化预测模型"""
        self.scaler = MinMaxScaler()
        self.lstm_model = None
        self.xgb_model = None
        
    def prepare_data(self, data: pd.DataFrame, lookback: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """准备LSTM模型训练数据
        
        Args:
            data: 股票历史数据
            lookback: 回看天数
            
        Returns:
            (X, y) 训练数据对
        """
        scaled_data = self.scaler.fit_transform(data[['Close']].values)
        X, y = [], []
        
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i])
            y.append(scaled_data[i])
            
        return np.array(X), np.array(y)
        
    def build_lstm_model(self, input_shape: Tuple[int, int]) -> None:
        """构建LSTM模型
        
        Args:
            input_shape: 输入数据形状
        """
        model = Sequential()
        
        # 第一个LSTM层
        model.add(LSTM(
            units=MODEL_PARAMS['lstm']['units'][0],
            return_sequences=True,
            input_shape=input_shape
        ))
        model.add(Dropout(MODEL_PARAMS['lstm']['dropout']))
        
        # 第二个LSTM层
        model.add(LSTM(
            units=MODEL_PARAMS['lstm']['units'][1],
            return_sequences=False
        ))
        model.add(Dropout(MODEL_PARAMS['lstm']['dropout']))
        
        # 输出层
        model.add(Dense(units=1))
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.lstm_model = model
        
    def train_lstm(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练LSTM模型
        
        Args:
            X: 训练数据
            y: 目标数据
        """
        if self.lstm_model is None:
            self.build_lstm_model((X.shape[1], X.shape[2]))
            
        self.lstm_model.fit(
            X, y,
            epochs=MODEL_PARAMS['lstm']['epochs'],
            batch_size=MODEL_PARAMS['lstm']['batch_size'],
            verbose=0
        )
        
    def train_xgboost(self, X: pd.DataFrame, y: pd.Series) -> None:
        """训练XGBoost模型
        
        Args:
            X: 特征数据
            y: 目标数据
        """
        self.xgb_model = xgb.XGBRegressor(
            max_depth=MODEL_PARAMS['xgboost']['max_depth'],
            learning_rate=MODEL_PARAMS['xgboost']['learning_rate'],
            n_estimators=MODEL_PARAMS['xgboost']['n_estimators']
        )
        self.xgb_model.fit(X, y)
        
    def predict_lstm(self, data: np.ndarray) -> List[float]:
        """使用LSTM模型预测
        
        Args:
            data: 输入数据
            
        Returns:
            预测结果列表
        """
        predictions = self.lstm_model.predict(data)
        return self.scaler.inverse_transform(predictions).flatten().tolist()
        
    def predict_xgboost(self, data: pd.DataFrame) -> List[float]:
        """使用XGBoost模型预测
        
        Args:
            data: 输入数据
            
        Returns:
            预测结果列表
        """
        return self.xgb_model.predict(data).tolist()
        
    def predict_next_month(self, historical_data: pd.DataFrame, 
                         technical_indicators: pd.DataFrame) -> Tuple[List[float], List[float]]:
        """预测下个月的股价
        
        Args:
            historical_data: 历史价格数据
            technical_indicators: 技术指标数据
            
        Returns:
            (lstm_predictions, xgb_predictions) 两个模型的预测结果
        """
        # 准备LSTM数据
        X_lstm, y_lstm = self.prepare_data(historical_data)
        self.train_lstm(X_lstm, y_lstm)
        
        # 准备XGBoost数据
        X_xgb = pd.concat([historical_data, technical_indicators], axis=1)
        y_xgb = historical_data['Close'].shift(-1).dropna()
        self.train_xgboost(X_xgb[:-1], y_xgb)
        
        # 预测
        lstm_pred = self.predict_lstm(X_lstm[-30:])  # 预测未来30天
        xgb_pred = self.predict_xgboost(X_xgb[-30:])  # 预测未来30天
        
        return lstm_pred, xgb_pred 