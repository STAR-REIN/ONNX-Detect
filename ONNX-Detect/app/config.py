# app/config.py
import os
import sys

# 检查 PyInstaller 是否将应用程序打包为单文件或单目录
if getattr(sys, 'frozen', False):
    # 对于 PyInstaller 打包的情况，sys.executable 总是指向当前执行文件的路径
    # os.path.dirname(sys.executable) 就能 reliably 获取到 EXE 文件所在的目录
    BASE_DIR = os.path.dirname(sys.executable)
    print(f"DEBUG (frozen): BASE_DIR set to sys.executable dirname: {BASE_DIR}")
else:
    # 对于开发环境，保持原样
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"DEBUG (development): BASE_DIR set to __file__ dirname twice: {BASE_DIR}")


IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm', '.ts')

# 所有的 ONNX 模型路径都基于 BASE_DIR 和 "models" 目录
MODEL_PATHS = {
    "yolov10n_basic": os.path.join(BASE_DIR, "models", "yolov10n_basic.onnx"),
    "yolov10n_enhance": os.path.join(BASE_DIR, "models", "yolov10n_enhance.onnx"),
    "yolov10s_basic": os.path.join(BASE_DIR, "models", "yolov10s_basic.onnx"),
    "yolov10s_enhance": os.path.join(BASE_DIR, "models", "yolov10s_enhance.onnx"),
    "yolov10m_basic": os.path.join(BASE_DIR, "models", "yolov10m_basic.onnx"),
    "yolov10m_enhance": os.path.join(BASE_DIR, "models", "yolov10m_enhance.onnx"),
    "yolov10l_basic": os.path.join(BASE_DIR, "models", "yolov10l_basic.onnx"),
    "yolov10l_enhance": os.path.join(BASE_DIR, "models", "yolov10l_enhance.onnx"),
    "yolov10x_basic": os.path.join(BASE_DIR, "models", "yolov10x_basic.onnx"),
    "yolov10x_enhance": os.path.join(BASE_DIR, "models", "yolov10x_enhance.onnx"),
}

# 新增：字体文件目录
FONT_DIR = os.path.join(BASE_DIR, "assets")

# 打印最终的 BASE_DIR 和一个模型路径，便于调试
print(f"Final BASE_DIR: {BASE_DIR}")
print(f"Example Model Path: {MODEL_PATHS.get('yolov10n_basic')}")
print(f"Final FONT_DIR: {FONT_DIR}") # 新增日志
