# ONNX Detect

![ONNX-Detect-Screenshot](./assets/screenshot.png)

This is a modern desktop application built on **PyQt6**, **PyQt-Fluent-Widgets**, and **ONNXRuntime**, specifically designed for ONNX model object detection. It features a qframelesswindow-based Acrylic interface, supporting multiple input sources, flexible model management (built-in and custom), and robust camera control capabilities.

---

## 🌎 Language

* **[Read the original Chinese (中文) README here](./README_zh.md)**

---

## 🚀 Core Features

* **Modern UI Interface**:
    * Built with `PyQt6` and the `pyqt6-fluent-widgets` library, providing a smooth Fluent Design (WinUI) style.
    * Supports the Windows 11 Acrylic translucent background effect and allows users to customize the background color tone.
* **High-Performance Inference Backend**:
    * Utilizes `onnxruntime-gpu` as the core inference engine, prioritizing **NVIDIA GPU (CUDA)** for acceleration, with seamless fallback to CPU.
    * The UI automatically displays the currently used inference device (GPU or CPU).
* **Flexible Inference Modes**:
    * **One-Time Inference**:
        * Supports **image files** (e.g., .png, .jpg).
        * Supports **video files** (e.g., .mp4, .avi); results can be played after processing.
        * Supports **single-frame camera capture** for immediate, one-time inference on the current camera view.
    * **Real-Time Inference**:
        * Supports **video file** input, processing in real-time and displaying both original/inferred dual views.
        * Supports **live camera** input, performing inference while displaying the camera feed.
        * Supports **pause/resume** during real-time inference.
* **Powerful Model Management**:
    * **Built-in Models**: Automatically loads all YOLOv10 (n, s, m, l, x) ONNX models from the `models` directory.
    * **Custom Models**:
        * Supports loading arbitrary ONNX models via the `custom_models/custom_models_config.yaml` configuration file.
        * Full support for custom **Class Names**.
        * Full support for custom **Bounding Box Colors**.
        * Provides in-app shortcuts to open the model directory and configuration file.
* **Advanced Camera Control**:
    * Automatically detects and lists all available system cameras.
    * Supports switching between "Enable/Disable" the camera system and "Selecting a specific camera."
    * **Resolution Settings**:
        * Automatically detects resolutions supported by each camera (e.g., 1080p, 720p, 480p).
        * Allows users to **preset the resolution** for a specific camera before inference.
* **Comprehensive File Handling**:
    * **Full support for Chinese (Unicode) paths**, whether for uploading files, saving results, or loading models.
    * Supports selecting multiple save formats (JPG, PNG, BMP, TIFF) when saving inference results (images).
    * Supports custom setting and opening of the default save directory.
* **Result Playback and State Management**:
    * Built-in video player for playing back **video inference results** (displaying the original video and result video side-by-side).
    * Supports playing, pausing, and resetting (returning to the start) the video.
    * Powerful application state machine (`ApplicationStateManager`) intelligently manages the enabled/disabled status of UI components to prevent user errors (e.g., switching modes during inference or uploading files while the camera is on).
* **Other Features**:
    * Includes an "About" page showing the version and changelog.
    * Includes a "Clear" function to reset the application state and clear the display area with one click.
    * Includes a mysterious Easter Egg.

---

## 📜 Changelog

<details>
<summary>Click to Expand/Collapse</summary>

<h3>Version Update Log</h3>
<p><b>V1.2.3 - November 13, 2025</b></p>
<ul>
    <li>Switching the OpenCV camera API to MSMF on Windows to resolve stuttering issues with high-resolution cameras.</li>
    <li>Optimizing User Experience: Initialization and Resource Reloading</li>
</ul>
<p><b>V1.2.2 - October 31, 2025</b></p>
<ul>
    <li>Added "Camera Settings" feature, allowing selection of camera resolution.</li>
</ul>
<p><b>V1.2.1 - October 30, 2025</b></p>
<ul>
    <li>Added a [Mysterious Easter Egg], triggered by a mysterious number.</li>
    <li>Added "About" interface, displaying the update log.</li>
    <li>Added "Clear" function, allowing the clearing of the output preview.</li>
    <li>Full support for Chinese path file operations; provides multiple formats for image files when saving inference results.</li>
</ul>
<p><b>V1.2.0 - October 29, 2025</b></p>
<ul>
    <li>Code structure refactoring, referencing the MVVM architecture and integrating high-level abstraction layers.</li>
    <li>Fixed several potential user UI interaction bugs.</li>
</ul>
<p><b>V1.1.1 - October 28, 2025</b></p>
<ul>
    <li>Added camera system: supports detection, selection, and enabling/disabling of cameras.</li>
    <li>One-time and real-time inference modes support the camera as an input source.</li>
    <li>Optimized UI state management to enhance user experience.</li>
</ul>
<p><b>V1.1.0 - October 27, 2025</b></p>
<ul>
    <li>Added custom model loading, management, and configuration features.</li>
    <li>Added custom theme color selection feature.</li>
</ul>
<p><b>V1.0.0 - October 26, 2025</b></p>
<ul>
    <li>Initial release, resolved onnx-runtime compatibility issue preventing normal packaging of the executable with pyinstaller.</li>
    <li>Used the PyQt6-fluent-widgets third-party library for UI beautification.</li>
    <li>Supports the Acrylic interface effect under Win11.</li>
</ul>
<p><b>V0.0.0 - October 26, 2025</b></p>
<ul>
    <li>Initial version, supports single YOLOv10 ONNX model loading and inference.</li>
    <li>Provides one-time image/video inference and real-time video inference features.</li>
    <li>Standard QT UI.</li>
</ul>
<p><b>GitHub: </b><a href="https://github.com/STAR-REIN/remote-repo">Click to Visit</a></p>

</details>

---

## 🛠️ Installation and Running

### Option 1: (Recommended) Using the Packaged .exe File

1.  Download the latest `.exe` executable file from the [Releases](https://github.com/STAR-REIN/ONNX-Detect/releases) page of this repository and download the environment compressed package from the [cloud drive link](https://pan.baidu.com/s/1tn5E1JG5FpbbVukE9UkVGg?pwd=ntdn) (password: ntdn).
2.  Environment compressed package version descriptions:
    * No suffix: Complete version, compressed package size is about 1.41G; comes with CUDA and onnx-runtime-gpu environment. You only need a GPU that supports CUDA 12.x.x to use GPU inference. **Recommended for users with a GPU but no pre-installed CUDA environment.**
    * Lite_GPU: Simplified version, compressed package size is about 744MB; retains GPU support but requires the user to install the CUDA environment themselves. **Recommended for users with an existing CUDA environment.**
    * Lite_CPU: Simplified version, compressed package size is about 684MB; removes GPU support and only supports CPU inference. **Recommended for users without a GPU.**
3.  First, download and decompress the required environment package. Then, place the `.exe` file into the root directory of the decompressed folder and double-click to run.
4.  Ensure that your `models` folder and (optional) `custom_models` folder are in the same directory as the `.exe` file.
5.  Directly run the `.exe` file.

### Option 2: Running from Source Code

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/STAR-REIN/ONNX-Detect.git](https://github.com/STAR-REIN/ONNX-Detect.git)
    cd ONNX-Detect
    ```

2.  **Create Conda Environment**:
    This project uses the `environment.yml` file to manage dependencies.
    ```bash
    conda env create -f environment.yml
    ```

3.  **Activate Environment**:
    ```bash
    conda activate pyqt6_package
    ```

4.  **Prepare Models**:
    * Download the built-in model compressed package from the [cloud drive link](https://pan.baidu.com/s/). (Cloud drive link to be updated)
    * Place your downloaded YOLOv10 `basic` and `enhance` ONNX model files into the `models` folder in the root directory.
    * (Optional) Configure the `custom_models` folder according to the instructions in the next section.

5.  **Run the Program**:
    ```bash
    python main.py
    ```

**Dependency Notes**:
* This project requires **Python 3.12.1**.
* GPU acceleration relies on `onnxruntime-gpu==1.19.0`. Please ensure your **NVIDIA driver** and **CUDA Toolkit** versions are compatible with ONNXRuntime. If your GPU is not supported, `onnxruntime-gpu` will automatically fall back to CPU mode.

---

## 📖 Usage Guide

1.  **Start the Program**: Run `.exe` or `python main.py`.
2.  **Select a Model**:
    * **Built-in Models**: Click "Built-in Model Selection" and choose a model from the dropdown menu. The program will load it automatically.
    * **Custom Models**: Click "External Model Management" -> "Load Custom Models" to load your YAML configuration. Then click "External Model Selection" to choose a model.
3.  **Select Inference Mode**:
    * **One-Time Mode**: For processing a single file or a single frame.
    * **Run-Time Mode (Real-Time)**: For processing video files or a live camera stream.
4.  **Select Input Source**:
    * **File**: Click the "Upload File" button and select an image or video. A preview will display after upload.
    * **Camera**:
        1.  (Optional) Click the "Camera Settings" button. While the **camera system is disabled**, pre-select a resolution for the camera you plan to use.
        2.  Click "Camera Selection" -> "Enable/Disable ✕" to start the camera system.
        3.  Click "Camera Selection" again and select a detected camera from the list (e.g., "Camera 0").
        4.  The input preview area will now display the live camera feed.
5.  **Start Inference**:
    * Click the "Start Inference" (or "Start Real-Time Inference") button.
    * The button will change to "Stop Inference" during the process.
    * In real-time inference mode, the "Play/Pause" button can be used to pause/resume the inference thread.
6.  **View Results**:
    * **One-Time Mode**: Results will appear in the right-side "Inference Results" area. If it's a video, the player will load automatically after processing is complete.
    * **Real-Time Mode**: "Original Frame" and "Inference Results" will be displayed simultaneously on the left and right sides.
7.  **Save Results**: After inference is complete, click "File" -> "Save Inference Results."

---

## ⚙️ Configuring Custom Models

The power of this tool lies in its ability to easily load your own ONNX models.

1.  **Create Directory**: In the root directory where the `.exe` file or `main.py` is located, create a folder named `custom_models`.
2.  **Place Files**:
    * Place your `.onnx` model file (e.g., `my_model.onnx`) into the `custom_models` folder.
    * Create a configuration file named `custom_models_config.yaml` in this folder.
3.  **Edit `custom_models_config.yaml`**:
    The application will automatically create a template (`.template`) of this file upon launch. You can refer to this template for editing. The format is as follows:

    ```yaml
    # ==============================================================================
    # Custom ONNX Model Configuration Instructions (Template Content)
    # ... (Instruction Text) ...
    # ------------------------------------------------------------------------------
    # Example Configuration:
    # ==============================================================================

    custom_models:
      - model_file: "my_custom_model_v1.onnx"  # Ensure this onnx file is in the custom_models directory
        menu_display_name: "My Custom Model - V1 Car Pedestrian"
        class_names: ["car", "person", "truck", "bus"]
        colors: ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"] # Corresponding colors for car, person, truck, bus

      - model_file: "another_custom_detector.onnx" # Another custom model
        menu_display_name: "Another Detector - Object Recognition"
        class_names: ["bottle", "cup", "keyboard", "mouse", "laptop", "monitor"]
        colors:
          - "#E74C3C" # Red
          - "#2ECC71" # Green
          - "#3498DB" # Blue
          - "#F1C40F" # Yellow
          - "#9B59B6" # Purple
          - "#1ABC9C" # Teal
          # ... More colors
    # ==============================================================================
    ```

4.  **Load Models**:
    * Start the application.
    * Click "External Model Management" -> "Load Custom Models."
    * The program will read `custom_models_config.yaml`, verify the existence of the `.onnx` files, and add all valid models to the "External Model Selection" dropdown menu.

---

## 📄 License

This project is licensed under the [GPLv3 License](LICENSE).

## 🙏 Acknowledgments

* [YOLOv10](https://github.com/THU-MIG/YOLOv10)
* [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
* [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
* [ONNXRuntime](https://github.com/microsoft/onnxruntime)
