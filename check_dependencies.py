#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查项目依赖是否已安装
"""

import sys
import subprocess
import importlib

def check_package(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name

    try:
        importlib.import_module(import_name)
        return True, "已安装"
    except ImportError:
        return False, "未安装"

def main():
    """主函数"""
    print("🔍 检查AI小说生成器依赖包...")
    print("=" * 60)

    # 核心依赖
    dependencies = [
        ("customtkinter", "customtkinter", "GUI框架"),
        ("langchain-openai", "langchain_openai", "OpenAI集成"),
        ("langchain", "langchain", "LangChain核心"),
        ("chromadb", "chromadb", "向量数据库"),
        ("langchain-chroma", "langchain_chroma", "Chroma集成"),
        ("openai", "openai", "OpenAI客户端"),
        ("google-generativeai", "google.generativeai", "Gemini集成"),
        ("requests", "requests", "HTTP请求"),
        ("nltk", "nltk", "自然语言处理"),
        ("numpy", "numpy", "数值计算"),
        ("tiktoken", "tiktoken", "Token计算"),
    ]

    # 可选依赖
    optional_dependencies = [
        ("azure-ai-inference", "azure.ai.inference", "Azure AI服务"),
        ("sentence-transformers", "sentence_transformers", "句子嵌入"),
        ("scikit-learn", "sklearn", "机器学习"),
    ]

    missing_required = []
    missing_optional = []

    print("📦 必需依赖:")
    all_required_ok = True
    for package, import_name, description in dependencies:
        is_installed, status = check_package(package, import_name)
        status_icon = "✅" if is_installed else "❌"
        print(f"  {status_icon} {package} ({description}) - {status}")
        if not is_installed:
            all_required_ok = False
            missing_required.append(package)

    print("\n📦 可选依赖:")
    for package, import_name, description in optional_dependencies:
        is_installed, status = check_package(package, import_name)
        status_icon = "✅" if is_installed else "⚠️"
        print(f"  {status_icon} {package} ({description}) - {status}")
        if not is_installed:
            missing_optional.append(package)

    print("\n" + "=" * 60)

    if all_required_ok:
        print("✅ 所有必需依赖都已安装！")
        print("🚀 可以运行 python main.py 启动程序")

        if missing_optional:
            print(f"\n💡 提示: 以下可选依赖未安装，某些功能可能不可用:")
            for package in missing_optional:
                print(f"   - {package}")

    else:
        print("❌ 检测到缺失的必需依赖！")
        print("\n🔧 安装方法:")
        print("   方法1: 安装所有依赖（推荐）")
        print("   pip install -r requirements.txt")
        print("\n   方法2: 只安装缺失的依赖")
        for package in missing_required:
            print(f"   pip install {package}")

        print(f"\n⚠️  请先安装缺失的依赖，然后再运行程序")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())