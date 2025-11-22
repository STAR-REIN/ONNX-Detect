# app/workers.py
import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

class PredictionWorker(QThread):
    frame_details_ready = pyqtSignal(list)
    finished = pyqtSignal(bool, str, float, QPixmap)
    progress = pyqtSignal(int)
    console_message = pyqtSignal(str)

    def __init__(self, predictor, input_path, output_path, is_video):
        super().__init__()
        self.predictor = predictor
        self.input_path = input_path
        self.output_path = output_path
        self.is_video = is_video
        self.is_running = True

    def run(self):
        try:
            if self.is_video:
                self._process_video()
            else:
                self._process_image()
        except Exception as e:
            self.console_message.emit(f"<font color='red'>线程错误: {e}</font>")
            self.finished.emit(False, str(e), 0.0, QPixmap())

    def _process_image(self):
        self.console_message.emit("开始处理图片...")
        self.progress.emit(25)
        result_img, detections, _ = self.predictor.predict_image_from_path(self.input_path)
        self.frame_details_ready.emit(detections)
        self.progress.emit(75)
        cv2.imwrite(self.output_path, result_img)
        self.progress.emit(100)
        pixmap = self._convert_cv_image_to_pixmap(result_img)
        self.finished.emit(True, self.output_path, 0.0, pixmap)
        self.console_message.emit("<font color='green'>图片处理完成。</font>")

    def _process_video(self):
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            self.finished.emit(False, "无法打开视频文件", 0.0, QPixmap())
            return
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (frame_width, frame_height))
        self.console_message.emit(f"开始处理视频: {total_frames} 帧, {fps:.2f} FPS...")
        frame_count = 0
        start_time = time.time()
        first_frame_pixmap = QPixmap()
        while self.is_running:
            ret, frame = cap.read()
            if not ret: break
            frame_count += 1
            processed_frame, detections = self.predictor.predict_frame(frame)
            self.frame_details_ready.emit(detections)
            out.write(processed_frame)
            if frame_count == 1:
                first_frame_pixmap = self._convert_cv_image_to_pixmap(processed_frame)
            progress_val = int((frame_count / total_frames) * 100)
            self.progress.emit(progress_val)
        end_time = time.time()
        cap.release()
        out.release()
        if frame_count > 0:
            avg_fps = frame_count / (end_time - start_time)
            self.console_message.emit(f"<font color='green'>视频处理完成。平均处理速度: {avg_fps:.2f} FPS。</font>")
            self.finished.emit(True, self.output_path, avg_fps, first_frame_pixmap)
        else:
            self.finished.emit(False, "未能处理任何视频帧", 0.0, QPixmap())

    def stop(self):
        self.is_running = False

    def _convert_cv_image_to_pixmap(self, cv_image):
        if cv_image is None: return QPixmap()
        h, w, ch = cv_image.shape
        bytes_per_line = ch * w
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(q_image)

class RealTimePredictionWorker(QThread):
    frame_processed = pyqtSignal(QPixmap, QPixmap, int, float, list)
    finished = pyqtSignal(bool, str)
    console_message = pyqtSignal(str)

    def __init__(self, predictor, input_path, output_path):
        super().__init__()
        self.predictor = predictor
        self.input_path = input_path
        self.output_path = output_path
        self.is_running = True
        self.is_paused = False
        self.frame_count = 0
        self.start_time = 0

    def run(self):
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            self.console_message.emit("<font color='red'>错误: 无法打开视频文件。</font>")
            self.finished.emit(False, "")
            return
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
        if not out.isOpened():
            self.console_message.emit(f"<font color='red'>错误: 无法创建视频写入器于 {self.output_path}。</font>")
            cap.release()
            self.finished.emit(False, "")
            return
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.console_message.emit("开始实时推理并保存...")
        self.start_time = time.time()
        is_success = False
        while self.is_running:
            if self.is_paused:
                self.msleep(100)
                continue
            ret, frame = cap.read()
            if not ret:
                self.console_message.emit("视频处理结束。")
                is_success = True
                break
            self.frame_count += 1
            processed_frame, detections = self.predictor.predict_frame(frame.copy())
            out.write(processed_frame)
            progress = int((self.frame_count / total_frames) * 100) if total_frames > 0 else 0
            elapsed_time = time.time() - self.start_time
            current_fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
            original_pixmap = self._convert_cv_image_to_pixmap(frame)
            processed_pixmap = self._convert_cv_image_to_pixmap(processed_frame)
            self.frame_processed.emit(original_pixmap, processed_pixmap, progress, current_fps, detections)
        cap.release()
        out.release()
        if not is_success:
            self.console_message.emit("<font color='orange'>实时推理被提前终止。</font>")
        self.finished.emit(is_success, self.output_path)

    def stop(self):
        self.is_running = False
        self.is_paused = False

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.console_message.emit("实时推理已暂停。")
        else:
            self.console_message.emit("实时推理已恢复。")

    def _convert_cv_image_to_pixmap(self, cv_image):
        if cv_image is None: return QPixmap()
        h, w, ch = cv_image.shape
        bytes_per_line = ch * w
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(q_image)
