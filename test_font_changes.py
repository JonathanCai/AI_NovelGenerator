#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字体修改效果测试程序
用于验证UI字体修改后的显示效果
"""

import customtkinter as ctk
from ui.font_config import configure_customtkinter_fonts, get_font

class FontTestApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("字体修改效果测试")
        self.root.geometry("800x600")

        # 配置字体设置
        configure_customtkinter_fonts()

        self.setup_ui()

    def setup_ui(self):
        """设置测试界面"""
        # 主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="字体修改效果测试",
            font=get_font("title")
        )
        title_label.pack(pady=(10, 30))

        # 不同字体的对比展示
        test_frame = ctk.CTkFrame(main_frame)
        test_frame.pack(fill="both", expand=True, pady=10)

        # 小字体
        small_label = ctk.CTkLabel(
            test_frame,
            text="这是小字体 (Small Font) - 12号",
            font=get_font("small")
        )
        small_label.pack(anchor="w", padx=20, pady=5)

        # 默认字体
        default_label = ctk.CTkLabel(
            test_frame,
            text="这是默认字体 (Default Font) - 14号",
            font=get_font("default")
        )
        default_label.pack(anchor="w", padx=20, pady=5)

        # 大字体
        large_label = ctk.CTkLabel(
            test_frame,
            text="这是大字体 (Large Font) - 16号",
            font=get_font("large")
        )
        large_label.pack(anchor="w", padx=20, pady=5)

        # 特大字体
        extra_large_label = ctk.CTkLabel(
            test_frame,
            text="这是特大字体 (Extra Large Font) - 18号",
            font=get_font("extra_large")
        )
        extra_large_label.pack(anchor="w", padx=20, pady=5)

        # 粗体字体
        bold_label = ctk.CTkLabel(
            test_frame,
            text="这是粗体字体 (Bold Font) - 14号",
            font=get_font("bold")
        )
        bold_label.pack(anchor="w", padx=20, pady=5)

        # 按钮字体
        button_frame = ctk.CTkFrame(test_frame)
        button_frame.pack(fill="x", padx=20, pady=20)

        button1 = ctk.CTkButton(
            button_frame,
            text="按钮字体测试",
            font=get_font("button")
        )
        button1.pack(side="left", padx=5)

        # 输入框字体
        entry_frame = ctk.CTkFrame(test_frame)
        entry_frame.pack(fill="x", padx=20, pady=10)

        entry_label = ctk.CTkLabel(entry_frame, text="输入框字体:", font=get_font("label"))
        entry_label.pack(side="left", padx=5)

        entry = ctk.CTkEntry(entry_frame, font=get_font("entry"), width=200)
        entry.pack(side="left", padx=5)
        entry.insert(0, "这是输入框的文字")

        # 文本框字体
        textbox_frame = ctk.CTkFrame(test_frame)
        textbox_frame.pack(fill="both", expand=True, padx=20, pady=10)

        textbox_label = ctk.CTkLabel(textbox_frame, text="文本框字体:", font=get_font("label"))
        textbox_label.pack(anchor="w", padx=5, pady=5)

        textbox = ctk.CTkTextbox(
            textbox_frame,
            font=get_font("textbox"),
            height=100
        )
        textbox.pack(fill="both", expand=True, padx=5, pady=5)
        textbox.insert("1.0", "这是文本框中的文字内容。现在的字体大小比原来的12号要大，提高了可读性。")
        textbox.configure(state="disabled")

        # 日志字体
        log_frame = ctk.CTkFrame(test_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        log_label = ctk.CTkLabel(log_frame, text="日志字体:", font=get_font("label"))
        log_label.pack(anchor="w", padx=5, pady=5)

        log_text = ctk.CTkTextbox(
            log_frame,
            font=get_font("log"),
            height=80
        )
        log_text.pack(fill="both", expand=True, padx=5, pady=5)
        log_text.insert("1.0", "这是日志框中的文字内容，使用等宽字体，适合显示代码和日志信息。")
        log_text.configure(state="disabled")

        # 关闭按钮
        close_button = ctk.CTkButton(
            main_frame,
            text="关闭测试窗口",
            command=self.root.destroy,
            font=get_font("button")
        )
        close_button.pack(pady=20)

    def run(self):
        """运行测试程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = FontTestApp()
    app.run()