"""
分析表单组件
"""

import streamlit as st
import datetime

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')


def render_analysis_form():
    """渲染股票分析表单"""
    
    # 添加表单样式
    st.markdown("""
    <style>
    /* 分析表单样式优化 */
    .stForm {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }

    /* 表单标题样式 */
    .stForm h3 {
        color: #4f46e5;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
        font-size: 1.3rem;
    }

    /* 表单控件优化 */
    .stForm .stSelectbox > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .stForm .stSelectbox > div > div:focus-within {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        transform: translateY(-1px);
    }

    .stForm .stTextInput > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .stForm .stTextInput > div > div:focus-within {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        transform: translateY(-1px);
    }

    .stForm .stDateInput > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .stForm .stDateInput > div > div:focus-within {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        transform: translateY(-1px);
    }

    .stForm .stSlider {
        margin: 1rem 0;
    }

    .stForm .stMultiSelect > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .stForm .stMultiSelect > div > div:focus-within {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        transform: translateY(-1px);
    }

    /* 表单提交按钮样式 */
    .stForm .stFormSubmitButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 3rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        width: 100%;
        margin-top: 1rem;
    }

    .stForm .stFormSubmitButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(79, 70, 229, 0.4);
        background: linear-gradient(135deg, #4338ca 0%, #0891b2 100%);
    }

    /* 标签样式优化 */
    .stForm label {
        font-weight: 600;
        color: #495057;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }

    /* 帮助文本样式 */
    .stForm .stSelectbox [data-testid="stTooltipHoverTarget"],
    .stForm .stTextInput [data-testid="stTooltipHoverTarget"],
    .stForm .stDateInput [data-testid="stTooltipHoverTarget"] {
        color: #6c757d;
    }

    /* 列布局优化 */
    .stForm .element-container {
        margin-bottom: 1rem;
    }

    /* 动画效果 */
    .stForm {
        animation: formFadeIn 0.6s ease-out;
    }

    @keyframes formFadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 分析配置")

    # 获取缓存的表单配置
    cached_config = st.session_state.get('form_config')
    
    # 首次访问：设置默认全选
    if cached_config is None:
        default_config = {
            'selected_analysts': ['market', 'social', 'news', 'fundamentals']
        }
        st.session_state.form_config = default_config
        cached_config = default_config
        logger.debug("📊 [首次访问] 设置默认全选所有分析师")
    else:
        # 后续访问：保持上次选择
        logger.debug(f"📊 [保持选择] 使用上次的分析师选择: {cached_config.get('selected_analysts', [])}")

    # 调试信息（只在没有分析运行时记录，避免重复）
    if not st.session_state.get('analysis_running', False):
        if cached_config:
            logger.debug(f"📊 [配置恢复] 使用缓存配置: {cached_config}")
        else:
            logger.debug("📊 [配置恢复] 使用默认配置")

    # ------------------ 将分析师团队选择移到表单外，实时更新 ------------------
    st.markdown("### 👥 选择分析师团队")
    col_a, col_b = st.columns(2)

    # 获取缓存的分析师选择
    cached_analysts = cached_config.get('selected_analysts', ['market', 'social', 'news', 'fundamentals'])
    logger.debug(f"📊 [分析师选择] cached_analysts(outside form): {cached_analysts}")

    with col_a:
        market_analyst = st.checkbox(
            "📈 市场分析师",
            value='market' in cached_analysts,
            help="专注于技术面分析、价格趋势、技术指标",
            key="market_analyst_checkbox"
        )
        social_analyst = st.checkbox(
            "💭 社交媒体分析师",
            value='social' in cached_analysts,
            help="分析社交媒体情绪、投资者情绪指标",
            key="social_analyst_checkbox"
        )
    with col_b:
        news_analyst = st.checkbox(
            "📰 新闻分析师",
            value='news' in cached_analysts,
            help="分析相关新闻事件、市场动态影响",
            key="news_analyst_checkbox"
        )
        fundamentals_analyst = st.checkbox(
            "💰 基本面分析师",
            value='fundamentals' in cached_analysts,
            help="分析财务数据、公司基本面、估值水平",
            key="fundamentals_analyst_checkbox"
        )

    # 收集选中的分析师（表单外，实时更新）
    selected_analysts = []
    if market_analyst:
        selected_analysts.append(("market", "市场分析师"))
    if social_analyst:
        selected_analysts.append(("social", "社交媒体分析师"))  # 保持与后端一致的 key 'social'
    if news_analyst:
        selected_analysts.append(("news", "新闻分析师"))
    if fundamentals_analyst:
        selected_analysts.append(("fundamentals", "基本面分析师"))

    # 动态显示选择摘要（表单外，随勾选立即变化）
    if selected_analysts:
        analyst_names = [a[1] for a in selected_analysts]
        st.success(f"已选择 {len(selected_analysts)} 个分析师: {', '.join(analyst_names)}")
    else:
        st.warning("请至少选择一个分析师")

    # 同步到 form_config，避免之后的表单内逻辑被旧缓存覆盖
    try:
        st.session_state.form_config = st.session_state.get('form_config', {}) or {}
        st.session_state.form_config['selected_analysts'] = [a[0] for a in selected_analysts]
    except Exception as e:
        logger.warning(f"⚠️ [配置同步] 更新 selected_analysts 失败: {e}")
    # --------------------------------------------------------------------

    # 创建表单
    with st.form("analysis_form", clear_on_submit=False):

        # 在表单开始时保存当前配置（用于检测变化）
        initial_config = cached_config.copy() if cached_config else {}
        col1, col2 = st.columns(2)
        
        with col1:
            # 市场选择（使用缓存的值）
            market_options = ["美股", "A股", "港股"]
            cached_market = cached_config.get('market_type', 'A股') if cached_config else 'A股'
            try:
                market_index = market_options.index(cached_market)
            except (ValueError, TypeError):
                market_index = 1  # 默认A股

            market_type = st.selectbox(
                "选择市场 🌍",
                options=market_options,
                index=market_index,
                help="选择要分析的股票市场"
            )

            # 根据市场类型显示不同的输入提示
            cached_stock = cached_config.get('stock_symbol', '') if cached_config else ''

            if market_type == "美股":
                stock_symbol = st.text_input(
                    "股票代码 📈",
                    value=cached_stock if (cached_config and cached_config.get('market_type') == '美股') else '',
                    placeholder="输入美股代码，如 AAPL, TSLA, MSFT，然后按回车确认",
                    help="输入要分析的美股代码，输入完成后请按回车键确认",
                    key="us_stock_input",
                    autocomplete="off"  # 修复autocomplete警告
                ).upper().strip()

                logger.debug(f"🔍 [FORM DEBUG] 美股text_input返回值: '{stock_symbol}'")

            elif market_type == "港股":
                stock_symbol = st.text_input(
                    "股票代码 📈",
                    value=cached_stock if (cached_config and cached_config.get('market_type') == '港股') else '',
                    placeholder="输入港股代码，如 0700.HK, 9988.HK, 3690.HK，然后按回车确认",
                    help="输入要分析的港股代码，如 0700.HK(腾讯控股), 9988.HK(阿里巴巴), 3690.HK(美团)，输入完成后请按回车键确认",
                    key="hk_stock_input",
                    autocomplete="off"  # 修复autocomplete警告
                ).upper().strip()

                logger.debug(f"🔍 [FORM DEBUG] 港股text_input返回值: '{stock_symbol}'")

            else:  # A股
                stock_symbol = st.text_input(
                    "股票代码 📈",
                    value=cached_stock if (cached_config and cached_config.get('market_type') == 'A股') else '',
                    placeholder="输入A股代码，如 000001, 600519，然后按回车确认",
                    help="输入要分析的A股代码，如 000001(平安银行), 600519(贵州茅台)，输入完成后请按回车键确认",
                    key="cn_stock_input",
                    autocomplete="off"  # 修复autocomplete警告
                ).strip()

                logger.debug(f"🔍 [FORM DEBUG] A股text_input返回值: '{stock_symbol}'")
            
            # 分析日期
            analysis_date = st.date_input(
                "分析日期 📅",
                value=datetime.date.today(),
                help="选择分析的基准日期"
            )
        
        with col2:
            # 研究深度（使用缓存的值）
            cached_depth = cached_config.get('research_depth', 3) if cached_config else 3
            research_depth = st.select_slider(
                "研究深度 🔍",
                options=[1, 2, 3, 4, 5],
                value=cached_depth,
                format_func=lambda x: {
                    1: "1级 - 快速分析",
                    2: "2级 - 基础分析",
                    3: "3级 - 标准分析",
                    4: "4级 - 深度分析",
                    5: "5级 - 全面分析"
                }[x],
                help="选择分析的深度级别，级别越高分析越详细但耗时更长"
            )
        
        # 高级选项
        with st.expander("🔧 高级选项"):
            include_sentiment = st.checkbox(
                "包含情绪分析",
                value=True,
                help="是否包含市场情绪和投资者情绪分析"
            )
            
            include_risk_assessment = st.checkbox(
                "包含风险评估",
                value=True,
                help="是否包含详细的风险因素评估"
            )
            
            custom_prompt = st.text_area(
                "自定义分析要求",
                placeholder="输入特定的分析要求或关注点...",
                help="可以输入特定的分析要求，AI会在分析中重点关注"
            )

        # 显示输入状态提示
        if not stock_symbol:
            st.info("💡 请在上方输入股票代码，输入完成后按回车键确认")
        else:
            st.success(f"✅ 已输入股票代码: {stock_symbol}")

        # 添加JavaScript来改善用户体验
        st.markdown("""
        <script>
        // 监听输入框的变化，提供更好的用户反馈
        document.addEventListener('DOMContentLoaded', function() {
            const inputs = document.querySelectorAll('input[type="text"]');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    if (this.value.trim()) {
                        this.style.borderColor = '#00ff00';
                        this.title = '按回车键确认输入';
                    } else {
                        this.style.borderColor = '';
                        this.title = '';
                    }
                });
            });
        });
        </script>
        """, unsafe_allow_html=True)

        # 在提交按钮前检测配置变化并保存
        current_config = {
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'research_depth': research_depth,
            'selected_analysts': [a[0] for a in selected_analysts],
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }

        # 实时保存用户选择（避免缓存覆盖用户选择）
        st.session_state.form_config = current_config
        try:
            from utils.smart_session_manager import smart_session_manager
            current_analysis_id = st.session_state.get('current_analysis_id', 'form_config_only')
            smart_session_manager.save_analysis_state(
                analysis_id=current_analysis_id,
                status=st.session_state.get('analysis_running', False) and 'running' or 'idle',
                stock_symbol=stock_symbol,
                market_type=market_type,
                form_config=current_config
            )
            logger.debug(f"📊 [配置自动保存] 表单配置已更新")
        except Exception as e:
            logger.warning(f"⚠️ [配置自动保存] 保存失败: {e}")

        # 提交按钮（不禁用，让用户可以点击）
        submitted = st.form_submit_button(
            "🚀 开始分析",
            type="primary",
            use_container_width=True
        )

    # 只有在提交时才返回数据
    if submitted and stock_symbol:  # 确保有股票代码才提交
        # 添加详细日志
        logger.debug(f"🔍 [FORM DEBUG] ===== 分析表单提交 =====")
        logger.debug(f"🔍 [FORM DEBUG] 用户输入的股票代码: '{stock_symbol}'")
        logger.debug(f"🔍 [FORM DEBUG] 市场类型: '{market_type}'")
        logger.debug(f"🔍 [FORM DEBUG] 分析日期: '{analysis_date}'")
        logger.debug(f"🔍 [FORM DEBUG] 选择的分析师: {[a[0] for a in selected_analysts]}")
        logger.debug(f"🔍 [FORM DEBUG] 研究深度: {research_depth}")

        form_data = {
            'submitted': True,
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'analysis_date': str(analysis_date),
            'analysts': [a[0] for a in selected_analysts],
            'research_depth': research_depth,
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }

        # 保存表单配置到缓存和持久化存储
        form_config = {
            'stock_symbol': stock_symbol,
            'market_type': market_type,
            'research_depth': research_depth,
            'selected_analysts': [a[0] for a in selected_analysts],
            'include_sentiment': include_sentiment,
            'include_risk_assessment': include_risk_assessment,
            'custom_prompt': custom_prompt
        }
        st.session_state.form_config = form_config

        # 保存到持久化存储
        try:
            from utils.smart_session_manager import smart_session_manager
            # 获取当前分析ID（如果有的话）
            current_analysis_id = st.session_state.get('current_analysis_id', 'form_config_only')
            smart_session_manager.save_analysis_state(
                analysis_id=current_analysis_id,
                status=st.session_state.get('analysis_running', False) and 'running' or 'idle',
                stock_symbol=stock_symbol,
                market_type=market_type,
                form_config=form_config
            )
        except Exception as e:
            logger.warning(f"⚠️ [配置持久化] 保存失败: {e}")

        logger.info(f"📊 [配置缓存] 表单配置已保存: {form_config}")

        logger.debug(f"🔍 [FORM DEBUG] 返回的表单数据: {form_data}")
        logger.debug(f"🔍 [FORM DEBUG] ===== 表单提交结束 =====")

        return form_data
    elif submitted and not stock_symbol:
        # 用户点击了提交但没有输入股票代码
        logger.error(f"🔍 [FORM DEBUG] 提交失败：股票代码为空")
        st.error("❌ 请输入股票代码后再提交")
        return {'submitted': False}
    else:
        return {'submitted': False}
