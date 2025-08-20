#!/usr/bin/env python3
"""
配置管理页面 - 增强版
支持环境变量重载、实时状态显示和配置验证
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import time
import json

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入UI工具函数
sys.path.append(str(Path(__file__).parent.parent))
from utils.ui_utils import apply_hide_deploy_button_css
from utils.config_reloader import config_reloader

from tradingagents.config.config_manager import (
    config_manager, ModelConfig, PricingConfig
)

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')


def render_config_management():
    """渲染配置管理页面 - 增强版"""
    # 应用隐藏Deploy按钮的CSS样式
    apply_hide_deploy_button_css()
    
    st.title("⚙️ 配置管理")
    
    # 添加配置重载控制面板
    render_config_reload_panel()

    # 侧边栏选择功能
    st.sidebar.title("配置选项")
    page = st.sidebar.selectbox(
        "选择功能",
        ["环境配置状态", "API密钥管理", "数据库配置", "系统设置", "模型配置", "定价设置", "使用统计"]
    )
    
    if page == "环境配置状态":
        render_environment_status()
    elif page == "API密钥管理":
        render_api_keys_management()
    elif page == "数据库配置":
        render_database_config()
    elif page == "系统设置":
        render_system_settings()
    elif page == "模型配置":
        render_model_config()
    elif page == "定价设置":
        render_pricing_config()
    elif page == "使用统计":
        render_usage_statistics()

def render_config_reload_panel():
    """渲染配置重载控制面板"""
    st.markdown("### 🔄 配置管理控制台")
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
    
    with col1:
        if st.button("🔄 重新加载配置", type="primary", help="重新加载.env文件中的环境变量"):
            with st.spinner("正在重新加载配置..."):
                success, message, stats = config_reloader.reload_environment_variables()
                
                if success:
                    st.success(message)
                    
                    if stats.get("total_changes", 0) > 0:
                        st.info(f"📊 配置变更统计：新增 {stats.get('new_keys', 0)} 个，更新 {stats.get('updated_keys', 0)} 个，移除 {stats.get('removed_keys', 0)} 个")
                        
                        # 显示变更详情
                        if st.expander("📋 查看详细变更"):
                            for key, change in stats.get("changes", {}).items():
                                if change["type"] == "new":
                                    st.success(f"➕ {key}: 新增配置")
                                elif change["type"] == "updated":  
                                    st.info(f"🔄 {key}: 配置已更新")
                                elif change["type"] == "removed":
                                    st.warning(f"➖ {key}: 配置已移除")
                    
                    # 自动刷新页面以反映最新状态
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        if st.button("📊 获取配置状态", help="查看当前环境变量配置状态"):
            st.session_state['show_config_status'] = True
            st.rerun()
    
    with col3:
        if st.button("✅ 验证所有配置", help="运行配置验证检查"):
            st.session_state['show_validation_results'] = True
            st.rerun()
    
    with col4:
        # 显示.env文件状态
        config_status = config_reloader.get_current_config_status()
        if config_status.get("env_file_exists", False):
            file_size = config_status.get("env_file_size", 0)
            modified_time = datetime.fromtimestamp(config_status.get("env_file_modified", 0))
            st.success(f"📄 .env文件: {file_size}字节, 修改于 {modified_time.strftime('%H:%M:%S')}")
        else:
            st.error("❌ .env文件不存在")
    
    st.markdown("---")

def render_environment_status():
    """渲染环境配置状态页面"""
    st.markdown("### 🔍 环境配置状态")
    
    # 获取当前配置状态
    status = config_reloader.get_current_config_status()
    
    if "error" in status:
        st.error(f"❌ 获取配置状态失败: {status['error']}")
        return
    
    # 显示综合验证结果
    validation = status.get("validation_results", {})
    overall_status = validation.get("overall_status", "unknown")
    
    if overall_status == "healthy":
        st.success("✅ 配置状态良好")
    elif overall_status == "warning":
        st.warning("⚠️ 配置存在警告")
    elif overall_status == "critical":
        st.error("❌ 配置存在严重问题")
    else:
        st.info("❓ 配置状态未知")
    
    # 显示关键问题和警告
    if validation.get("critical_issues"):
        st.markdown("#### ❌ 严重问题")
        for issue in validation["critical_issues"]:
            st.error(issue)
    
    if validation.get("warnings"):
        st.markdown("#### ⚠️ 警告")
        for warning in validation["warnings"]:
            st.warning(warning)
    
    if validation.get("recommendations"):
        st.markdown("#### 💡 建议")
        for rec in validation["recommendations"]:
            st.info(rec)
    
    # 显示配置分类统计
    col1, col2, col3 = st.columns(3)
    
    with col1:
        api_keys = status.get("api_keys", {})
        configured_apis = sum(1 for key, info in api_keys.items() if info.get("configured", False))
        total_apis = len(api_keys)
        
        st.metric(
            "API密钥配置", 
            f"{configured_apis}/{total_apis}",
            help="已配置的API密钥数量"
        )
    
    with col2:
        db_config = status.get("database_config", {})
        configured_db = sum(1 for key, info in db_config.items() if info.get("configured", False))
        total_db = len(db_config)
        
        st.metric(
            "数据库配置",
            f"{configured_db}/{total_db}",
            help="已配置的数据库设置数量"
        )
    
    with col3:
        sys_config = status.get("system_config", {})
        configured_sys = sum(1 for key, info in sys_config.items() if info.get("configured", False))
        total_sys = len(sys_config)
        
        st.metric(
            "系统配置",
            f"{configured_sys}/{total_sys}",
            help="已配置的系统设置数量"
        )

def render_api_keys_management():
    """渲染API密钥管理页面"""
    st.markdown("### 🔑 API密钥管理")
    
    # 获取API密钥状态
    status = config_reloader.get_current_config_status()
    api_keys = status.get("api_keys", {})
    
    if not api_keys:
        st.warning("⚠️ 无法获取API密钥状态")
        return
    
    # 创建API密钥状态表格
    api_data = []
    for key, info in api_keys.items():
        validation = info.get("validation", {})
        api_data.append({
            "API密钥": key,
            "状态": "✅ 已配置" if info.get("configured", False) else "❌ 未配置",
            "掩码值": info.get("masked_value", ""),
            "验证结果": validation.get("message", "未知"),
            "验证状态": {
                "success": "✅ 正常",
                "warning": "⚠️ 警告", 
                "error": "❌ 错误",
                "info": "ℹ️ 信息"
            }.get(validation.get("level", "info"), "❓ 未知")
        })
    
    df = pd.DataFrame(api_data)
    
    # 显示表格
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # 分类显示
    st.markdown("#### 📊 配置详情")
    
    # 分组显示API密钥
    providers = {
        "核心AI提供商": ["DASHSCOPE_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "DEEPSEEK_API_KEY"],
        "其他AI服务": ["VOLCENGINE_API_KEY", "CUSTOM_OPENAI_API_KEY", "OPENROUTER_API_KEY"],
        "数据服务": ["FINNHUB_API_KEY", "TUSHARE_TOKEN"]
    }
    
    for category, keys in providers.items():
        with st.expander(f"{category} ({sum(1 for k in keys if api_keys.get(k, {}).get('configured', False))}/{len(keys)})"):
            for key in keys:
                if key in api_keys:
                    info = api_keys[key]
                    validation = info.get("validation", {})
                    
                    col1, col2, col3 = st.columns([2, 2, 3])
                    
                    with col1:
                        st.write(f"**{key}**")
                    
                    with col2:
                        if info.get("configured", False):
                            st.success("已配置")
                        else:
                            st.error("未配置")
                    
                    with col3:
                        level = validation.get("level", "info")
                        message = validation.get("message", "无验证信息")
                        
                        if level == "success":
                            st.success(message)
                        elif level == "warning":
                            st.warning(message)
                        elif level == "error":
                            st.error(message)
                        else:
                            st.info(message)

def render_database_config():
    """渲染数据库配置页面"""
    st.markdown("### 🗄️ 数据库配置")
    
    # 获取数据库配置状态
    status = config_reloader.get_current_config_status()
    db_config = status.get("database_config", {})
    
    if not db_config:
        st.warning("⚠️ 无法获取数据库配置状态")
        return
    
    # MongoDB配置
    with st.expander("📊 MongoDB 配置", expanded=True):
        mongodb_info = db_config.get("TRADINGAGENTS_MONGODB_URL", {})
        validation = mongodb_info.get("validation", {})
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if mongodb_info.get("configured", False):
                st.success("✅ 已配置")
            else:
                st.error("❌ 未配置")
        
        with col2:
            level = validation.get("level", "info")
            message = validation.get("message", "无验证信息")
            
            if level == "success":
                st.success(message)
            elif level == "warning":
                st.warning(message)
            elif level == "error":
                st.error(message)
            else:
                st.info(message)
        
        if mongodb_info.get("configured", False):
            masked_url = mongodb_info.get("value", "")
            st.code(masked_url, language="text")
    
    # Redis配置
    with st.expander("🔴 Redis 配置", expanded=True):
        redis_info = db_config.get("TRADINGAGENTS_REDIS_URL", {})
        validation = redis_info.get("validation", {})
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if redis_info.get("configured", False):
                st.success("✅ 已配置")
            else:
                st.error("❌ 未配置")
        
        with col2:
            level = validation.get("level", "info")
            message = validation.get("message", "无验证信息")
            
            if level == "success":
                st.success(message)
            elif level == "warning":
                st.warning(message)
            elif level == "error":
                st.error(message)
            else:
                st.info(message)
        
        if redis_info.get("configured", False):
            masked_url = redis_info.get("value", "")
            st.code(masked_url, language="text")
    
    # 缓存类型配置
    with st.expander("💾 缓存配置", expanded=True):
        cache_info = db_config.get("TRADINGAGENTS_CACHE_TYPE", {})
        validation = cache_info.get("validation", {})
        
        cache_value = cache_info.get("value", "redis")
        st.info(f"当前缓存类型: **{cache_value}**")
        
        level = validation.get("level", "info")
        message = validation.get("message", "无验证信息")
        
        if level == "success":
            st.success(message)
        elif level == "warning":
            st.warning(message)
        elif level == "error":
            st.error(message)
        else:
            st.info(message)


def render_model_config():
    """渲染模型配置页面"""
    st.markdown("**🤖 模型配置**")

    # 加载现有配置
    models = config_manager.load_models()

    # 显示当前配置
    st.markdown("**当前模型配置**")
    
    if models:
        # 创建DataFrame显示
        model_data = []
        env_status = config_manager.get_env_config_status()

        for i, model in enumerate(models):
            # 检查API密钥来源
            env_has_key = env_status["api_keys"].get(model.provider.lower(), False)
            api_key_display = "***" + model.api_key[-4:] if model.api_key else "未设置"
            if env_has_key:
                api_key_display += " (.env)"

            model_data.append({
                "序号": i,
                "供应商": model.provider,
                "模型名称": model.model_name,
                "API密钥": api_key_display,
                "最大Token": model.max_tokens,
                "温度": model.temperature,
                "状态": "✅ 启用" if model.enabled else "❌ 禁用"
            })
        
        df = pd.DataFrame(model_data)
        st.dataframe(df, use_container_width=True)
        
        # 编辑模型配置
        st.markdown("**编辑模型配置**")
        
        # 选择要编辑的模型
        model_options = [f"{m.provider} - {m.model_name}" for m in models]
        selected_model_idx = st.selectbox("选择要编辑的模型", range(len(model_options)),
                                         format_func=lambda x: model_options[x],
                                         key="select_model_to_edit")
        
        if selected_model_idx is not None:
            model = models[selected_model_idx]

            # 检查是否来自.env
            env_has_key = env_status["api_keys"].get(model.provider.lower(), False)
            if env_has_key:
                st.info(f"💡 此模型的API密钥来自 .env 文件，修改 .env 文件后需重启应用生效")

            col1, col2 = st.columns(2)

            with col1:
                new_api_key = st.text_input("API密钥", value=model.api_key, type="password", key=f"edit_api_key_{selected_model_idx}")
                if env_has_key:
                    st.caption("⚠️ 此密钥来自 .env 文件，Web修改可能被覆盖")
                new_max_tokens = st.number_input("最大Token数", value=model.max_tokens, min_value=1000, max_value=32000, key=f"edit_max_tokens_{selected_model_idx}")
                new_temperature = st.slider("温度参数", 0.0, 2.0, model.temperature, 0.1, key=f"edit_temperature_{selected_model_idx}")

            with col2:
                new_enabled = st.checkbox("启用模型", value=model.enabled, key=f"edit_enabled_{selected_model_idx}")
                new_base_url = st.text_input("自定义API地址 (可选)", value=model.base_url or "", key=f"edit_base_url_{selected_model_idx}")
            
            if st.button("保存配置", type="primary", key=f"save_model_config_{selected_model_idx}"):
                # 更新模型配置
                models[selected_model_idx] = ModelConfig(
                    provider=model.provider,
                    model_name=model.model_name,
                    api_key=new_api_key,
                    base_url=new_base_url if new_base_url else None,
                    max_tokens=new_max_tokens,
                    temperature=new_temperature,
                    enabled=new_enabled
                )
                
                config_manager.save_models(models)
                st.success("✅ 配置已保存！")
                st.rerun()
    
    else:
        st.warning("没有找到模型配置")
    
    # 添加新模型
    st.markdown("**添加新模型**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_provider = st.selectbox("供应商", ["dashscope", "openai", "google", "anthropic", "other"], key="new_provider")
        new_model_name = st.text_input("模型名称", placeholder="例如: gpt-4, qwen-plus-latest", key="new_model_name")
        new_api_key = st.text_input("API密钥", type="password", key="new_api_key")

    with col2:
        new_max_tokens = st.number_input("最大Token数", value=4000, min_value=1000, max_value=32000, key="new_max_tokens")
        new_temperature = st.slider("温度参数", 0.0, 2.0, 0.7, 0.1, key="new_temperature")
        new_enabled = st.checkbox("启用模型", value=True, key="new_enabled")
    
    if st.button("添加模型", key="add_new_model"):
        if new_provider and new_model_name and new_api_key:
            new_model = ModelConfig(
                provider=new_provider,
                model_name=new_model_name,
                api_key=new_api_key,
                max_tokens=new_max_tokens,
                temperature=new_temperature,
                enabled=new_enabled
            )
            
            models.append(new_model)
            config_manager.save_models(models)
            st.success("✅ 新模型已添加！")
            st.rerun()
        else:
            st.error("请填写所有必需字段")


def render_pricing_config():
    """渲染定价配置页面"""
    st.markdown("**💰 定价设置**")

    # 加载现有定价
    pricing_configs = config_manager.load_pricing()

    # 显示当前定价
    st.markdown("**当前定价配置**")
    
    if pricing_configs:
        pricing_data = []
        for i, pricing in enumerate(pricing_configs):
            pricing_data.append({
                "序号": i,
                "供应商": pricing.provider,
                "模型名称": pricing.model_name,
                "输入价格 (每1K token)": f"{pricing.input_price_per_1k} {pricing.currency}",
                "输出价格 (每1K token)": f"{pricing.output_price_per_1k} {pricing.currency}",
                "货币": pricing.currency
            })
        
        df = pd.DataFrame(pricing_data)
        st.dataframe(df, use_container_width=True)
        
        # 编辑定价
        st.markdown("**编辑定价**")
        
        pricing_options = [f"{p.provider} - {p.model_name}" for p in pricing_configs]
        selected_pricing_idx = st.selectbox("选择要编辑的定价", range(len(pricing_options)),
                                          format_func=lambda x: pricing_options[x],
                                          key="select_pricing_to_edit")
        
        if selected_pricing_idx is not None:
            pricing = pricing_configs[selected_pricing_idx]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_input_price = st.number_input("输入价格 (每1K token)",
                                                value=pricing.input_price_per_1k,
                                                min_value=0.0, step=0.001, format="%.6f",
                                                key=f"edit_input_price_{selected_pricing_idx}")

            with col2:
                new_output_price = st.number_input("输出价格 (每1K token)",
                                                 value=pricing.output_price_per_1k,
                                                 min_value=0.0, step=0.001, format="%.6f",
                                                 key=f"edit_output_price_{selected_pricing_idx}")

            with col3:
                new_currency = st.selectbox("货币", ["CNY", "USD", "EUR"],
                                          index=["CNY", "USD", "EUR"].index(pricing.currency),
                                          key=f"edit_currency_{selected_pricing_idx}")
            
            if st.button("保存定价", type="primary", key=f"save_pricing_config_{selected_pricing_idx}"):
                pricing_configs[selected_pricing_idx] = PricingConfig(
                    provider=pricing.provider,
                    model_name=pricing.model_name,
                    input_price_per_1k=new_input_price,
                    output_price_per_1k=new_output_price,
                    currency=new_currency
                )
                
                config_manager.save_pricing(pricing_configs)
                st.success("✅ 定价已保存！")
                st.rerun()
    
    # 添加新定价
    st.markdown("**添加新定价**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_provider = st.text_input("供应商", placeholder="例如: openai, dashscope", key="new_pricing_provider")
        new_model_name = st.text_input("模型名称", placeholder="例如: gpt-4, qwen-plus", key="new_pricing_model")
        new_currency = st.selectbox("货币", ["CNY", "USD", "EUR"], key="new_pricing_currency")

    with col2:
        new_input_price = st.number_input("输入价格 (每1K token)", min_value=0.0, step=0.001, format="%.6f", key="new_pricing_input")
        new_output_price = st.number_input("输出价格 (每1K token)", min_value=0.0, step=0.001, format="%.6f", key="new_pricing_output")
    
    if st.button("添加定价", key="add_new_pricing"):
        if new_provider and new_model_name:
            new_pricing = PricingConfig(
                provider=new_provider,
                model_name=new_model_name,
                input_price_per_1k=new_input_price,
                output_price_per_1k=new_output_price,
                currency=new_currency
            )
            
            pricing_configs.append(new_pricing)
            config_manager.save_pricing(pricing_configs)
            st.success("✅ 新定价已添加！")
            st.rerun()
        else:
            st.error("请填写供应商和模型名称")


def render_usage_statistics():
    """渲染使用统计页面"""
    st.markdown("**📊 使用统计**")

    # 时间范围选择
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("统计时间范围", [7, 30, 90, 365], index=1, key="stats_time_range")
    with col2:
        st.metric("统计周期", f"最近 {days} 天")

    # 获取统计数据
    stats = config_manager.get_usage_statistics(days)

    if stats["total_requests"] == 0:
        st.info("📝 暂无使用记录")
        return

    # 总体统计
    st.markdown("**📈 总体统计**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总成本", f"¥{stats['total_cost']:.4f}")
    
    with col2:
        st.metric("总请求数", f"{stats['total_requests']:,}")
    
    with col3:
        st.metric("输入Token", f"{stats['total_input_tokens']:,}")
    
    with col4:
        st.metric("输出Token", f"{stats['total_output_tokens']:,}")
    
    # 按供应商统计
    if stats["provider_stats"]:
        st.markdown("**🏢 按供应商统计**")
        
        provider_data = []
        for provider, data in stats["provider_stats"].items():
            provider_data.append({
                "供应商": provider,
                "成本": f"¥{data['cost']:.4f}",
                "请求数": data['requests'],
                "输入Token": f"{data['input_tokens']:,}",
                "输出Token": f"{data['output_tokens']:,}",
                "平均成本/请求": f"¥{data['cost']/data['requests']:.6f}" if data['requests'] > 0 else "¥0"
            })
        
        df = pd.DataFrame(provider_data)
        st.dataframe(df, use_container_width=True)
        
        # 成本分布饼图
        if len(provider_data) > 1:
            fig = px.pie(
                values=[stats["provider_stats"][p]["cost"] for p in stats["provider_stats"]],
                names=list(stats["provider_stats"].keys()),
                title="成本分布"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 使用趋势
    st.markdown("**📈 使用趋势**")
    
    records = config_manager.load_usage_records()
    if records:
        # 按日期聚合
        daily_stats = {}
        for record in records:
            try:
                date = datetime.fromisoformat(record.timestamp).date()
                if date not in daily_stats:
                    daily_stats[date] = {"cost": 0, "requests": 0}
                daily_stats[date]["cost"] += record.cost
                daily_stats[date]["requests"] += 1
            except:
                continue
        
        if daily_stats:
            dates = sorted(daily_stats.keys())
            costs = [daily_stats[date]["cost"] for date in dates]
            requests = [daily_stats[date]["requests"] for date in dates]
            
            # 创建双轴图表
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=costs,
                mode='lines+markers',
                name='每日成本 (¥)',
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=requests,
                mode='lines+markers',
                name='每日请求数',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title='使用趋势',
                xaxis_title='日期',
                yaxis=dict(title='成本 (¥)', side='left'),
                yaxis2=dict(title='请求数', side='right', overlaying='y'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)


def render_system_settings():
    """渲染系统设置页面"""
    st.markdown("**🔧 系统设置**")

    # 加载当前设置
    settings = config_manager.load_settings()

    st.markdown("**基本设置**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_provider = st.selectbox(
            "默认供应商",
            ["dashscope", "openai", "google", "anthropic"],
            index=["dashscope", "openai", "google", "anthropic"].index(
                settings.get("default_provider", "dashscope")
            ),
            key="settings_default_provider"
        )

        enable_cost_tracking = st.checkbox(
            "启用成本跟踪",
            value=settings.get("enable_cost_tracking", True),
            key="settings_enable_cost_tracking"
        )

        currency_preference = st.selectbox(
            "首选货币",
            ["CNY", "USD", "EUR"],
            index=["CNY", "USD", "EUR"].index(
                settings.get("currency_preference", "CNY")
            ),
            key="settings_currency_preference"
        )
    
    with col2:
        default_model = st.text_input(
            "默认模型",
            value=settings.get("default_model", "qwen-turbo"),
            key="settings_default_model"
        )

        cost_alert_threshold = st.number_input(
            "成本警告阈值",
            value=settings.get("cost_alert_threshold", 100.0),
            min_value=0.0,
            step=10.0,
            key="settings_cost_alert_threshold"
        )

        max_usage_records = st.number_input(
            "最大使用记录数",
            value=settings.get("max_usage_records", 10000),
            min_value=1000,
            max_value=100000,
            step=1000,
            key="settings_max_usage_records"
        )

    auto_save_usage = st.checkbox(
        "自动保存使用记录",
        value=settings.get("auto_save_usage", True),
        key="settings_auto_save_usage"
    )
    
    if st.button("保存设置", type="primary", key="save_system_settings"):
        new_settings = {
            "default_provider": default_provider,
            "default_model": default_model,
            "enable_cost_tracking": enable_cost_tracking,
            "cost_alert_threshold": cost_alert_threshold,
            "currency_preference": currency_preference,
            "auto_save_usage": auto_save_usage,
            "max_usage_records": max_usage_records
        }
        
        config_manager.save_settings(new_settings)
        st.success("✅ 设置已保存！")
        st.rerun()
    
    # 数据管理
    st.markdown("**数据管理**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("导出配置", help="导出所有配置到JSON文件", key="export_config"):
            # 这里可以实现配置导出功能
            st.info("配置导出功能开发中...")
    
    with col2:
        if st.button("清空使用记录", help="清空所有使用记录", key="clear_usage_records"):
            if st.session_state.get("confirm_clear", False):
                config_manager.save_usage_records([])
                st.success("✅ 使用记录已清空！")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ 再次点击确认清空")
    
    with col3:
        if st.button("重置配置", help="重置所有配置到默认值", key="reset_all_config"):
            if st.session_state.get("confirm_reset", False):
                # 删除配置文件，重新初始化
                import shutil
                if config_manager.config_dir.exists():
                    shutil.rmtree(config_manager.config_dir)
                config_manager._init_default_configs()
                st.success("✅ 配置已重置！")
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ 再次点击确认重置")


def render_env_status():
    """显示.env配置状态"""
    st.markdown("**📋 配置状态概览**")

    # 获取.env配置状态
    env_status = config_manager.get_env_config_status()

    # 显示.env文件状态
    col1, col2 = st.columns(2)

    with col1:
        if env_status["env_file_exists"]:
            st.success("✅ .env 文件已存在")
        else:
            st.error("❌ .env 文件不存在")
            st.info("💡 请复制 .env.example 为 .env 并配置API密钥")

    with col2:
        # 统计已配置的API密钥数量
        configured_keys = sum(1 for configured in env_status["api_keys"].values() if configured)
        total_keys = len(env_status["api_keys"])
        st.metric("API密钥配置", f"{configured_keys}/{total_keys}")

    # 详细API密钥状态
    with st.expander("🔑 API密钥详细状态", expanded=False):
        api_col1, api_col2 = st.columns(2)

        with api_col1:
            st.write("**大模型API密钥:**")
            for provider, configured in env_status["api_keys"].items():
                if provider in ["dashscope", "openai", "google", "anthropic"]:
                    status = "✅ 已配置" if configured else "❌ 未配置"
                    provider_name = {
                        "dashscope": "阿里百炼",
                        "openai": "OpenAI",
                        "google": "Google AI",
                        "anthropic": "Anthropic"
                    }.get(provider, provider)
                    st.write(f"- {provider_name}: {status}")

        with api_col2:
            st.write("**其他API密钥:**")
            finnhub_status = "✅ 已配置" if env_status["api_keys"]["finnhub"] else "❌ 未配置"
            st.write(f"- FinnHub (金融数据): {finnhub_status}")

            reddit_status = "✅ 已配置" if env_status["other_configs"]["reddit_configured"] else "❌ 未配置"
            st.write(f"- Reddit API: {reddit_status}")

    # 配置优先级说明
    st.info("""
    📌 **配置优先级说明:**
    - API密钥优先从 `.env` 文件读取
    - Web界面配置作为补充和管理工具
    - 修改 `.env` 文件后需重启应用生效
    - 推荐使用 `.env` 文件管理敏感信息
    """)

    st.divider()


def main():
    """主函数"""
    st.set_page_config(
        page_title="配置管理 - TradingAgents",
        page_icon="⚙️",
        layout="wide"
    )
    
    render_config_management()

if __name__ == "__main__":
    main()
