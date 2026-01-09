# 🖐️Touchless Control System

**GestureFlow AI** is a lightweight Python application that transforms your webcam into a touchless controller. Navigate your computer using hand gestures and eye blinks without any physical contact.

Powered by **OpenCV** and **Google MediaPipe**, it provides a fluid, low-latency experience optimized for desktop use.

## 🚀 Features

* **🖱️ Precision Mouse:** Control the cursor with your index finger. Includes dynamic smoothing and acceleration for natural movement.
* **📜 Continuous Scrolling:**
    * ✊ **Closed Fist:** Continuous Scroll **UP**.
    * ✋ **Open Hand:** Continuous Scroll **DOWN**.
* **👀 Eye Click:** Blink your eyes deliberately to trigger a left click or double click.
* **🤏 Pinch Interaction:** Touch your thumb to your index finger to Click, Hold, or Drag & Drop.
* **⚡ Optimized Performance:** Runs smoothly at 60 FPS on standard CPUs.

## 🛠️ Installation

### Prerequisites
* Python 3.7 or higher
* A webcam

### Install Dependencies
Run the following command to install the required libraries:

```bash
pip install opencv-python mediapipe pyautogui numpy pillow screeninfo
```
##🎮 Usage
Clone the repository or download the script.

Run the main file:

```
python main.py
```
Calibration (Optional): Click the "CALIBRATE EYES" button and look at the camera for 3 seconds to adjust blink sensitivity to your lighting conditions.
 
