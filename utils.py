# utils.py
# -*- coding: utf-8 -*-
import os
import json
import logging
import tempfile
from pathlib import Path

def read_file(filename: str) -> str:
    """安全地读取文件的全部内容，带有完善的错误处理。"""
    if not filename or not isinstance(filename, str):
        logging.error("read_file: filename 必须是非空字符串")
        return ""

    try:
        # 检查文件是否存在
        file_path = Path(filename)
        if not file_path.exists():
            logging.warning(f"文件不存在: {filename}")
            return ""

        # 检查文件是否可读
        if not os.access(filename, os.R_OK):
            logging.error(f"文件不可读: {filename}")
            return ""

        # 检查文件大小，避免读取过大的文件
        file_size = file_path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB限制
            logging.error(f"文件过大 ({file_size} bytes)，拒绝读取: {filename}")
            return ""

        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return content

    except UnicodeDecodeError as e:
        logging.error(f"文件编码错误，尝试其他编码: {e}")
        # 尝试其他编码
        for encoding in ['utf-8-sig', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    content = file.read()
                logging.info(f"使用 {encoding} 编码成功读取文件: {filename}")
                return content
            except UnicodeDecodeError:
                continue
        logging.error(f"无法使用任何编码读取文件: {filename}")
        return ""

    except PermissionError as e:
        logging.error(f"权限不足，无法读取文件: {filename}, 错误: {e}")
        return ""

    except IOError as e:
        logging.error(f"IO错误，无法读取文件: {filename}, 错误: {e}")
        return ""

    except Exception as e:
        logging.error(f"[read_file] 读取文件时发生未知错误: {filename}, 错误: {e}")
        return ""

def append_text_to_file(text_to_append: str, file_path: str):
    """在文件末尾追加文本(带换行)。若文本非空且无换行，则自动加换行。"""
    if text_to_append and not text_to_append.startswith('\n'):
        text_to_append = '\n' + text_to_append

    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(text_to_append)
    except IOError as e:
        print(f"[append_text_to_file] 发生错误：{e}")

def clear_file_content(filename: str):
    """清空指定文件内容。"""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            pass
    except IOError as e:
        print(f"[clear_file_content] 无法清空文件 '{filename}' 的内容：{e}")

def save_string_to_txt(content: str, filename: str) -> bool:
    """安全地将字符串保存为 txt 文件（覆盖写）。"""
    if not isinstance(content, str):
        logging.error("save_string_to_txt: content 必须是字符串")
        return False

    if not filename or not isinstance(filename, str):
        logging.error("save_string_to_txt: filename 必须是非空字符串")
        return False

    try:
        # 确保目录存在
        file_path = Path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用原子性写入：先写临时文件，再重命名
        temp_file = file_path.with_suffix(file_path.suffix + '.tmp')

        with open(temp_file, 'w', encoding='utf-8') as file:
            file.write(content)

        # 原子性重命名
        if os.name == 'nt':  # Windows
            if file_path.exists():
                os.remove(file_path)
        temp_file.rename(file_path)

        logging.debug(f"成功保存文件: {filename}")
        return True

    except PermissionError as e:
        logging.error(f"权限不足，无法保存文件: {filename}, 错误: {e}")
        return False

    except IOError as e:
        logging.error(f"IO错误，无法保存文件: {filename}, 错误: {e}")
        # 尝试清理临时文件
        try:
            if 'temp_file' in locals() and temp_file.exists():
                temp_file.unlink()
        except:
            pass
        return False

    except Exception as e:
        logging.error(f"[save_string_to_txt] 保存文件时发生未知错误: {filename}, 错误: {e}")
        # 尝试清理临时文件
        try:
            if 'temp_file' in locals() and temp_file.exists():
                temp_file.unlink()
        except:
            pass
        return False

def save_data_to_json(data: dict, file_path: str) -> bool:
    """安全地将数据保存到 JSON 文件。"""
    if not isinstance(data, (dict, list)):
        logging.error("save_data_to_json: data 必须是字典或列表")
        return False

    if not file_path or not isinstance(file_path, str):
        logging.error("save_data_to_json: file_path 必须是非空字符串")
        return False

    try:
        # 确保目录存在
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # 验证数据是否可以JSON序列化
        json.dumps(data)  # 测试序列化

        # 使用原子性写入
        temp_file = path.with_suffix(path.suffix + '.tmp')
        with open(temp_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        # 原子性重命名
        if os.name == 'nt':  # Windows
            if path.exists():
                os.remove(path)
        temp_file.rename(path)

        logging.debug(f"成功保存JSON文件: {file_path}")
        return True

    except (TypeError, ValueError) as e:
        logging.error(f"数据无法JSON序列化: {e}")
        return False

    except PermissionError as e:
        logging.error(f"权限不足，无法保存JSON文件: {file_path}, 错误: {e}")
        return False

    except IOError as e:
        logging.error(f"IO错误，无法保存JSON文件: {file_path}, 错误: {e}")
        # 尝试清理临时文件
        try:
            if 'temp_file' in locals() and temp_file.exists():
                temp_file.unlink()
        except:
            pass
        return False

    except Exception as e:
        logging.error(f"[save_data_to_json] 保存JSON文件时发生未知错误: {file_path}, 错误: {e}")
        # 尝试清理临时文件
        try:
            if 'temp_file' in locals() and temp_file.exists():
                temp_file.unlink()
        except:
            pass
        return False


def create_directory_safely(directory: str) -> bool:
    """安全地创建目录"""
    if not directory or not isinstance(directory, str):
        logging.error("create_directory_safely: directory 必须是非空字符串")
        return False

    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        logging.debug(f"成功创建目录: {directory}")
        return True
    except PermissionError as e:
        logging.error(f"权限不足，无法创建目录: {directory}, 错误: {e}")
        return False
    except Exception as e:
        logging.error(f"创建目录时发生未知错误: {directory}, 错误: {e}")
        return False


def backup_file(file_path: str, backup_suffix: str = '.backup') -> bool:
    """创建文件备份"""
    if not file_path or not isinstance(file_path, str):
        logging.error("backup_file: file_path 必须是非空字符串")
        return False

    try:
        path = Path(file_path)
        if not path.exists():
            logging.warning(f"要备份的文件不存在: {file_path}")
            return False

        backup_path = path.with_suffix(path.suffix + backup_suffix)
        if backup_path.exists():
            # 如果备份文件已存在，添加时间戳
            import time
            timestamp = int(time.time())
            backup_path = path.with_suffix(f"{path.suffix}.{timestamp}.backup")

        import shutil
        shutil.copy2(file_path, backup_path)
        logging.info(f"文件备份成功: {file_path} -> {backup_path}")
        return True

    except Exception as e:
        logging.error(f"创建文件备份失败: {file_path}, 错误: {e}")
        return False
