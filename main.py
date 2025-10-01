# main.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
import logging
import sys
import traceback
from ui import NovelGeneratorGUI

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('novel_generator.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def handle_global_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))

    error_msg = f"程序遇到未处理的错误:\n{exc_type.__name__}: {exc_value}\n\n详细错误信息已保存到日志文件。"

    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("程序错误", error_msg)
        root.destroy()
    except:
        print(error_msg)

def main():
    try:
        # 设置日志
        setup_logging()
        logging.info("程序启动")

        # 设置全局异常处理器
        sys.excepthook = handle_global_exception

        # 检查Python版本
        if sys.version_info < (3, 8):
            logging.error("需要Python 3.8或更高版本")
            return 1

        # 初始化GUI
        app = ctk.CTk()
        app.title("AI Novel Generator")

        # 设置窗口图标
        try:
            import os
            if os.path.exists("icon.ico"):
                app.iconbitmap("icon.ico")
        except Exception as e:
            logging.warning(f"无法加载图标: {e}")

        # 设置关闭事件处理
        def on_closing():
            try:
                logging.info("程序正常关闭")
                app.quit()
                app.destroy()
            except Exception as e:
                logging.error(f"关闭程序时出错: {e}")
                app.destroy()

        app.protocol("WM_DELETE_WINDOW", on_closing)

        # 创建GUI
        gui = NovelGeneratorGUI(app)

        logging.info("GUI初始化完成，启动主循环")
        app.mainloop()

    except Exception as e:
        logging.error(f"程序启动失败: {e}")
        logging.error(traceback.format_exc())
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
