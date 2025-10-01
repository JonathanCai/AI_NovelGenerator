# ui/font_config.py
# -*- coding: utf-8 -*-
"""
UI字体配置统一管理模块
用于统一管理整个应用程序的字体大小设置，确保UI界面的字体一致性
"""

# 默认字体族
DEFAULT_FONT_FAMILY = "Microsoft YaHei"

# 字体大小配置
class FontSizes:
    """字体大小配置类"""
    # 基础字体大小（原12号）
    DEFAULT = 14  # 从12增加到14，提升可读性

    # 小字体（原10号）
    SMALL = 12    # 从10增加到12

    # 大字体（原14号）
    LARGE = 16    # 从14增加到16

    # 特大字体（原16号）
    EXTRA_LARGE = 18  # 从16增加到18

    # 按钮字体
    BUTTON = DEFAULT

    # 输入框字体
    ENTRY = DEFAULT

    # 文本框字体
    TEXTBOX = DEFAULT

    # 标签字体
    LABEL = DEFAULT

    # 标题字体
    TITLE = EXTRA_LARGE

    # 日志字体（等宽字体更合适）
    LOG = ("Consolas", DEFAULT)

# 字体样式配置
class Fonts:
    """字体样式配置类"""

    # 基础字体
    DEFAULT = (DEFAULT_FONT_FAMILY, FontSizes.DEFAULT)

    # 小字体
    SMALL = (DEFAULT_FONT_FAMILY, FontSizes.SMALL)

    # 大字体
    LARGE = (DEFAULT_FONT_FAMILY, FontSizes.LARGE)

    # 特大字体
    EXTRA_LARGE = (DEFAULT_FONT_FAMILY, FontSizes.EXTRA_LARGE)

    # 粗体字体
    BOLD = (DEFAULT_FONT_FAMILY, FontSizes.DEFAULT, "bold")

    # 大粗体
    LARGE_BOLD = (DEFAULT_FONT_FAMILY, FontSizes.LARGE, "bold")

    # 特大粗体
    EXTRA_LARGE_BOLD = (DEFAULT_FONT_FAMILY, FontSizes.EXTRA_LARGE, "bold")

    # 按钮字体
    BUTTON = (DEFAULT_FONT_FAMILY, FontSizes.BUTTON)

    # 输入框字体
    ENTRY = (DEFAULT_FONT_FAMILY, FontSizes.ENTRY)

    # 文本框字体
    TEXTBOX = (DEFAULT_FONT_FAMILY, FontSizes.TEXTBOX)

    # 标签字体
    LABEL = (DEFAULT_FONT_FAMILY, FontSizes.LABEL)

    # 标题字体
    TITLE = (DEFAULT_FONT_FAMILY, FontSizes.TITLE, "bold")

    # 日志字体（等宽字体）
    LOG = FontSizes.LOG

def get_font(font_type: str = "default", **kwargs):
    """
    获取指定类型的字体

    Args:
        font_type (str): 字体类型，可选值：default, small, large, extra_large,
                        bold, large_bold, extra_large_bold, button, entry,
                        textbox, label, title, log
        **kwargs: 额外的字体参数，如 size, weight 等

    Returns:
        tuple: 字体配置元组
    """
    font_map = {
        "default": Fonts.DEFAULT,
        "small": Fonts.SMALL,
        "large": Fonts.LARGE,
        "extra_large": Fonts.EXTRA_LARGE,
        "bold": Fonts.BOLD,
        "large_bold": Fonts.LARGE_BOLD,
        "extra_large_bold": Fonts.EXTRA_LARGE_BOLD,
        "button": Fonts.BUTTON,
        "entry": Fonts.ENTRY,
        "textbox": Fonts.TEXTBOX,
        "label": Fonts.LABEL,
        "title": Fonts.TITLE,
        "log": Fonts.LOG,
    }

    base_font = font_map.get(font_type, Fonts.DEFAULT)

    # 如果提供了额外的参数，需要修改字体配置
    if kwargs:
        font_list = list(base_font)
        if "size" in kwargs:
            font_list[1] = kwargs["size"]
        if "weight" in kwargs:
            if len(font_list) == 2:
                font_list.append(kwargs["weight"])
            else:
                font_list[2] = kwargs["weight"]
        return tuple(font_list)

    return base_font

def configure_customtkinter_fonts():
    """配置CustomTkinter的默认字体"""
    import customtkinter as ctk

    # 设置CustomTkinter的默认字体
    try:
        ctk.set_appearance_mode("System")  # 确保在设置字体前设置外观模式

        # 可以在这里添加更多的CustomTkinter字体配置
        # 目前CustomTkinter没有直接的API来全局设置字体
        # 我们需要在创建组件时手动指定字体
        pass
    except Exception as e:
        import logging
        logging.warning(f"配置CustomTkinter字体时出现警告: {e}")

# 为了向后兼容，保留一些常用的字体常量
DEFAULT_FONT = Fonts.DEFAULT
SMALL_FONT = Fonts.SMALL
LARGE_FONT = Fonts.LARGE
BOLD_FONT = Fonts.BOLD
TITLE_FONT = Fonts.TITLE
BUTTON_FONT = Fonts.BUTTON
ENTRY_FONT = Fonts.ENTRY
TEXTBOX_FONT = Fonts.TEXTBOX
LABEL_FONT = Fonts.LABEL
LOG_FONT = Fonts.LOG