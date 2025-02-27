# 美股 AI 自动选股工具

基于人工智能的美股自动选股系统，结合基本面分析、技术分析和市场情绪分析，自动筛选潜力股票并预测未来一个月的股价走势。

## 功能特点

- 🔍 自动筛选符合条件的美股（市值、ROE、EPS等指标）
- 📊 技术分析（MA、RSI、MACD等指标）
- 🤖 AI模型预测（LSTM + XGBoost）
- 📱 Web界面展示
- ⏰ 自动执行和更新

## 项目结构

```
.
├── src/
│   ├── data/          # 数据获取和处理
│   ├── models/        # AI 模型
│   ├── web/          # Web 界面
│   └── utils/        # 工具函数
├── tests/            # 测试文件
├── data/             # 数据存储
├── config/           # 配置文件
└── requirements.txt  # 项目依赖
```

## 安装说明

1. 克隆项目
```bash
git clone [项目地址]
cd stock-ai-selector
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
- 复制 `.env.example` 为 `.env`
- 填入必要的 API keys（Alpha Vantage 等）

## 使用方法

1. 启动 Web 界面
```bash
python src/web/app.py
```

2. 设置自动执行
- Linux/Mac: 使用 crontab
- Windows: 使用 Task Scheduler

## 技术栈

- 数据源：Yahoo Finance、Alpha Vantage
- AI 模型：LSTM、XGBoost
- Web 框架：Flask/Streamlit
- 数据处理：Pandas、NumPy
- 可视化：Plotly、Matplotlib

## 许可证

MIT License 