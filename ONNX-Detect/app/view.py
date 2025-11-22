# app/view.py
import os
import cv2
import sys
from qframelesswindow import AcrylicWindow
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QStyle, QVBoxLayout, QWidget,
                             QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QFrame, QRadioButton, QButtonGroup, QSlider)
from PyQt6.QtGui import QDesktopServices,  QFont, QPixmap, QImage, QIcon,QResizeEvent
from PyQt6.QtCore import QUrl, Qt, QTimer, QDateTime,QSize
# 重新导入 CommandBar
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition,
    CommandBar, TransparentDropDownPushButton, RoundMenu, Action, FluentIcon,
    ProgressBar, StrongBodyLabel, PrimaryPushButton, PushButton, RadioButton,
    MessageBox, LineEdit,StyleSheetBase,Theme, isDarkTheme, qconfig
)

from .ui.ui_form import Ui_Form
from .config import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, MODEL_PATHS
from .workers import PredictionWorker, RealTimePredictionWorker
from yolov10_onnx import YOLOv10_ONNX_Predictor
from enum import Enum

# 1. 【新增】完全按照官方文档，定义一个 StyleSheet 类
class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet """
    MAIN_VIEW = "main_view"  # 对应我们的qss文件名 main_view.qss
    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        # 这会根据当前亮/暗主题，自动返回 "qss/light/main_view.qss" 或 "qss/dark/main_view.qss"
        return f"qss/{theme.value.lower()}/{self.value}.qss"


class MainView(AcrylicWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("\n--- MainView 初始化 (控制按钮对齐阶段) ---")
        self.resize(1000, 700)
        self.windowEffect.setAcrylicEffect(self.winId(), "CCDDDDDD")
        if hasattr(self, 'titleBar') and self.titleBar is not None:
            self.titleBar.setVisible(True)
            self.titleBar.raise_()
            # 隐藏 TitleBar 默认的 iconLabel 和 titleLabel
            if hasattr(self.titleBar, '_iconLabel'):
                self.titleBar._iconLabel.setVisible(False)
                print("DEBUG: Found default _iconLabel. Hiding it.")
            if hasattr(self.titleBar, '_titleLabel'):
                self.titleBar._titleLabel.setVisible(False)
                print("DEBUG: Found default _titleLabel. Hiding it.")
            self.custom_icon_label = QLabel(self.titleBar)
            self.custom_icon_label.setObjectName("customIconLabel")
            self.custom_icon_label.setFixedSize(QSize(20, 20))  # 标准标题栏图标大小

            self.custom_title_label = QLabel(self.titleBar)
            self.custom_title_label.setObjectName("customTitleLabel")

            title_bar_layout = self.titleBar.layout()
            if title_bar_layout is None:
                # 这种情况下，TitleBar可能还没创建自己的布局，我们创建一个
                print("WARNING: self.titleBar has no layout. Creating one.")
                title_bar_layout = QHBoxLayout(self.titleBar)
                self.titleBar.setLayout(title_bar_layout)
            else:
                print(f"DEBUG: self.titleBar already has a layout: {type(title_bar_layout)}")

            # ！！！ 核心修改 ！！！
            # 恢复 TitleBar 布局的默认边距，让 qframelesswindow 自己管理伸缩和居中
            # 同时确保左右有一定边距，让图标和按钮不至于顶到最边缘
            # 只设置左边距，右边距让 qframelesswindow 自己的控制按钮去管理
            title_bar_layout.setContentsMargins(8, 0, 0, 0)  # 左边距8px, 顶部/右部/底部0
            title_bar_layout.setSpacing(5)  # 图标和标题之间的间距
            # --------------------------------------------------------------------------------------
            # 移除所有关于 addStretch/insertStretch 的代码
            # 让 qframelesswindow 自己管理控制按钮在布局右侧的行为。
            # 我们只是替换了左侧的图标和标题。
            # --------------------------------------------------------------------------------------
            # 确保只添加一次 custom_icon_label 和 custom_title_label
            # 并且将它们插入到 TitleBar 布局的最前面
            # 注意：这里我们假设 qframelesswindow 的 control buttons 是在布局的靠右侧位置
            # 且不是通过 insertWidget(0) 加入的默认布局。

            # 清空自定义标签和图标，以避免重复添加
            # 为了严谨性，这里可以考虑移除所有非默认的item，但考虑到简单和qframelesswindow的内部机制，
            # 我们直接insertWidget，它会自动调整现有组件的索引。

            # 检查custom_icon_label是否已经在布局中, 避免重复添加 (虽然上面的_iconLabel.setVisible(False)暗示着_iconLabel已经存在)
            # 我们可以简单地在最前面添加我们的图标和标题，QFramelessWindow会将其默认按钮挤向右边

            # 为了确保我们的自定义内容在TitleBar的布局最左边：
            # 找到并移除可能存在的我们之前添加的自定义标签，然后再重新添加
            current_icon_index = title_bar_layout.indexOf(self.custom_icon_label)
            if current_icon_index != -1:
                item = title_bar_layout.takeAt(current_icon_index)
                if item: item.widget().deleteLater()

            current_title_index = title_bar_layout.indexOf(self.custom_title_label)
            if current_title_index != -1:
                item = title_bar_layout.takeAt(current_title_index)
                if item: item.widget().deleteLater()
            # 将我们的自定义图标和标题添加到最前面
            title_bar_layout.insertWidget(0, self.custom_icon_label)
            title_bar_layout.insertWidget(1, self.custom_title_label)
            # 设置窗口图标和标题，覆写的方法会触发更新我们自己的 QLabel
            self.setWindowTitle(" ONNX Detect V1.0.0")
            self.setWindowIcon(QIcon("assets/app_icon.png"))

            # 手动调用更新我们自己的标签，确保初始状态正确
            self._update_custom_labels()
            icon_path = "assets/app_icon.png"
            if not os.path.exists(icon_path):
                print(f"WARNING: 图标文件 '{icon_path}' 不存在！请检查路径是否正确。")
            else:
                print(f"INFO: 图标文件 '{icon_path}' 存在。")
            self.custom_icon_label.setVisible(True)
            self.custom_title_label.setVisible(True)
            print(f"DEBUG: titleBar.height() after setup: {self.titleBar.height()}px")
        else:
            print("ERROR: self.titleBar object DOES NOT EXIST or is None after super().__init__!")

        print("--- MainView 初始化结束 (控制按钮对齐阶段) ---\n")
        # --- 步骤 3: 为窗口本身设置主布局 ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        title_bar_height = self.titleBar.height() if hasattr(self, 'titleBar') and self.titleBar else 32
        self.main_layout.setContentsMargins(0, title_bar_height, 0, 0)  # 保持与标题栏高度相同的顶部边距
        # --- 步骤 4: 创建内容容器 ---
        self.content_container = QWidget(self)
        self.content_container.setObjectName("content_container")
        self.content_container.setStyleSheet("#content_container { background: transparent; }")
        container_layout = QVBoxLayout(self.content_container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(5)
        self.commandBar = self._create_command_bar()
        container_layout.addWidget(self.commandBar)
        self.ui_content_widget = QWidget()
        self.ui = Ui_Form()
        self.ui.setupUi(self.ui_content_widget)
        container_layout.addWidget(self.ui_content_widget, 1)
        # --- 步骤 5: 将内容容器添加到窗口的主布局中 ---
        self.main_layout.addWidget(self.content_container)
        # --- 步骤 6: 初始化状态和连接信号 (保持不变) ---
        self.default_save_directory = os.path.join(os.getcwd(), "predictions")
        self.uploaded_input_file = None
        self.predicted_output_file = None
        self._current_selected_model_path = ""
        self.yolo_predictor = None
        self.is_predicting = False
        self.is_playing_onetime = False
        self.worker = None
        self.playback_timer = QTimer(self)
        self.input_video_cap = None
        self.output_video_cap = None
        self.frame_detail_count = 0
        self._setup_ui()
        self._connect_signals()

        StyleSheet.MAIN_VIEW.apply(self)

        self.console_msg("程序启动成功。")

    def _update_custom_labels(self):
        """ Manually update the text and icon of our custom labels. """
        if hasattr(self, 'custom_icon_label') and self.custom_icon_label:
            icon_pixmap = self.windowIcon().pixmap(20, 20)
            self.custom_icon_label.setPixmap(icon_pixmap)
        if hasattr(self, 'custom_title_label') and self.custom_title_label:
            self.custom_title_label.setText(self.windowTitle())

    def setWindowTitle(self, title: str):
        super().setWindowTitle(title)
        self._update_custom_labels()

    def setWindowIcon(self, icon: QIcon):
        super().setWindowIcon(icon)
        self._update_custom_labels()

    # 重新引入创建 CommandBar 的方法
    def _create_command_bar(self):
        """动态创建命令栏并返回它"""
        commandBar = CommandBar(self)
        # --- 文件操作 ---
        fileMenuButton = TransparentDropDownPushButton(FluentIcon.DOCUMENT, "文件")
        fileMenu = RoundMenu(parent=self)
        action_set_dir = Action(FluentIcon.FOLDER, "设置默认保存目录")
        action_open_dir = Action(FluentIcon.SEND_FILL, "打开保存目录")
        self.actionSaveOutput = Action(FluentIcon.SAVE, "保存推理结果")
        fileMenu.addActions([action_set_dir, action_open_dir, self.actionSaveOutput])
        fileMenuButton.setMenu(fileMenu)
        action_set_dir.triggered.connect(self.select_default_save_directory)
        action_open_dir.triggered.connect(self.open_default_save_directory)
        self.actionSaveOutput.triggered.connect(self.save_output)
        # --- 模型选择 ---
        modelMenuButton = TransparentDropDownPushButton(FluentIcon.CONSTRACT, "选择模型")  # 使用 CONSTRACT 图标
        modelMenu = RoundMenu(parent=self)
        # --- 【核心新增代码】在这里为下拉菜单设置字体 ---

        # 【关键】这里没有 setFont 或 setStyleSheet

        self.model_actions = {}
        if MODEL_PATHS:
            basic_models = sorted([key for key in MODEL_PATHS if "basic" in key.lower()])
            enhance_models = sorted([key for key in MODEL_PATHS if "enhance" in key.lower()])

            def add_model_action(model_key):
                action_text = model_key.replace("_", " ").replace("Yolov10", "YoloV10").title()
                action = Action(action_text)
                action.setCheckable(True)
                action.triggered.connect(lambda checked, key=model_key: self.set_current_model(key))
                modelMenu.addAction(action)
                self.model_actions[model_key] = action

            # ... 后续代码不变 ...
            if basic_models:
                for model_key in basic_models: add_model_action(model_key)
            if basic_models and enhance_models: modelMenu.addSeparator()
            if enhance_models:
                for model_key in enhance_models: add_model_action(model_key)

        modelMenuButton.setMenu(modelMenu)
        commandBar.addWidget(fileMenuButton)
        commandBar.addWidget(modelMenuButton)

        return commandBar

    # 修正 enable_ui_elements，重新使用 self.commandBar
    def enable_ui_elements(self, enable):
        """启用或禁用UI元素"""
        self.ui.Upload.setEnabled(enable)
        self.commandBar.setEnabled(enable)  # <-- 恢复这一行
        self.ui.OneTime_radio.setEnabled(enable)
        self.ui.RunTime_radio.setEnabled(enable)

        is_runtime_mode = self.ui.RunTime_radio.isChecked()
        if is_runtime_mode:
            self.ui.StartPredict.setEnabled(True)
            self.ui.PlayStop.setEnabled(self.is_predicting)
            self.ui.Restart.setEnabled(not self.is_predicting and self.uploaded_input_file is not None)
            self.actionSaveOutput.setEnabled(False)
        else:
            self.ui.StartPredict.setEnabled(enable)
            can_play = enable and self.predicted_output_file is not None
            self.ui.PlayStop.setEnabled(can_play)
            self.ui.Restart.setEnabled(can_play)
            self.actionSaveOutput.setEnabled(enable)

    # ... 从这里开始，下面的所有其他方法都保持原样，无需改动 ...
    def _setup_ui(self):
        """初始化UI组件状态"""
        os.makedirs(self.default_save_directory, exist_ok=True)
        self.ui.progressBar.setValue(0)
        self.ui.videoDisplayArea.setText("请上传图片或视频")
        self.ui.predictDisplayArea.setText("推理结果将显示在此处")
        self.ui.FPS.setText("FPS: --")
        # -------------------【从这里开始修改】-------------------
        # 1. 将原来的 QStyle 图标替换为 FluentIcon
        self.play_icon = FluentIcon.PLAY
        self.pause_icon = FluentIcon.PAUSE
        # 2. 设置按钮的初始图标
        self.ui.PlayStop.setIcon(self.play_icon)
        self.ui.Restart.setIcon(FluentIcon.SYNC)  # 为 Restart 按钮设置图标
        self.ui.PlayStop.setEnabled(False)
        self.ui.Restart.setEnabled(False)
        self.ui.OneTime_radio.setChecked(True)



    def _connect_signals(self):
        """连接所有信号与槽"""
        self.ui.Upload.clicked.connect(self.select_input_file)
        self.ui.StartPredict.clicked.connect(self.start_prediction)
        self.ui.PlayStop.clicked.connect(self.toggle_playback)
        self.ui.Restart.clicked.connect(self.restart_playback)
        self.ui.OneTime_radio.toggled.connect(self._on_mode_changed)
        self.ui.RunTime_radio.toggled.connect(self._on_mode_changed)
        self.playback_timer.timeout.connect(self._update_playback_frame)

        if MODEL_PATHS:
            first_model_key = list(MODEL_PATHS.keys())[0]
            self.set_current_model(first_model_key)

    def _on_mode_changed(self):
        if self.is_predicting:
            self.console_msg("<font color='orange'>推理模式已更改，正在停止当前任务...</font>")
            if self.worker: self.worker.stop()
        is_runtime_mode = self.ui.RunTime_radio.isChecked()
        self.ui.PlayStop.setEnabled(not is_runtime_mode and self.predicted_output_file is not None)
        self.ui.Restart.setEnabled(not is_runtime_mode and self.predicted_output_file is not None)
        self.actionSaveOutput.setEnabled(not is_runtime_mode)

    def set_current_model(self, model_key):
        model_path = MODEL_PATHS.get(model_key)
        if model_path and os.path.exists(model_path):
            self._current_selected_model_path = model_path
            self.console_msg(f"模型已选择: {os.path.basename(model_path)}")
            try:
                self.yolo_predictor = YOLOv10_ONNX_Predictor(model_path)
                self.console_msg("<font color='green'>ONNX预测器加载成功。</font>")
                for key, action in self.model_actions.items():
                    action.setChecked(key == model_key)
            except Exception as e:
                self.yolo_predictor = None
                self.console_msg(f"<font color='red'>ONNX预测器加载失败: {e}</font>")
                QMessageBox.critical(self, "模型加载失败", f"加载模型 {os.path.basename(model_path)} 失败:\n{e}")
        else:
            self.console_msg(f"<font color='red'>错误: 模型文件不存在或未在MODEL_PATHS中定义: {model_path}</font>")

    def select_input_file(self):
        file_filter = "所有媒体文件 ({});;图片文件 ({});;视频文件 ({})".format(
            " ".join([f'*{ext}' for ext in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS]),
            " ".join([f'*{ext}' for ext in IMAGE_EXTENSIONS]),
            " ".join([f'*{ext}' for ext in VIDEO_EXTENSIONS])
        )
        selected_file, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", file_filter)
        if selected_file:
            self._reset_state()
            self.uploaded_input_file = selected_file
            self.console_msg(f"已选择文件: {os.path.basename(self.uploaded_input_file)}")
            self._display_input_preview()

    def _update_console_with_details(self, details: list):
        if not details:
            return
        self.frame_detail_count += 1
        html = f"<b>[帧 {self.frame_detail_count} 检测结果]</b><br>"
        for item in details:
            class_name = item['class_name']
            confidence = item['score']
            box = item['box']
            html += (
                f"&nbsp;&nbsp;- <font color='#3498db'>类别:</font> <b>{class_name}</b>, "
                f"<font color='#e67e22'>置信度:</font> {confidence:.2%}, "
                f"<font color='#2ecc71'>位置:</font> [{box[0]}, {box[1]}, {box[2]}, {box[3]}]<br>"
            )
        self.console_msg(html)

    def start_prediction(self):
        if not self.yolo_predictor:
            QMessageBox.warning(self, "模型未加载", "请先选择一个有效的ONNX模型。")
            return
        if not self.uploaded_input_file:
            QMessageBox.warning(self, "未选择文件", "请先上传一个图片或视频文件。")
            return
        if self.ui.OneTime_radio.isChecked():
            self._start_onetime_prediction()
        elif self.ui.RunTime_radio.isChecked():
            self._start_runtime_prediction()

    def _start_onetime_prediction(self):
        if self.is_predicting:
            self.console_msg("<font color='orange'>警告: 已有推理任务正在进行。</font>")
            return
        self.frame_detail_count = 0
        self.is_predicting = True
        self.enable_ui_elements(False)
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setValue(0)
        self.ui.predictDisplayArea.clear()
        self.ui.predictDisplayArea.setText("正在准备推理...")
        is_video = os.path.splitext(self.uploaded_input_file)[1].lower() in VIDEO_EXTENSIONS
        file_ext = ".mp4" if is_video else ".png"
        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        temp_output_filename = f"temp_prediction_{timestamp}{file_ext}"
        temp_output_path = os.path.join(self.default_save_directory, temp_output_filename)
        self.worker = PredictionWorker(self.yolo_predictor, self.uploaded_input_file, temp_output_path, is_video)
        self.worker.frame_details_ready.connect(self._update_console_with_details)
        self.worker.finished.connect(self._prediction_finished)
        self.worker.progress.connect(self.ui.progressBar.setValue)
        self.worker.console_message.connect(self.console_msg)
        self.worker.start()

    def _start_runtime_prediction(self):
        if self.is_predicting:
            if self.worker: self.worker.stop()
            return

        is_video = os.path.splitext(self.uploaded_input_file)[1].lower() in VIDEO_EXTENSIONS
        if not is_video:
            QMessageBox.warning(self, "模式错误", "实时推理模式仅支持视频文件。")
            return
        self.frame_detail_count = 0
        self.is_predicting = True
        self.enable_ui_elements(False)
        self.ui.StartPredict.setText("停止推理")
        self.ui.PlayStop.setEnabled(True)
        self.ui.PlayStop.setIcon(self.pause_icon)
        self.ui.predictDisplayArea.clear()
        self.ui.predictDisplayArea.setText("准备实时推理...")
        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        temp_output_filename = f"temp_realtime_{timestamp}.mp4"
        temp_output_path = os.path.join(self.default_save_directory, temp_output_filename)
        self.worker = RealTimePredictionWorker(self.yolo_predictor, self.uploaded_input_file, temp_output_path)
        self.worker.frame_processed.connect(self._update_realtime_ui_and_details)
        self.worker.finished.connect(self._realtime_prediction_finished)
        self.worker.console_message.connect(self.console_msg)
        self.worker.start()

    def _prediction_finished(self, is_success, result_path, avg_fps, first_frame_pixmap):
        self.is_predicting = False
        self.enable_ui_elements(True)
        if is_success:
            self.predicted_output_file = result_path
            self.ui.FPS.setText(f"FPS: {avg_fps:.2f}" if avg_fps > 0 else "FPS: --")
            self.display_media_on_label(first_frame_pixmap, self.ui.predictDisplayArea)
            if os.path.splitext(self.uploaded_input_file)[1].lower() in VIDEO_EXTENSIONS:
                self.ui.PlayStop.setEnabled(True)
                self.ui.Restart.setEnabled(True)
        else:
            self.console_msg(f"<font color='red'>推理失败: {result_path}</font>")
            self.ui.predictDisplayArea.setText("推理失败")
            QMessageBox.critical(self, "推理错误", f"推理过程中发生错误: {result_path}")

    def _update_realtime_ui_and_details(self, original_pixmap, processed_pixmap, progress, fps, details):
        self.display_media_on_label(original_pixmap, self.ui.videoDisplayArea)
        self.display_media_on_label(processed_pixmap, self.ui.predictDisplayArea)
        self.ui.progressBar.setValue(progress)
        self.ui.FPS.setText(f"FPS: {fps:.2f}")
        self._update_console_with_details(details)

    def _realtime_prediction_finished(self, is_success, result_path):
        self.is_predicting = False
        self.enable_ui_elements(True)
        self.ui.StartPredict.setText("开始推理")
        self.worker = None
        self.ui.PlayStop.setEnabled(False)
        self.ui.PlayStop.setIcon(self.play_icon)
        if is_success:
            self.console_msg(
                f"实时推理完成，结果已保存至: <a href='file:///{result_path}'>{os.path.basename(result_path)}</a>")
            self.predicted_output_file = result_path
            self.ui.PlayStop.setEnabled(True)
            self.ui.Restart.setEnabled(True)
            self.actionSaveOutput.setEnabled(True)
        else:
            self.console_msg("<font color='orange'>实时推理未正常完成。</font>")
            self.predicted_output_file = None
            self.ui.PlayStop.setEnabled(False)
            self.ui.Restart.setEnabled(self.uploaded_input_file is not None)
            self.actionSaveOutput.setEnabled(False)

    def toggle_playback(self):
        if self.is_predicting and self.ui.RunTime_radio.isChecked():
            if self.worker:
                self.worker.toggle_pause()
                if self.worker.is_paused:
                    self.ui.PlayStop.setIcon(self.play_icon)
                else:
                    self.ui.PlayStop.setIcon(self.pause_icon)
            return
        if not self.uploaded_input_file or not self.predicted_output_file:
            return
        if self.is_playing_onetime:
            self.playback_timer.stop()
            self.is_playing_onetime = False
            self.ui.PlayStop.setIcon(self.play_icon)
            self.console_msg("播放已暂停。")
        else:
            if not self.input_video_cap:
                self._start_playback_session()
            else:
                fps = self.input_video_cap.get(cv2.CAP_PROP_FPS)
                self.playback_timer.start(int(1000 / fps))
                self.is_playing_onetime = True
                self.ui.PlayStop.setIcon(self.pause_icon)
                self.console_msg("播放已恢复。")

    def restart_playback(self):
        if self.ui.RunTime_radio.isChecked() and not self.predicted_output_file:
            self.console_msg("重新开始实时推理...")
            self._start_runtime_prediction()
            return
        if self.predicted_output_file:
            self._stop_playback_session()
            self._start_playback_session()
        else:
            self.console_msg("没有可供回放的文件。")

    def _start_playback_session(self):
        self.input_video_cap = cv2.VideoCapture(self.uploaded_input_file)
        self.output_video_cap = cv2.VideoCapture(self.predicted_output_file)
        if not self.input_video_cap.isOpened() or not self.output_video_cap.isOpened():
            QMessageBox.warning(self, "播放错误", "无法打开视频文件进行播放。")
            self._stop_playback_session()
            return
        fps = self.input_video_cap.get(cv2.CAP_PROP_FPS)
        self.playback_timer.start(int(1000 / fps))
        self.is_playing_onetime = True
        self.ui.PlayStop.setIcon(self.pause_icon)
        self.console_msg("开始播放...")

    def _update_playback_frame(self):
        if not self.input_video_cap or not self.output_video_cap: return
        ret1, frame1 = self.input_video_cap.read()
        ret2, frame2 = self.output_video_cap.read()
        if not ret1 or not ret2:
            self._stop_playback_session()
            self.console_msg("播放结束。")
            return
        total_frames = self.input_video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
        current_frame = self.input_video_cap.get(cv2.CAP_PROP_POS_FRAMES)
        progress = int((current_frame / total_frames) * 100) if total_frames > 0 else 0
        self.ui.progressBar.setValue(progress)
        pixmap1 = self._convert_cv_image_to_pixmap(frame1)
        pixmap2 = self._convert_cv_image_to_pixmap(frame2)
        self.display_media_on_label(pixmap1, self.ui.videoDisplayArea)
        self.display_media_on_label(pixmap2, self.ui.predictDisplayArea)

    def _stop_playback_session(self):
        self.is_playing_onetime = False
        self.playback_timer.stop()
        if self.input_video_cap: self.input_video_cap.release()
        if self.output_video_cap: self.output_video_cap.release()
        self.input_video_cap = None
        self.output_video_cap = None
        self.ui.PlayStop.setIcon(self.play_icon)
        self.ui.progressBar.setValue(0)

    def save_output(self):
        if not self.predicted_output_file or not os.path.exists(self.predicted_output_file):
            QMessageBox.warning(self, "无结果可保存", "请先完成一次推理以生成结果。")
            return
        original_basename = os.path.splitext(os.path.basename(self.uploaded_input_file))[0]
        file_ext = os.path.splitext(self.predicted_output_file)[1]
        default_save_name = f"{original_basename}_predicted{file_ext}"
        save_path, _ = QFileDialog.getSaveFileName(self, "保存预测结果",
                                                   os.path.join(self.default_save_directory, default_save_name),
                                                   f"Files (*{file_ext})")
        if save_path:
            try:
                os.rename(self.predicted_output_file, save_path)
                self.console_msg(f"<font color='purple'>结果已保存至: {save_path}</font>")
                QMessageBox.information(self, "保存成功", f"结果已成功保存到:\n{save_path}")
                self.predicted_output_file = None
            except Exception as e:
                self.console_msg(f"<font color='red'>保存失败: {e}</font>")
                QMessageBox.critical(self, "保存失败", f"无法保存文件: {e}")

    def select_default_save_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择默认保存目录", self.default_save_directory)
        if dir_path:
            self.default_save_directory = dir_path
            self.console_msg(f"默认保存目录已设置为: {dir_path}")

    def open_default_save_directory(self):
        if os.path.exists(self.default_save_directory):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.default_save_directory))
        else:
            QMessageBox.warning(self, "目录不存在", f"目录 '{self.default_save_directory}' 不存在。")

    def _display_input_preview(self):
        file_ext = os.path.splitext(self.uploaded_input_file)[1].lower()
        pixmap = QPixmap()
        if file_ext in IMAGE_EXTENSIONS:
            pixmap = QPixmap(self.uploaded_input_file)
        elif file_ext in VIDEO_EXTENSIONS:
            cap = cv2.VideoCapture(self.uploaded_input_file)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    pixmap = self._convert_cv_image_to_pixmap(frame)
                cap.release()
        self.display_media_on_label(pixmap, self.ui.videoDisplayArea)

    def display_media_on_label(self, pixmap, label):
        if not pixmap or pixmap.isNull():
            label.setText("无法显示预览")
            return
        scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)

    def _convert_cv_image_to_pixmap(self, cv_image):
        if cv_image is None: return QPixmap()
        h, w, ch = cv_image.shape
        bytes_per_line = ch * w
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return QPixmap(QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888))

    def console_msg(self, msg):
        self.ui.console_text_edit.append(msg)
        self.ui.console_text_edit.verticalScrollBar().setValue(self.ui.console_text_edit.verticalScrollBar().maximum())

    def _reset_state(self):
        self._stop_playback_session()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.uploaded_input_file = None
        self.predicted_output_file = None
        self.is_predicting = False
        self.worker = None
        self.ui.videoDisplayArea.clear()
        self.ui.videoDisplayArea.setText("请上传图片或视频")
        self.ui.predictDisplayArea.clear()
        self.ui.predictDisplayArea.setText("推理结果将显示在此处")
        self.ui.FPS.setText("FPS: --")
        self.ui.progressBar.setValue(0)
        self.ui.PlayStop.setEnabled(False)
        self.ui.Restart.setEnabled(False)
        self.ui.StartPredict.setText("开始推理")
        self.actionSaveOutput.setEnabled(False)

    def closeEvent(self, event):
        self._reset_state()
        event.accept()

