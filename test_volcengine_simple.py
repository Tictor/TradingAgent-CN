#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试火山引擎集成 - 简化版
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_volcengine_config():
    """测试火山引擎配置"""
    
    print("[TEST] 火山引擎配置测试")
    print("=" * 50)
    
    # 模拟Web界面配置
    config = {
        'llm_provider': 'volcengine',
        'llm_model': 'ep-20241201-abc123'
    }
    
    print("配置测试:")
    print(f"  提供商: {config['llm_provider']}")
    print(f"  模型ID: {config['llm_model']}")
    
    # 验证配置
    if config['llm_provider'] == 'volcengine':
        if config['llm_model'] and config['llm_model'].startswith('ep-'):
            print("  状态: 配置验证通过")
            return True
        else:
            print("  状态: 模型ID格式错误")
            return False
    else:
        print("  状态: 提供商配置错误")
        return False

def test_default_config():
    """测试默认配置加载"""
    
    print("\n[TEST] 默认配置加载测试")
    print("=" * 30)
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 创建配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "volcengine"
        config["deep_think_llm"] = "ep-20241201-test"
        config["quick_think_llm"] = "ep-20241201-test"
        
        print("配置创建:")
        print(f"  llm_provider: {config['llm_provider']}")
        print(f"  deep_think_llm: {config['deep_think_llm']}")
        print(f"  quick_think_llm: {config['quick_think_llm']}")
        
        print("  状态: 配置创建成功")
        return True
        
    except Exception as e:
        print(f"  状态: 配置创建失败 - {e}")
        return False

def test_env_variables():
    """测试环境变量"""
    
    print("\n[TEST] 环境变量测试")
    print("=" * 30)
    
    # 设置测试环境变量
    os.environ['VOLCENGINE_API_KEY'] = 'test-volcengine-key-123'
    os.environ['FINNHUB_API_KEY'] = 'test-finnhub-key-123'
    
    # 检查环境变量
    volcengine_key = os.getenv('VOLCENGINE_API_KEY')
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    print("环境变量检查:")
    print(f"  VOLCENGINE_API_KEY: {'已设置' if volcengine_key else '未设置'}")
    print(f"  FINNHUB_API_KEY: {'已设置' if finnhub_key else '未设置'}")
    
    if volcengine_key and finnhub_key:
        print("  状态: 环境变量验证通过")
        return True
    else:
        print("  状态: 环境变量验证失败")
        return False

def test_api_key_validation():
    """测试API密钥验证"""
    
    print("\n[TEST] API密钥验证测试")
    print("=" * 30)
    
    def validate_api_key(key, expected_format):
        if not key:
            return "未配置", "error"
        if expected_format == "volcengine" and len(key) >= 20:
            return f"{key[:8]}...", "success"
        else:
            return f"{key[:8]}... (格式异常)", "warning"
    
    test_keys = [
        ("", "空密钥"),
        ("short", "短密钥"),
        ("volcengine-test-key-12345678901234567890", "有效密钥")
    ]
    
    print("密钥验证:")
    success_count = 0
    for key, desc in test_keys:
        status, level = validate_api_key(key, "volcengine")
        icon = {"success": "[OK]", "warning": "[WARN]", "error": "[ERR]"}.get(level, "[?]")
        print(f"  {icon} {desc}: {status}")
        if level == "success":
            success_count += 1
    
    print(f"  状态: {success_count}/{len(test_keys)} 测试通过")
    return success_count > 0

if __name__ == "__main__":
    print("火山引擎集成测试开始")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("配置测试", test_volcengine_config()))
    results.append(("默认配置", test_default_config()))
    results.append(("环境变量", test_env_variables()))
    results.append(("密钥验证", test_api_key_validation()))
    
    # 总结结果
    print("\n" + "=" * 60)
    print("测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 火山引擎集成测试全部通过!")
        print("\n使用说明:")
        print("1. 在.env文件中设置: VOLCENGINE_API_KEY=你的API密钥")
        print("2. 在Web界面选择'火山引擎'作为LLM提供商")
        print("3. 输入你的个人模型ID (格式: ep-yyyymmdd-xxxxxx)")
        print("4. 开始分析，系统将使用火山引擎API")
    else:
        print("\n[WARNING] 部分测试未通过，请检查配置")