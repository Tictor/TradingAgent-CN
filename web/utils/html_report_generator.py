#!/usr/bin/env python3
"""
HTML报告生成器
基于Web展示格式生成独立的HTML报告文件
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')


class HTMLReportGenerator:
    """HTML报告生成器"""

    def __init__(self):
        """初始化HTML报告生成器"""
        logger.info("📄 初始化HTML报告生成器")

    def generate_html_report(self, results: Dict[str, Any]) -> str:
        """生成HTML格式的分析报告"""
        
        stock_symbol = results.get('stock_symbol', 'N/A')
        decision = results.get('decision', {})
        state = results.get('state', {})
        success = results.get('success', False)
        error = results.get('error')
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建HTML内容
        html_content = self._generate_html_structure(
            stock_symbol=stock_symbol,
            decision=decision,
            state=state,
            results=results,
            timestamp=timestamp,
            success=success,
            error=error
        )
        
        return html_content

    def _generate_html_structure(self, stock_symbol: str, decision: Dict, state: Dict, 
                                results: Dict, timestamp: str, success: bool, error: str) -> str:
        """生成完整的HTML结构"""
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_symbol} 股票分析报告 - TradingAgents-CN</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="main-header">
            <h1>🤖 TradingAgents-CN</h1>
            <h2>{stock_symbol} 股票分析报告</h2>
            <p class="timestamp">生成时间: {timestamp}</p>
        </header>

        {self._generate_error_section(success, error) if not success and error else ""}
        
        <main>
            {self._generate_decision_summary_html(decision, stock_symbol)}
            
            {self._generate_analysis_info_html(results)}
            
            {self._generate_detailed_analysis_html(state)}
        </main>

        <footer class="risk-warning">
            <h3>⚠️ 重要风险提示</h3>
            <div class="warning-content">
                <p><strong>投资风险提示</strong>:</p>
                <ul>
                    <li><strong>仅供参考</strong>: 本分析结果仅供参考，不构成投资建议</li>
                    <li><strong>投资风险</strong>: 股票投资有风险，可能导致本金损失</li>
                    <li><strong>理性决策</strong>: 请结合多方信息进行理性投资决策</li>
                    <li><strong>专业咨询</strong>: 重大投资决策建议咨询专业财务顾问</li>
                    <li><strong>自担风险</strong>: 投资决策及其后果由投资者自行承担</li>
                </ul>
            </div>
            <p class="report-footer">报告生成时间: {timestamp}</p>
        </footer>
    </div>

    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""

    def _get_css_styles(self) -> str:
        """获取CSS样式，基于Streamlit web界面的样式"""
        
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 18px;  /* 增加基础字体大小 */
            line-height: 1.7;  /* 增加行高提升可读性 */
            color: #262730;
            background-color: #fafafa;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* 主标题样式 */
        .main-header {
            background: linear-gradient(90deg, #1f77b4, #ff7f0e);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }

        .main-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .main-header h2 {
            font-size: 1.8rem;
            font-weight: 300;
            margin-bottom: 1rem;
        }

        .timestamp {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        /* 错误信息样式 */
        .error-section {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 2rem 0;
        }

        .error-section h3 {
            color: #721c24;
            margin-bottom: 1rem;
        }

        .error-section p {
            color: #721c24;
        }

        /* 决策摘要样式 */
        .decision-summary {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }

        .decision-summary h3 {
            color: #1f77b4;
            margin-bottom: 2rem;
            font-size: 1.8rem;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 0.5rem;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
            text-align: center;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #262730;
        }

        .metric-value.buy {
            color: #28a745;
        }

        .metric-value.sell {
            color: #dc3545;
        }

        .metric-value.hold {
            color: #ffc107;
        }

        /* 推理内容样式 */
        .reasoning-section {
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
        }

        .reasoning-section h4 {
            color: #1976d2;
            margin-bottom: 1rem;
        }

        /* 分析配置信息样式 */
        .analysis-info {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 2rem 0;
        }

        .analysis-info h3 {
            color: #1f77b4;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }

        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }

        .config-item {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .config-item .label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
        }

        .config-item .value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #262730;
        }

        .analysts-list {
            margin-top: 1rem;
            padding: 1rem;
            background: #e8f5e8;
            border-radius: 8px;
        }

        .analysts-list strong {
            color: #2e7d32;
        }

        /* 详细分析报告样式 */
        .detailed-analysis {
            margin: 3rem 0;
        }

        .detailed-analysis h3 {
            color: #1f77b4;
            margin-bottom: 2rem;
            font-size: 1.8rem;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 0.5rem;
        }

        /* Tab样式 */
        .tabs-container {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }

        .tabs-nav {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }

        .tab-button {
            background: white;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 0.8rem 1.2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            color: #495057;
        }

        .tab-button:hover {
            background: #e3f2fd;
            border-color: #2196f3;
            transform: translateY(-1px);
        }

        .tab-button.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102,126,234,0.3);
        }

        .tab-content {
            display: none;
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .tab-content.active {
            display: block;
        }

        .tab-content h4 {
            color: #1f77b4;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }

        .tab-content p {
            margin-bottom: 1.2rem;
            text-align: justify;
            font-size: 16px;
            line-height: 1.8;
        }

        /* 改进的Markdown样式 */
        .analysis-main-title {
            color: #1f77b4;
            font-size: 1.6rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e3f2fd;
        }

        .analysis-section-title {
            color: #1565c0;
            font-size: 1.4rem;
            font-weight: 600;
            margin: 1.8rem 0 1rem 0;
            padding-left: 1rem;
            border-left: 4px solid #2196f3;
            background-color: #f8fffe;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }

        .analysis-subtitle {
            color: #1976d2;
            font-size: 1.2rem;
            font-weight: 500;
            margin: 1.5rem 0 0.8rem 0;
            padding-left: 0.5rem;
            border-left: 3px solid #64b5f6;
        }

        /* 内容段落样式 */
        .tab-content p {
            font-size: 17px;
            line-height: 1.8;
            margin-bottom: 1.2rem;
            text-align: justify;
            color: #333;
        }

        /* 强调文本样式 */
        .tab-content strong {
            color: #1565c0;
            font-weight: 600;
        }

        .tab-content em {
            color: #666;
            font-style: italic;
        }

        .tab-content code {
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #d84315;
        }

        /* 链接样式 */
        .tab-content a {
            color: #1976d2;
            text-decoration: none;
            border-bottom: 1px solid #bbdefb;
        }

        .tab-content a:hover {
            color: #0d47a1;
            border-bottom: 1px solid #1976d2;
        }

        /* 占位符样式 */
        .analysis-placeholder {
            text-align: center;
            padding: 3rem;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 15px;
            margin: 2rem 0;
        }

        .analysis-placeholder h4 {
            color: #6c757d;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }

        .analysis-placeholder p {
            color: #6c757d;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }

        .placeholder-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .placeholder-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .placeholder-card .icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .placeholder-card .title {
            font-weight: bold;
            color: #495057;
            margin-bottom: 0.3rem;
        }

        .placeholder-card .desc {
            font-size: 0.8rem;
            color: #6c757d;
        }

        .placeholder-tip {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 2rem;
        }

        .placeholder-tip p {
            color: #1976d2;
            margin: 0;
            font-size: 0.95rem;
        }

        /* 风险提示样式 */
        .risk-warning {
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            border: 2px solid #f44336;
            border-radius: 15px;
            padding: 2rem;
            margin-top: 3rem;
        }

        .risk-warning h3 {
            color: #c62828;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }

        .warning-content {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }

        .warning-content ul {
            list-style: none;
            padding: 0;
        }

        .warning-content li {
            margin-bottom: 0.8rem;
            padding-left: 1.5rem;
            position: relative;
        }

        .warning-content li:before {
            content: "⚠️";
            position: absolute;
            left: 0;
        }

        .report-footer {
            text-align: center;
            font-size: 0.9rem;
            color: #666;
            margin-top: 1rem;
            font-style: italic;
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .main-header {
                padding: 1.5rem;
            }
            
            .main-header h1 {
                font-size: 2rem;
            }
            
            .main-header h2 {
                font-size: 1.5rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }
            
            .tabs-nav {
                flex-direction: column;
            }
            
            .tab-button {
                text-align: center;
            }
        }

        /* 团队决策特殊样式 */
        .team-decision {
            margin: 2.5rem 0;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 3px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .team-decision h5 {
            color: white;
            margin: 0;
            font-size: 1.3rem;
            font-weight: 600;
            padding: 1rem 1.5rem;
            background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
            border-bottom: none;
        }

        .team-decision .content {
            background: #ffffff;
            padding: 2rem 1.5rem;
            margin: 0;
            border: none;
            font-size: 17px;
            line-height: 1.8;
        }

        .team-decision .content p {
            color: #333;
            margin-bottom: 1.2rem;
        }

        .team-decision .content h3,
        .team-decision .content h4,
        .team-decision .content h5 {
            color: #1565c0;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }

        .team-decision .content strong {
            color: #1565c0;
            font-weight: 600;
        }

        /* 滚动优化 */
        html {
            scroll-behavior: smooth;
        }

        /* 打印样式 */
        @media print {
            .container {
                max-width: none;
                margin: 0;
                padding: 0;
            }
            
            .main-header {
                background: #1f77b4 !important;
                color: white !important;
                -webkit-print-color-adjust: exact;
            }
            
            .tab-content {
                display: block !important;
            }
            
            .tabs-nav {
                display: none;
            }
        }
        """

    def _generate_error_section(self, success: bool, error: str) -> str:
        """生成错误信息部分"""
        if success or not error:
            return ""
            
        return f"""
        <div class="error-section">
            <h3>❌ 分析失败</h3>
            <p><strong>错误信息</strong>: {error}</p>
            <p><strong>解决方案</strong>: 请检查API密钥配置，确保网络连接正常，然后重新运行分析。</p>
        </div>
        """

    def _generate_decision_summary_html(self, decision: Dict, stock_symbol: str) -> str:
        """生成投资决策摘要HTML"""
        
        if not decision:
            return """
            <div class="analysis-placeholder">
                <h4>📊 等待投资决策</h4>
                <p>分析完成后，投资决策将在此处显示</p>
                <div class="placeholder-cards">
                    <div class="placeholder-card">
                        <div class="icon">📊</div>
                        <div class="title">投资建议</div>
                        <div class="desc">买入/卖出/持有</div>
                    </div>
                    <div class="placeholder-card">
                        <div class="icon">💰</div>
                        <div class="title">目标价位</div>
                        <div class="desc">预期价格区间</div>
                    </div>
                    <div class="placeholder-card">
                        <div class="icon">⚖️</div>
                        <div class="title">风险评级</div>
                        <div class="desc">风险程度评估</div>
                    </div>
                    <div class="placeholder-card">
                        <div class="icon">🎯</div>
                        <div class="title">置信度</div>
                        <div class="desc">分析可信程度</div>
                    </div>
                </div>
            </div>
            """

        # 处理投资建议
        action = decision.get('action', 'N/A')
        action_translation = {
            'BUY': '买入', 'SELL': '卖出', 'HOLD': '持有',
            '买入': '买入', '卖出': '卖出', '持有': '持有'
        }
        chinese_action = action_translation.get(action.upper(), action)
        action_class = {
            'BUY': 'buy', 'SELL': 'sell', 'HOLD': 'hold',
            '买入': 'buy', '卖出': 'sell', '持有': 'hold'
        }.get(action.upper(), '')

        # 处理置信度
        confidence = decision.get('confidence', 0)
        confidence_str = f"{confidence:.1%}" if isinstance(confidence, (int, float)) else str(confidence)

        # 处理风险评分
        risk_score = decision.get('risk_score', 0)
        risk_str = f"{risk_score:.1%}" if isinstance(risk_score, (int, float)) else str(risk_score)

        # 处理目标价格
        target_price = decision.get('target_price')
        
        # 根据股票代码确定货币符号
        import re
        is_china = re.match(r'^\d{6}$', str(stock_symbol)) if stock_symbol else False
        currency_symbol = "¥" if is_china else "$"
        
        if target_price is not None and isinstance(target_price, (int, float)) and target_price > 0:
            price_display = f"{currency_symbol}{target_price:.2f}"
        else:
            price_display = "待分析"

        # 生成推理部分
        reasoning_section = ""
        if 'reasoning' in decision and decision['reasoning']:
            reasoning_section = f"""
            <div class="reasoning-section">
                <h4>🧠 AI分析推理</h4>
                <div class="reasoning-content">{decision['reasoning']}</div>
            </div>
            """

        return f"""
        <section class="decision-summary">
            <h3>🎯 投资决策摘要</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">投资建议</div>
                    <div class="metric-value {action_class}">{chinese_action}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">置信度</div>
                    <div class="metric-value">{confidence_str}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">风险评分</div>
                    <div class="metric-value">{risk_str}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">目标价位</div>
                    <div class="metric-value">{price_display}</div>
                </div>
            </div>
            {reasoning_section}
        </section>
        """

    def _generate_analysis_info_html(self, results: Dict) -> str:
        """生成分析配置信息HTML"""
        
        llm_provider = results.get('llm_provider', 'dashscope')
        provider_name = {
            'dashscope': '阿里百炼',
            'google': 'Google AI',
            'deepseek': 'DeepSeek',
            'openai': 'OpenAI',
            'volcengine': '火山引擎',
            'openrouter': 'OpenRouter'
        }.get(llm_provider, llm_provider)

        llm_model = results.get('llm_model', 'N/A')
        model_display = {
            'qwen-turbo': 'Qwen Turbo',
            'qwen-plus': 'Qwen Plus',
            'qwen-max': 'Qwen Max',
            'gemini-2.0-flash': 'Gemini 2.0 Flash',
            'gemini-1.5-pro': 'Gemini 1.5 Pro',
            'gemini-1.5-flash': 'Gemini 1.5 Flash'
        }.get(llm_model, llm_model)

        analysts = results.get('analysts', [])
        analysts_count = len(analysts) if analysts else 0

        # 分析师列表
        analyst_names = {
            'market': '📈 市场技术分析师',
            'fundamentals': '💰 基本面分析师',
            'news': '📰 新闻分析师',
            'social_media': '💭 社交媒体分析师',
            'risk': '⚠️ 风险评估师'
        }
        
        analysts_display = ""
        if analysts:
            analyst_list = [analyst_names.get(analyst, analyst) for analyst in analysts]
            analysts_display = f"""
            <div class="analysts-list">
                <strong>参与的分析师:</strong><br>
                {' • '.join(analyst_list)}
            </div>
            """

        return f"""
        <section class="analysis-info">
            <h3>📋 分析配置信息</h3>
            <div class="config-grid">
                <div class="config-item">
                    <div class="label">LLM提供商</div>
                    <div class="value">{provider_name}</div>
                </div>
                <div class="config-item">
                    <div class="label">AI模型</div>
                    <div class="value">{model_display}</div>
                </div>
                <div class="config-item">
                    <div class="label">分析师数量</div>
                    <div class="value">{analysts_count}个</div>
                </div>
            </div>
            {analysts_display}
        </section>
        """

    def _generate_detailed_analysis_html(self, state: Dict) -> str:
        """生成详细分析报告HTML"""
        
        # 定义分析模块
        analysis_modules = [
            {
                'key': 'market_report',
                'title': '📈 市场技术分析',
                'description': '技术指标、价格趋势、支撑阻力位分析'
            },
            {
                'key': 'fundamentals_report',
                'title': '💰 基本面分析',
                'description': '财务数据、估值水平、盈利能力分析'
            },
            {
                'key': 'sentiment_report',
                'title': '💭 市场情绪分析',
                'description': '投资者情绪、社交媒体情绪指标'
            },
            {
                'key': 'news_report',
                'title': '📰 新闻事件分析',
                'description': '相关新闻事件、市场动态影响分析'
            },
            {
                'key': 'risk_assessment',
                'title': '⚠️ 风险评估',
                'description': '风险因素识别、风险等级评估'
            },
            {
                'key': 'investment_plan',
                'title': '📋 投资建议',
                'description': '具体投资策略、仓位管理建议'
            },
            {
                'key': 'investment_debate_state',
                'title': '🔬 研究团队决策',
                'description': '多头/空头研究员辩论分析，研究经理综合决策'
            },
            {
                'key': 'trader_investment_plan',
                'title': '💼 交易团队计划',
                'description': '专业交易员制定的具体交易执行计划'
            },
            {
                'key': 'risk_debate_state',
                'title': '⚖️ 风险管理团队',
                'description': '激进/保守/中性分析师风险评估，投资组合经理最终决策'
            },
            {
                'key': 'final_trade_decision',
                'title': '🎯 最终交易决策',
                'description': '综合所有团队分析后的最终投资决策'
            }
        ]

        # 过滤出有数据的模块
        available_modules = []
        for module in analysis_modules:
            if module['key'] in state and state[module['key']]:
                if isinstance(state[module['key']], dict):
                    has_content = any(v for v in state[module['key']].values() if v)
                    if has_content:
                        available_modules.append(module)
                else:
                    available_modules.append(module)

        if not available_modules:
            return self._generate_analysis_placeholder_html()

        # 生成标签页导航
        tabs_nav = []
        tab_contents = []
        
        for i, module in enumerate(available_modules):
            tab_id = f"tab_{module['key']}"
            active_class = "active" if i == 0 else ""
            
            tabs_nav.append(f'<button class="tab-button {active_class}" onclick="showTab(\'{tab_id}\')">{module["title"]}</button>')
            
            content = state[module['key']]
            content_html = self._format_module_content_html(content, module['key'])
            
            tab_contents.append(f'''
            <div id="{tab_id}" class="tab-content {active_class}">
                <h4>{module["title"]}</h4>
                <p><em>{module["description"]}</em></p>
                <hr style="margin: 1rem 0; border: none; border-top: 1px solid #dee2e6;">
                {content_html}
            </div>
            ''')

        return f"""
        <section class="detailed-analysis">
            <h3>📋 详细分析报告</h3>
            <div class="tabs-container">
                <div class="tabs-nav">
                    {''.join(tabs_nav)}
                </div>
                {''.join(tab_contents)}
            </div>
        </section>
        """

    def _format_module_content_html(self, content: Any, module_key: str) -> str:
        """格式化模块内容为HTML"""
        
        if isinstance(content, str):
            # 改进的Markdown到HTML转换
            html_content = self._convert_markdown_to_html(content)
            return html_content
            
        elif isinstance(content, dict):
            # 特殊处理团队决策报告
            if module_key == 'investment_debate_state':
                return self._format_investment_debate_html(content)
            elif module_key == 'risk_debate_state':
                return self._format_risk_debate_html(content)
            else:
                # 普通字典格式化
                sections = []
                for key, value in content.items():
                    section_title = key.replace('_', ' ').title()
                    formatted_value = str(value).replace('\n\n', '</p><p>').replace('\n', '<br>')
                    sections.append(f'<h5>{section_title}</h5><p>{formatted_value}</p>')
                return ''.join(sections)
        else:
            return f'<p>{str(content)}</p>'

    def _convert_markdown_to_html(self, text: str) -> str:
        """将Markdown文本转换为格式化的HTML"""
        if not text:
            return '<p>暂无内容</p>'
            
        # 按行处理
        lines = text.split('\n')
        html_lines = []
        in_paragraph = False
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            # 空行处理
            if not line:
                if current_paragraph:
                    html_lines.append(f'<p>{"<br>".join(current_paragraph)}</p>')
                    current_paragraph = []
                    in_paragraph = False
                continue
            
            # 标题处理
            if line.startswith('###'):
                if current_paragraph:
                    html_lines.append(f'<p>{"<br>".join(current_paragraph)}</p>')
                    current_paragraph = []
                title = line[3:].strip()
                html_lines.append(f'<h5 class="analysis-subtitle">{title}</h5>')
                in_paragraph = False
                continue
            elif line.startswith('##'):
                if current_paragraph:
                    html_lines.append(f'<p>{"<br>".join(current_paragraph)}</p>')
                    current_paragraph = []
                title = line[2:].strip()
                html_lines.append(f'<h4 class="analysis-section-title">{title}</h4>')
                in_paragraph = False
                continue
            elif line.startswith('#'):
                if current_paragraph:
                    html_lines.append(f'<p>{"<br>".join(current_paragraph)}</p>')
                    current_paragraph = []
                title = line[1:].strip()
                html_lines.append(f'<h3 class="analysis-main-title">{title}</h3>')
                in_paragraph = False
                continue
                
            # 列表处理
            if line.startswith('- '):
                if current_paragraph:
                    html_lines.append(f'<p>{"<br>".join(current_paragraph)}</p>')
                    current_paragraph = []
                    in_paragraph = False
                
                # 收集连续的列表项
                list_items = [line[2:].strip()]
                continue
            
            # 处理强调文本和其他格式
            formatted_line = self._format_text_styles(line)
            current_paragraph.append(formatted_line)
            in_paragraph = True
        
        # 处理最后的段落
        if current_paragraph:
            html_lines.append(f'<p>{"<br>".join(current_paragraph)}</p>')
        
        return '\n'.join(html_lines)

    def _format_text_styles(self, text: str) -> str:
        """格式化文本样式（粗体、斜体等）"""
        import re
        
        # 处理粗体 **text** 
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # 处理斜体 *text*
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)', r'<em>\1</em>', text)
        
        # 处理代码 `code`
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # 处理链接 [text](url) - 简单版本
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
        
        return text

    def _format_investment_debate_html(self, content: Dict) -> str:
        """格式化研究团队决策HTML"""
        sections = []
        
        if content.get('bull_history'):
            formatted_content = self._convert_markdown_to_html(content['bull_history'])
            sections.append(f'''
            <div class="team-decision">
                <h5>📈 多头研究员分析</h5>
                <div class="content">{formatted_content}</div>
            </div>
            ''')
            
        if content.get('bear_history'):
            formatted_content = self._convert_markdown_to_html(content['bear_history'])
            sections.append(f'''
            <div class="team-decision">
                <h5>📉 空头研究员分析</h5>
                <div class="content">{formatted_content}</div>
            </div>
            ''')
            
        if content.get('judge_decision'):
            formatted_content = self._convert_markdown_to_html(content['judge_decision'])
            sections.append(f'''
            <div class="team-decision">
                <h5>🎯 研究经理综合决策</h5>
                <div class="content">{formatted_content}</div>
            </div>
            ''')
            
        return ''.join(sections)

    def _format_risk_debate_html(self, content: Dict) -> str:
        """格式化风险管理团队决策HTML"""
        sections = []
        
        if content.get('risky_history'):
            formatted_content = self._convert_markdown_to_html(content['risky_history'])
            sections.append(f'''
            <div class="team-decision">
                <h5>🚀 激进分析师评估</h5>
                <div class="content">{formatted_content}</div>
            </div>
            ''')
            
        if content.get('safe_history'):
            formatted_content = self._convert_markdown_to_html(content['safe_history'])
            sections.append(f'''
            <div class="team-decision">
                <h5>🛡️ 保守分析师评估</h5>
                <div class="content">{formatted_content}</div>
            </div>
            ''')
            
        if content.get('neutral_history'):
            formatted_content = self._convert_markdown_to_html(content['neutral_history'])
            sections.append(f'''
            <div class="team-decision">
                <h5>⚖️ 中性分析师评估</h5>
                <div class="content">{formatted_content}</div>
            </div>
            ''')
            
        if content.get('judge_decision'):
            formatted_content = self._convert_markdown_to_html(content['judge_decision'])
            sections.append(f'''
            <div class="team-decision">
                <h5>🎯 投资组合经理最终决策</h5>
                <div class="content">{formatted_content}</div>
            </div>
            ''')
            
        return ''.join(sections)

    def _generate_analysis_placeholder_html(self) -> str:
        """生成分析占位符HTML"""
        
        return """
        <section class="detailed-analysis">
            <h3>📋 详细分析报告</h3>
            <div class="analysis-placeholder">
                <h4>📊 等待分析数据</h4>
                <p>请先配置API密钥并运行股票分析，分析完成后详细报告将在此处显示</p>
                <div class="placeholder-cards">
                    <div class="placeholder-card">
                        <div class="icon">📈</div>
                        <div class="title">技术分析</div>
                        <div class="desc">价格趋势、支撑阻力</div>
                    </div>
                    <div class="placeholder-card">
                        <div class="icon">💰</div>
                        <div class="title">基本面分析</div>
                        <div class="desc">财务数据、估值分析</div>
                    </div>
                    <div class="placeholder-card">
                        <div class="icon">📰</div>
                        <div class="title">新闻分析</div>
                        <div class="desc">市场情绪、事件影响</div>
                    </div>
                    <div class="placeholder-card">
                        <div class="icon">⚖️</div>
                        <div class="title">风险评估</div>
                        <div class="desc">风险控制、投资建议</div>
                    </div>
                </div>
                <div class="placeholder-tip">
                    <p>💡 <strong>提示</strong>: 配置API密钥后，系统将生成包含多个智能体团队分析的详细投资报告</p>
                </div>
            </div>
        </section>
        """

    def _get_javascript(self) -> str:
        """获取JavaScript代码，用于标签页切换功能"""
        
        return """
        function showTab(tabId) {
            // 隐藏所有标签内容
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            
            // 移除所有标签按钮的active类
            const tabButtons = document.querySelectorAll('.tab-button');
            tabButtons.forEach(button => {
                button.classList.remove('active');
            });
            
            // 显示选中的标签内容
            const selectedTab = document.getElementById(tabId);
            if (selectedTab) {
                selectedTab.classList.add('active');
            }
            
            // 激活对应的标签按钮
            const clickedButton = event.target;
            clickedButton.classList.add('active');
        }

        // 页面加载完成后的初始化
        document.addEventListener('DOMContentLoaded', function() {
            console.log('TradingAgents-CN HTML Report Loaded');
            
            // 确保第一个标签是激活状态
            const firstTab = document.querySelector('.tab-content');
            const firstButton = document.querySelector('.tab-button');
            if (firstTab) firstTab.classList.add('active');
            if (firstButton) firstButton.classList.add('active');
        });
        """


# 创建全局HTML报告生成器实例
html_report_generator = HTMLReportGenerator()