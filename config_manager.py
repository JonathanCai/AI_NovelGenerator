# config_manager.py
# -*- coding: utf-8 -*-
import json
import os
import threading
import logging
from typing import Dict, Any
from llm_adapters import create_llm_adapter
from embedding_adapters import create_embedding_adapter


def validate_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """验证并修正配置数据的完整性"""
    if not isinstance(config_data, dict):
        return create_default_config_dict()

    # 必需的顶级键
    required_keys = [
        "last_interface_format", "last_embedding_interface_format",
        "llm_configs", "embedding_configs", "other_params",
        "choose_configs", "proxy_setting", "webdav_config"
    ]

    # 创建默认配置结构
    default_config = create_default_config_dict()

    # 合并配置，确保所有必需键都存在
    for key in required_keys:
        if key not in config_data:
            config_data[key] = default_config[key]

    # 验证和修正具体配置项
    _validate_llm_configs(config_data.get("llm_configs", {}))
    _validate_embedding_configs(config_data.get("embedding_configs", {}))
    _validate_other_params(config_data.get("other_params", {}))
    _validate_choose_configs(config_data.get("choose_configs", {}))
    _validate_proxy_setting(config_data.get("proxy_setting", {}))

    return config_data


def create_default_config_dict() -> Dict[str, Any]:
    """创建默认配置字典"""
    return {
        "last_interface_format": "OpenAI",
        "last_embedding_interface_format": "OpenAI",
        "llm_configs": {
            "DeepSeek V3": {
                "api_key": "",
                "base_url": "https://api.deepseek.com/v1",
                "model_name": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 8192,
                "timeout": 600,
                "interface_format": "OpenAI"
            }
        },
        "embedding_configs": {
            "OpenAI": {
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model_name": "text-embedding-ada-002",
                "retrieval_k": 4,
                "interface_format": "OpenAI"
            }
        },
        "other_params": {
            "topic": "",
            "genre": "",
            "num_chapters": 0,
            "word_number": 0,
            "filepath": "",
            "chapter_num": "120",
            "user_guidance": "",
            "characters_involved": "",
            "key_items": "",
            "scene_location": "",
            "time_constraint": ""
        },
        "choose_configs": {
            "prompt_draft_llm": "DeepSeek V3",
            "chapter_outline_llm": "DeepSeek V3",
            "architecture_llm": "DeepSeek V3",
            "final_chapter_llm": "DeepSeek V3",
            "consistency_review_llm": "DeepSeek V3"
        },
        "proxy_setting": {
            "proxy_url": "127.0.0.1",
            "proxy_port": "",
            "enabled": False
        },
        "webdav_config": {
            "webdav_url": "",
            "webdav_username": "",
            "webdav_password": ""
        }
    }


def _validate_llm_configs(llm_configs: Dict[str, Any]) -> None:
    """验证LLM配置"""
    if not isinstance(llm_configs, dict):
        return

    for name, config in llm_configs.items():
        if not isinstance(config, dict):
            continue

        # 确保必需字段存在
        required_fields = ["api_key", "base_url", "model_name", "temperature", "max_tokens", "timeout", "interface_format"]
        for field in required_fields:
            if field not in config:
                # 设置默认值
                if field == "temperature":
                    config[field] = 0.7
                elif field == "max_tokens":
                    config[field] = 4096
                elif field == "timeout":
                    config[field] = 600
                elif field == "interface_format":
                    config[field] = "OpenAI"
                else:
                    config[field] = ""

        # 验证数值范围
        config["temperature"] = max(0.0, min(2.0, float(config.get("temperature", 0.7))))
        config["max_tokens"] = max(1, min(32768, int(config.get("max_tokens", 4096))))
        config["timeout"] = max(10, min(3600, int(config.get("timeout", 600))))


def _validate_embedding_configs(embedding_configs: Dict[str, Any]) -> None:
    """验证Embedding配置"""
    if not isinstance(embedding_configs, dict):
        return

    for name, config in embedding_configs.items():
        if not isinstance(config, dict):
            continue

        required_fields = ["api_key", "base_url", "model_name", "retrieval_k", "interface_format"]
        for field in required_fields:
            if field not in config:
                if field == "retrieval_k":
                    config[field] = 4
                elif field == "interface_format":
                    config[field] = "OpenAI"
                else:
                    config[field] = ""

        config["retrieval_k"] = max(1, min(20, int(config.get("retrieval_k", 4))))


def _validate_other_params(other_params: Dict[str, Any]) -> None:
    """验证其他参数"""
    if not isinstance(other_params, dict):
        return

    # 确保所有必需字段存在
    required_fields = ["topic", "genre", "num_chapters", "word_number", "filepath",
                      "chapter_num", "user_guidance", "characters_involved",
                      "key_items", "scene_location", "time_constraint"]

    for field in required_fields:
        if field not in other_params:
            other_params[field] = ""

    # 验证数值类型
    other_params["num_chapters"] = max(1, min(1000, int(other_params.get("num_chapters", 0))))
    other_params["word_number"] = max(100, min(50000, int(other_params.get("word_number", 0))))


def _validate_choose_configs(choose_configs: Dict[str, Any]) -> None:
    """验证选择配置"""
    if not isinstance(choose_configs, dict):
        return

    # 确保所有必需字段存在
    required_configs = ["prompt_draft_llm", "chapter_outline_llm", "architecture_llm",
                       "final_chapter_llm", "consistency_review_llm"]

    for config_name in required_configs:
        if config_name not in choose_configs:
            choose_configs[config_name] = "DeepSeek V3"


def _validate_proxy_setting(proxy_setting: Dict[str, Any]) -> None:
    """验证代理设置"""
    if not isinstance(proxy_setting, dict):
        return

    required_fields = ["proxy_url", "proxy_port", "enabled"]
    for field in required_fields:
        if field not in proxy_setting:
            if field == "enabled":
                proxy_setting[field] = False
            else:
                proxy_setting[field] = ""

    # 验证代理端口
    try:
        port = int(proxy_setting.get("proxy_port", 0))
        if port < 1 or port > 65535:
            proxy_setting["proxy_port"] = ""
    except (ValueError, TypeError):
        proxy_setting["proxy_port"] = ""


def load_config(config_file: str) -> dict:
    """从指定的 config_file 加载配置，若不存在则创建一个默认配置文件。"""
    config_lock = threading.Lock()

    with config_lock:
        # PenBo 修改代码，增加配置文件不存在则创建一个默认配置文件
        if not os.path.exists(config_file):
            create_config(config_file)

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 验证配置文件完整性
                return validate_config(config_data)
        except json.JSONDecodeError as e:
            print(f"配置文件JSON格式错误: {e}")
            return create_config(config_file)
        except IOError as e:
            print(f"配置文件读取错误: {e}")
            return create_config(config_file)
        except Exception as e:
            print(f"配置文件加载时发生未知错误: {e}")
            return create_config(config_file)


def create_config(config_file: str) -> dict:
    """创建默认配置文件"""
    config = create_default_config_dict()
    save_config(config, config_file)
    return config



def save_config(config_data: dict, config_file: str) -> bool:
    """将 config_data 保存到 config_file 中，返回 True/False 表示是否成功。"""
    config_lock = threading.Lock()

    with config_lock:
        try:
            # 验证配置数据完整性
            config_data = validate_config(config_data)

            # 创建备份文件
            backup_file = config_file + '.backup'
            if os.path.exists(config_file):
                import shutil
                shutil.copy2(config_file, backup_file)

            # 原子性写入：先写入临时文件，再重命名
            temp_file = config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)

            # 原子性重命名
            if os.name == 'nt':  # Windows
                if os.path.exists(config_file):
                    os.remove(config_file)
            os.rename(temp_file, config_file)

            return True
        except (IOError, OSError) as e:
            print(f"配置文件保存错误: {e}")
            return False
        except Exception as e:
            print(f"配置文件保存时发生未知错误: {e}")
            return False

def test_llm_config(interface_format, api_key, base_url, model_name, temperature, max_tokens, timeout, log_func, handle_exception_func):
    """测试当前的LLM配置是否可用"""
    def task():
        try:
            log_func("开始测试LLM配置...")
            llm_adapter = create_llm_adapter(
                interface_format=interface_format,
                base_url=base_url,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            test_prompt = "Please reply 'OK'"
            response = llm_adapter.invoke(test_prompt)
            if response:
                log_func("✅ LLM配置测试成功！")
                log_func(f"测试回复: {response}")
            else:
                log_func("❌ LLM配置测试失败：未获取到响应")
        except Exception as e:
            log_func(f"❌ LLM配置测试出错: {str(e)}")
            handle_exception_func("测试LLM配置时出错")

    threading.Thread(target=task, daemon=True).start()

def test_embedding_config(api_key, base_url, interface_format, model_name, log_func, handle_exception_func):
    """测试当前的Embedding配置是否可用"""
    def task():
        try:
            log_func("开始测试Embedding配置...")
            embedding_adapter = create_embedding_adapter(
                interface_format=interface_format,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )

            test_text = "测试文本"
            embeddings = embedding_adapter.embed_query(test_text)
            if embeddings and len(embeddings) > 0:
                log_func("✅ Embedding配置测试成功！")
                log_func(f"生成的向量维度: {len(embeddings)}")
            else:
                log_func("❌ Embedding配置测试失败：未获取到向量")
        except Exception as e:
            log_func(f"❌ Embedding配置测试出错: {str(e)}")
            handle_exception_func("测试Embedding配置时出错")

    threading.Thread(target=task, daemon=True).start()