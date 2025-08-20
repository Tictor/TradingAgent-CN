#!/usr/bin/env python3
"""
分析结果自动保存功能
在分析完成后自动保存结果到本地目录
"""

import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

# 导入报告导出器
from .report_exporter import save_modular_reports_to_results_dir, save_report_to_results_dir, ReportExporter

def _format_team_decision_content(content: Dict[str, Any], module_key: str) -> str:
    """格式化团队决策内容"""
    formatted_content = ""

    if module_key == 'investment_debate_state':
        # 研究团队决策格式化
        if content.get('bull_history'):
            formatted_content += "## 📈 多头研究员分析\n\n"
            formatted_content += f"{content['bull_history']}\n\n"

        if content.get('bear_history'):
            formatted_content += "## 📉 空头研究员分析\n\n"
            formatted_content += f"{content['bear_history']}\n\n"

        if content.get('judge_decision'):
            formatted_content += "## 🎯 研究经理综合决策\n\n"
            formatted_content += f"{content['judge_decision']}\n\n"

    elif module_key == 'risk_debate_state':
        # 风险管理团队决策格式化
        if content.get('risky_history'):
            formatted_content += "## 🚀 激进分析师评估\n\n"
            formatted_content += f"{content['risky_history']}\n\n"

        if content.get('safe_history'):
            formatted_content += "## 🛡️ 保守分析师评估\n\n"
            formatted_content += f"{content['safe_history']}\n\n"

        if content.get('neutral_history'):
            formatted_content += "## ⚖️ 中性分析师评估\n\n"
            formatted_content += f"{content['neutral_history']}\n\n"

        if content.get('judge_decision'):
            formatted_content += "## 🎯 投资组合经理最终决策\n\n"
            formatted_content += f"{content['judge_decision']}\n\n"

    return formatted_content


class AutoSaver:
    """分析结果自动保存器"""

    def __init__(self):
        self.enabled = True  # 默认启用
        self.save_formats = ['markdown']  # 默认保存markdown格式
        self.report_exporter = ReportExporter()

    def is_enabled(self) -> bool:
        """检查自动保存是否启用"""
        # 从session state获取用户设置，默认启用
        return st.session_state.get('auto_save_enabled', True)
    
    def get_save_formats(self) -> list:
        """获取自动保存格式"""
        # 从session state获取用户设置，默认保存markdown
        return st.session_state.get('auto_save_formats', ['markdown'])

    def save_results_automatically(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """自动保存分析结果
        
        Args:
            results: 分析结果字典
            
        Returns:
            保存结果信息
        """
        if not self.is_enabled():
            logger.debug("🔇 自动保存已禁用，跳过保存")
            return {'enabled': False}

        if not results:
            logger.warning("⚠️ 分析结果为空，跳过自动保存")
            return {'enabled': True, 'success': False, 'reason': 'empty_results'}

        stock_symbol = results.get('stock_symbol', 'unknown')
        logger.info(f"💾 开始自动保存分析结果: {stock_symbol}")

        save_info = {
            'enabled': True,
            'success': False,
            'stock_symbol': stock_symbol,
            'saved_files': {},
            'formats': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            # 1. 总是保存分模块报告（CLI兼容格式）
            logger.info("📁 自动保存分模块报告...")
            modular_files = save_modular_reports_to_results_dir(results, stock_symbol)
            if modular_files:
                save_info['saved_files']['modular'] = modular_files
                save_info['formats'].append('modular_reports')
                logger.info(f"✅ 自动保存分模块报告成功，共 {len(modular_files)} 个文件")

            # 2. 保存配置的格式
            formats = self.get_save_formats()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            for format_type in formats:
                logger.info(f"📄 自动保存 {format_type} 格式...")
                try:
                    if format_type == 'markdown':
                        content = self.report_exporter.export_report(results, 'markdown')
                        if content:
                            filename = f"{stock_symbol}_analysis_{timestamp}.md"
                            saved_path = save_report_to_results_dir(content, filename, stock_symbol)
                            if saved_path:
                                save_info['saved_files']['markdown'] = saved_path
                                save_info['formats'].append('markdown')
                                logger.info(f"✅ Markdown格式自动保存成功: {saved_path}")

                    elif format_type == 'json':
                        # 保存原始JSON格式结果
                        json_content = json.dumps(results, ensure_ascii=False, indent=2).encode('utf-8')
                        filename = f"{stock_symbol}_analysis_{timestamp}.json"
                        saved_path = save_report_to_results_dir(json_content, filename, stock_symbol)
                        if saved_path:
                            save_info['saved_files']['json'] = saved_path
                            save_info['formats'].append('json')
                            logger.info(f"✅ JSON格式自动保存成功: {saved_path}")

                    elif format_type == 'docx' and self.report_exporter.pandoc_available:
                        content = self.report_exporter.export_report(results, 'docx')
                        if content:
                            filename = f"{stock_symbol}_analysis_{timestamp}.docx"
                            saved_path = save_report_to_results_dir(content, filename, stock_symbol)
                            if saved_path:
                                save_info['saved_files']['docx'] = saved_path
                                save_info['formats'].append('docx')
                                logger.info(f"✅ Word格式自动保存成功: {saved_path}")

                except Exception as e:
                    logger.error(f"❌ {format_type} 格式自动保存失败: {e}")

            # 3. 判断总体保存是否成功
            if save_info['saved_files']:
                save_info['success'] = True
                logger.info(f"✅ 自动保存完成: {save_info['formats']}")
            else:
                save_info['success'] = False
                save_info['reason'] = 'no_files_saved'
                logger.warning("⚠️ 自动保存失败：没有文件被保存")

        except Exception as e:
            save_info['success'] = False
            save_info['error'] = str(e)
            logger.error(f"❌ 自动保存异常: {e}")

        return save_info

    def show_auto_save_notification(self, save_info: Dict[str, Any]):
        """显示自动保存通知"""
        if not save_info.get('enabled', False):
            return

        if save_info.get('success', False):
            saved_files = save_info.get('saved_files', {})
            formats = save_info.get('formats', [])
            
            # 显示成功通知
            st.success(f"💾 **自动保存成功** - {save_info['stock_symbol']}")
            
            with st.expander("📁 查看自动保存的文件", expanded=False):
                if 'modular' in saved_files:
                    st.write("**📋 分模块报告:**")
                    for module, path in saved_files['modular'].items():
                        st.write(f"- {module}: `{Path(path).name}`")
                
                if 'markdown' in saved_files:
                    st.write("**📄 Markdown汇总报告:**")
                    st.write(f"- `{Path(saved_files['markdown']).name}`")
                
                if 'json' in saved_files:
                    st.write("**📊 JSON原始数据:**")
                    st.write(f"- `{Path(saved_files['json']).name}`")
                
                if 'docx' in saved_files:
                    st.write("**📝 Word文档:**")
                    st.write(f"- `{Path(saved_files['docx']).name}`")

                # 显示保存位置
                if saved_files:
                    first_file_path = next(iter(saved_files.values()))
                    if isinstance(first_file_path, dict):
                        first_file_path = next(iter(first_file_path.values()))
                    
                    save_dir = Path(first_file_path).parent
                    st.info(f"📁 **保存位置**: `{save_dir}`")

        else:
            reason = save_info.get('reason', 'unknown')
            error = save_info.get('error', '')
            
            if reason == 'empty_results':
                st.warning("💾 自动保存: 分析结果为空")
            elif reason == 'no_files_saved':
                st.warning("💾 自动保存: 没有文件被保存")
            elif error:
                st.error(f"💾 自动保存失败: {error}")
            else:
                st.warning("💾 自动保存失败")


# 创建全局自动保存器实例
auto_saver = AutoSaver()


def render_auto_save_settings():
    """渲染自动保存设置界面"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(79, 70, 229, 0.2);
    ">
        <h4 style="
            color: #4f46e5;
            font-weight: 700;
            margin-bottom: 1rem;
        ">💾 自动保存设置</h4>
    </div>
    """, unsafe_allow_html=True)

    # 启用/禁用自动保存
    auto_save_enabled = st.checkbox(
        "启用自动保存",
        value=st.session_state.get('auto_save_enabled', True),
        help="分析完成后自动保存结果到本地目录"
    )
    st.session_state.auto_save_enabled = auto_save_enabled

    if auto_save_enabled:
        # 选择保存格式
        st.write("**保存格式:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            save_markdown = st.checkbox(
                "📄 Markdown报告",
                value='markdown' in st.session_state.get('auto_save_formats', ['markdown']),
                help="轻量级文本格式，易于阅读和分享"
            )
            
            save_json = st.checkbox(
                "📊 JSON原始数据",
                value='json' in st.session_state.get('auto_save_formats', ['markdown']),
                help="保存完整的分析结果数据，便于程序化处理"
            )
        
        with col2:
            save_docx = st.checkbox(
                "📝 Word文档",
                value='docx' in st.session_state.get('auto_save_formats', ['markdown']),
                help="适合进一步编辑和格式化" + ("" if ReportExporter().pandoc_available else " (需要pandoc)")
            )
            
            # 显示总是保存的项目
            st.markdown("**📋 分模块报告** *(总是保存)*")
            st.caption("自动保存与CLI版本兼容的分模块报告")

        # 更新session state
        formats = []
        if save_markdown:
            formats.append('markdown')
        if save_json:
            formats.append('json')
        if save_docx and ReportExporter().pandoc_available:
            formats.append('docx')
        
        st.session_state.auto_save_formats = formats

        # 显示保存位置信息
        with st.expander("📁 保存位置信息"):
            st.info("""
            **保存位置**: `results/{股票代码}/{日期}/reports/`
            
            **文件结构**:
            ```
            results/
            └── AAPL/
                └── 2024-12-20/
                    └── reports/
                        ├── market_report.md
                        ├── fundamentals_report.md
                        ├── sentiment_report.md
                        ├── news_report.md
                        ├── investment_plan.md
                        ├── final_trade_decision.md
                        └── AAPL_analysis_20241220_143022.md
            ```
            
            💡 这种格式与CLI版本完全兼容，可以在两个界面间无缝切换。
            """)

    else:
        st.info("自动保存已禁用。分析完成后不会自动保存文件，但您仍可以使用手动导出功能。")


def auto_save_analysis_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """自动保存分析结果的便捷函数
    
    Args:
        results: 分析结果字典
        
    Returns:
        保存结果信息
    """
    return auto_saver.save_results_automatically(results)


def show_auto_save_notification(save_info: Dict[str, Any]):
    """显示自动保存通知的便捷函数"""
    auto_saver.show_auto_save_notification(save_info)