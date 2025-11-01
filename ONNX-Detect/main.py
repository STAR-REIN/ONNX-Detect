# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont  # 导入这两个类
from app.views.main_window import MainView
from qfluentwidgets import setTheme, Theme
from app.configs.config import FONT_DIR  # 导入 FONT_DIR

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- 字体加载阶段 ---
    print("\n--- 字体加载阶段 ---")
    font_family_name = "JetBrains Maple Mono"  # 期望的字体家族名称（可能不完全匹配文件名）
    loaded_font_families = []

    # 确保字体目录存在
    if not os.path.exists(FONT_DIR):
        print(f"ERROR: 字体目录 '{FONT_DIR}' 不存在。跳过字体加载。")
    else:
        # 遍历字体目录下的所有 .ttf 文件并加载
        for filename in os.listdir(FONT_DIR):
            if filename.lower().endswith('.ttf'):
                font_path = os.path.join(FONT_DIR, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    # addApplicationFont 成功会返回一个ID，然后可以用这个ID获取字体家族名称
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        loaded_font_families.append(families[0])
                        print(f"INFO: 成功加载字体文件 '{filename}', 字体家族: '{families[0]}'")
                    else:
                        print(f"WARNING: 成功加载字体文件 '{filename}', 但无法获取字体家族名称 (ID: {font_id})")
                else:
                    print(f"ERROR: 无法加载字体文件 '{filename}'。请检查文件是否损坏或格式错误。")

        # 对加载的字体家族进行去重和排序
        unique_loaded_families = sorted(list(set(loaded_font_families)))

        if unique_loaded_families:
            print(f"INFO: 应用程序检测到所有已加载字体家族: {', '.join(unique_loaded_families)}")
            # 尝试设置应用程序的默认字体为 JetBrains Mono 系列中的某一个
            # 通常，直接使用家族名如 "JetBrains Mono" 会选择 Regular 样式
            if font_family_name in unique_loaded_families:
                # 可以根据需要调整字体大小
                default_font = QFont(font_family_name, 10)
                app.setFont(default_font)
                print(f"INFO: 成功将应用程序默认字体设置为 '{font_family_name}'。")
            else:
                print(f"WARNING: 指定的默认字体家族 '{font_family_name}' 未在加载的字体中找到。")
                print(f"DEBUG: 尝试将应用程序默认字体设置为第一个加载的字体家族: '{unique_loaded_families[0]}'")
                app.setFont(QFont(unique_loaded_families[0], 10))
        else:
            print("WARNING: 未加载任何自定义字体文件。")
    print("--- 字体加载阶段结束 ---\n")
    # --- 字体加载阶段结束 ---

    # 只需要设置全局主题即可
    setTheme(Theme.LIGHT)

    # MainView 在创建时，会自动根据主题加载对应的 QSS 文件
    window = MainView()

    window.show()
    sys.exit(app.exec())
