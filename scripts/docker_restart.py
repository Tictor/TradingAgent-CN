#!/usr/bin/env python3
"""
Docker服务重启脚本
用于.env文件修改后快速重启Docker服务
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, description):
    """运行系统命令"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True, encoding='utf-8')
        print(f"✅ {description}成功")
        if result.stdout:
            print(f"输出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败")
        if e.stderr:
            print(f"错误: {e.stderr.strip()}")
        return False

def main():
    """主函数"""
    print("🐳 TradingAgents-CN Docker 服务重启工具")
    print("=" * 50)
    
    # 检查当前目录是否包含docker-compose.yml
    project_root = Path(__file__).parent.parent
    compose_file = project_root / "docker-compose.yml"
    
    if not compose_file.exists():
        print(f"❌ 未找到docker-compose.yml文件: {compose_file}")
        return False
    
    print(f"📁 项目目录: {project_root}")
    
    # 切换到项目目录
    os.chdir(project_root)
    
    # 获取用户选择
    print("\n请选择重启选项:")
    print("1. 仅重启web服务 (推荐用于.env文件修改)")
    print("2. 重启所有服务")
    print("3. 完全重新构建并启动")
    print("4. 查看服务状态")
    print("5. 查看服务日志")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice == "1":
        # 仅重启web服务
        print("\n🔄 重启web服务...")
        success = run_command("docker-compose restart web", "重启web服务")
        
        if success:
            print("\n⏱️ 等待服务启动...")
            time.sleep(5)
            run_command("docker-compose ps web", "检查web服务状态")
            print("\n🌐 Web服务应该在 http://localhost:8501 可用")
            print("💡 如果修改了.env文件，新配置现在应该已生效")
    
    elif choice == "2":
        # 重启所有服务
        print("\n🔄 重启所有服务...")
        success = run_command("docker-compose restart", "重启所有服务")
        
        if success:
            print("\n⏱️ 等待服务启动...")
            time.sleep(10)
            run_command("docker-compose ps", "检查所有服务状态")
    
    elif choice == "3":
        # 完全重新构建
        print("\n🔧 停止所有服务...")
        run_command("docker-compose down", "停止服务")
        
        print("\n🏗️ 重新构建并启动...")
        success = run_command("docker-compose up -d --build", "重新构建并启动")
        
        if success:
            print("\n⏱️ 等待服务启动...")
            time.sleep(15)
            run_command("docker-compose ps", "检查所有服务状态")
    
    elif choice == "4":
        # 查看服务状态
        print("\n📊 当前服务状态:")
        run_command("docker-compose ps", "获取服务状态")
        
        print("\n🔍 详细容器信息:")
        run_command("docker ps --filter name=TradingAgents", "获取容器信息")
    
    elif choice == "5":
        # 查看服务日志
        print("\n📋 最近的服务日志:")
        
        service = input("请输入服务名 (web/mongodb/redis，回车查看web日志): ").strip()
        if not service:
            service = "web"
        
        run_command(f"docker-compose logs --tail=50 {service}", f"获取{service}服务日志")
    
    else:
        print("❌ 无效选项")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 操作完成！")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 操作已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)