#!/usr/bin/env python3
"""
配置重载工具
支持环境变量的动态重载和验证
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dotenv import load_dotenv
import re

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

class ConfigReloader:
    """配置重载器"""
    
    def __init__(self):
        """初始化配置重载器"""
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / ".env"
        self._last_reload_time = 0
        
        # 重要的API密钥配置
        self.important_keys = [
            "DASHSCOPE_API_KEY",
            "OPENAI_API_KEY", 
            "GOOGLE_API_KEY",
            "DEEPSEEK_API_KEY",
            "VOLCENGINE_API_KEY",
            "CUSTOM_OPENAI_API_KEY",
            "OPENROUTER_API_KEY",
            "FINNHUB_API_KEY",
            "TUSHARE_TOKEN"
        ]
        
        # 数据库配置
        self.database_keys = [
            "TRADINGAGENTS_MONGODB_URL",
            "TRADINGAGENTS_REDIS_URL",
            "TRADINGAGENTS_CACHE_TYPE"
        ]
        
        # 系统配置
        self.system_keys = [
            "MEMORY_ENABLED",
            "TRADINGAGENTS_LOG_LEVEL",
            "TRADINGAGENTS_LOG_DIR",
            "TRADINGAGENTS_RESULTS_DIR"
        ]
        
        logger.info("🔧 配置重载器已初始化")

    def reload_environment_variables(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        重新加载环境变量
        
        Returns:
            Tuple[bool, str, Dict]: (成功状态, 消息, 统计信息)
        """
        try:
            if not self.env_file.exists():
                return False, f"❌ .env文件不存在: {self.env_file}", {}
            
            # 记录重载前的值（仅记录重要配置）
            before_values = {}
            for key in self.important_keys + self.database_keys + self.system_keys:
                before_values[key] = os.getenv(key, "")
            
            # 重新加载.env文件
            result = load_dotenv(self.env_file, override=True)
            
            if not result:
                return False, "❌ .env文件加载失败", {}
            
            # 记录重载后的值
            after_values = {}
            for key in self.important_keys + self.database_keys + self.system_keys:
                after_values[key] = os.getenv(key, "")
            
            # 比较变化
            changes = {}
            new_keys = 0
            updated_keys = 0
            
            for key in before_values:
                before_val = before_values[key]
                after_val = after_values[key]
                
                if before_val != after_val:
                    if before_val == "" and after_val != "":
                        changes[key] = {"type": "new", "from": "", "to": self._mask_sensitive_value(key, after_val)}
                        new_keys += 1
                    elif before_val != "" and after_val == "":
                        changes[key] = {"type": "removed", "from": self._mask_sensitive_value(key, before_val), "to": ""}
                    else:
                        changes[key] = {"type": "updated", "from": self._mask_sensitive_value(key, before_val), "to": self._mask_sensitive_value(key, after_val)}
                        updated_keys += 1
            
            # 触发配置管理器重新初始化
            try:
                # 重新初始化配置管理器
                sys.path.insert(0, str(self.project_root))
                from tradingagents.config.config_manager import config_manager
                config_manager._load_environment_variables()
                logger.info("✅ 配置管理器已重新初始化")
            except Exception as e:
                logger.warning(f"⚠️ 配置管理器重新初始化失败: {e}")
            
            self._last_reload_time = time.time()
            
            # 生成统计信息
            stats = {
                "total_changes": len(changes),
                "new_keys": new_keys,
                "updated_keys": updated_keys,
                "removed_keys": len([c for c in changes.values() if c["type"] == "removed"]),
                "changes": changes,
                "reload_time": self._last_reload_time
            }
            
            message = f"✅ 环境变量重新加载成功"
            if stats["total_changes"] > 0:
                message += f"，检测到 {stats['total_changes']} 个配置变更"
            else:
                message += "，未检测到配置变更"
            
            logger.info(f"🔄 {message}")
            
            return True, message, stats
            
        except Exception as e:
            error_msg = f"❌ 环境变量重新加载失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, {}

    def get_current_config_status(self) -> Dict[str, Any]:
        """
        获取当前配置状态
        
        Returns:
            Dict: 当前配置状态信息
        """
        try:
            status = {
                "env_file_exists": self.env_file.exists(),
                "env_file_path": str(self.env_file),
                "env_file_size": 0,
                "env_file_modified": 0,
                "last_reload_time": self._last_reload_time,
                "api_keys": {},
                "database_config": {},
                "system_config": {},
                "validation_results": {}
            }
            
            # 文件信息
            if status["env_file_exists"]:
                file_stat = self.env_file.stat()
                status["env_file_size"] = file_stat.st_size
                status["env_file_modified"] = file_stat.st_mtime
            
            # API密钥状态
            for key in self.important_keys:
                value = os.getenv(key, "")
                status["api_keys"][key] = {
                    "configured": bool(value),
                    "masked_value": self._mask_sensitive_value(key, value),
                    "validation": self._validate_api_key(key, value)
                }
            
            # 数据库配置状态
            for key in self.database_keys:
                value = os.getenv(key, "")
                status["database_config"][key] = {
                    "configured": bool(value),
                    "value": value if not self._is_sensitive_key(key) else self._mask_sensitive_value(key, value),
                    "validation": self._validate_database_config(key, value)
                }
            
            # 系统配置状态
            for key in self.system_keys:
                value = os.getenv(key, "")
                status["system_config"][key] = {
                    "configured": bool(value),
                    "value": value,
                    "validation": self._validate_system_config(key, value)
                }
            
            # 整体验证结果
            status["validation_results"] = self._run_comprehensive_validation()
            
            return status
            
        except Exception as e:
            logger.error(f"❌ 获取配置状态失败: {e}")
            return {"error": str(e)}

    def _mask_sensitive_value(self, key: str, value: str) -> str:
        """屏蔽敏感值"""
        if not value:
            return ""
        
        if self._is_sensitive_key(key):
            if len(value) <= 8:
                return "*" * len(value)
            else:
                return value[:4] + "*" * (len(value) - 8) + value[-4:]
        else:
            return value

    def _is_sensitive_key(self, key: str) -> bool:
        """判断是否为敏感配置键"""
        sensitive_patterns = [
            "API_KEY", "TOKEN", "PASSWORD", "SECRET", "PRIVATE",
            "MONGODB_URL", "REDIS_URL"
        ]
        return any(pattern in key.upper() for pattern in sensitive_patterns)

    def _validate_api_key(self, key: str, value: str) -> Dict[str, Any]:
        """验证API密钥格式"""
        if not value:
            return {"valid": False, "message": "未配置", "level": "warning"}
        
        # 基于不同提供商的格式验证
        if key == "OPENAI_API_KEY":
            if re.match(r'^sk-[a-zA-Z0-9]{48}$', value):
                return {"valid": True, "message": "格式正确", "level": "success"}
            else:
                return {"valid": False, "message": "格式不正确，应为sk-开头的48字符", "level": "error"}
        
        elif key == "GOOGLE_API_KEY":
            if re.match(r'^[a-zA-Z0-9_-]{39}$', value):
                return {"valid": True, "message": "格式正确", "level": "success"}
            else:
                return {"valid": False, "message": "格式不正确，应为39字符的字母数字组合", "level": "error"}
        
        elif key == "DASHSCOPE_API_KEY":
            if re.match(r'^sk-[a-zA-Z0-9]{24,32}$', value):
                return {"valid": True, "message": "格式正确", "level": "success"}
            else:
                return {"valid": False, "message": "格式不正确，应为sk-开头", "level": "error"}
        
        elif key == "DEEPSEEK_API_KEY":
            if re.match(r'^sk-[a-zA-Z0-9]{48}$', value):
                return {"valid": True, "message": "格式正确", "level": "success"}
            else:
                return {"valid": False, "message": "格式不正确，应为sk-开头的48字符", "level": "error"}
        
        elif key in ["VOLCENGINE_API_KEY", "CUSTOM_OPENAI_API_KEY", "OPENROUTER_API_KEY"]:
            if len(value) >= 20:
                return {"valid": True, "message": "格式可能正确", "level": "success"}
            else:
                return {"valid": False, "message": "密钥长度过短", "level": "warning"}
        
        elif key in ["FINNHUB_API_KEY", "TUSHARE_TOKEN"]:
            if len(value) >= 10:
                return {"valid": True, "message": "格式可能正确", "level": "success"}
            else:
                return {"valid": False, "message": "Token长度过短", "level": "warning"}
        
        else:
            # 通用验证
            if len(value) >= 10:
                return {"valid": True, "message": "已配置", "level": "success"}
            else:
                return {"valid": False, "message": "配置值过短", "level": "warning"}

    def _validate_database_config(self, key: str, value: str) -> Dict[str, Any]:
        """验证数据库配置"""
        if not value:
            return {"valid": False, "message": "未配置", "level": "warning"}
        
        if key == "TRADINGAGENTS_MONGODB_URL":
            if value.startswith("mongodb://"):
                return {"valid": True, "message": "MongoDB URL格式正确", "level": "success"}
            else:
                return {"valid": False, "message": "应以mongodb://开头", "level": "error"}
        
        elif key == "TRADINGAGENTS_REDIS_URL":
            if value.startswith("redis://"):
                return {"valid": True, "message": "Redis URL格式正确", "level": "success"}
            else:
                return {"valid": False, "message": "应以redis://开头", "level": "error"}
        
        elif key == "TRADINGAGENTS_CACHE_TYPE":
            if value.lower() in ["redis", "memory", "none"]:
                return {"valid": True, "message": f"缓存类型: {value}", "level": "success"}
            else:
                return {"valid": False, "message": "应为redis/memory/none之一", "level": "error"}
        
        return {"valid": True, "message": "已配置", "level": "success"}

    def _validate_system_config(self, key: str, value: str) -> Dict[str, Any]:
        """验证系统配置"""
        if key == "MEMORY_ENABLED":
            if value.lower() in ["true", "false", "1", "0", ""]:
                return {"valid": True, "message": f"内存功能: {'启用' if value.lower() in ['true', '1'] else '禁用'}", "level": "success"}
            else:
                return {"valid": False, "message": "应为true/false", "level": "error"}
        
        elif key == "TRADINGAGENTS_LOG_LEVEL":
            if value.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", ""]:
                return {"valid": True, "message": f"日志级别: {value or 'INFO'}", "level": "success"}
            else:
                return {"valid": False, "message": "应为DEBUG/INFO/WARNING/ERROR", "level": "error"}
        
        elif key in ["TRADINGAGENTS_LOG_DIR", "TRADINGAGENTS_RESULTS_DIR"]:
            if value:
                path = Path(value)
                try:
                    # 检查路径是否可写
                    if path.exists() or path.parent.exists():
                        return {"valid": True, "message": f"路径: {value}", "level": "success"}
                    else:
                        return {"valid": False, "message": "路径不存在", "level": "warning"}
                except:
                    return {"valid": False, "message": "路径格式无效", "level": "error"}
            else:
                return {"valid": True, "message": "使用默认路径", "level": "success"}
        
        return {"valid": True, "message": "已配置" if value else "使用默认值", "level": "success"}

    def _run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行综合配置验证"""
        try:
            results = {
                "overall_status": "unknown",
                "critical_issues": [],
                "warnings": [],
                "recommendations": []
            }
            
            # 检查关键API密钥
            critical_keys = ["DASHSCOPE_API_KEY", "FINNHUB_API_KEY"]
            missing_critical = []
            
            for key in critical_keys:
                if not os.getenv(key):
                    missing_critical.append(key)
                    results["critical_issues"].append(f"缺少必需的API密钥: {key}")
            
            # 检查数据库配置
            mongodb_url = os.getenv("TRADINGAGENTS_MONGODB_URL", "")
            redis_url = os.getenv("TRADINGAGENTS_REDIS_URL", "")
            
            if not mongodb_url and not redis_url:
                results["warnings"].append("未配置数据库，将使用本地存储")
            
            # 检查内存功能
            memory_enabled = os.getenv("MEMORY_ENABLED", "true").lower()
            if memory_enabled == "false":
                results["warnings"].append("内存功能已禁用")
            
            # 提供配置建议
            if not os.getenv("TUSHARE_TOKEN"):
                results["recommendations"].append("配置TUSHARE_TOKEN以获得更准确的A股数据")
            
            if not os.getenv("GOOGLE_API_KEY"):
                results["recommendations"].append("配置GOOGLE_API_KEY以使用Google AI模型")
            
            # 确定整体状态
            if results["critical_issues"]:
                results["overall_status"] = "critical"
            elif results["warnings"]:
                results["overall_status"] = "warning"  
            else:
                results["overall_status"] = "healthy"
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 综合验证失败: {e}")
            return {
                "overall_status": "error",
                "critical_issues": [f"验证过程出错: {str(e)}"],
                "warnings": [],
                "recommendations": []
            }

    def validate_specific_config(self, key: str, value: str) -> Dict[str, Any]:
        """验证特定配置项"""
        if key in self.important_keys:
            return self._validate_api_key(key, value)
        elif key in self.database_keys:
            return self._validate_database_config(key, value)
        elif key in self.system_keys:
            return self._validate_system_config(key, value)
        else:
            return {"valid": True, "message": "已配置" if value else "未配置", "level": "info"}

# 创建全局实例
config_reloader = ConfigReloader()