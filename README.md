# 🖐️Touchless Control System

**GestureFlow AI**, bilgisayarınızı fiziksel temas olmadan, sadece el hareketleri ve göz kırpma mimikleriyle kontrol etmenizi sağlayan Python tabanlı bir yapay zeka projesidir.

Proje, **OpenCV** ve **Google MediaPipe** kütüphanelerini kullanarak yüksek performanslı ve düşük gecikmeli (low-latency) bir deneyim sunar.

## 🚀 Özellikler

* **🖱️ Akıllı Mouse Kontrolü:** İşaret parmağı ile imleci yönetin. Hıza duyarlı ivmelenme (acceleration) ve titreme önleyici (stabilization) algoritmalar içerir.
* **📜 Akışkan Scroll (Kaydırma):**
    * ✊ **Yumruk:** Sayfayı yukarı kaydırır.
    * ✋ **Açık El:** Sayfayı aşağı kaydırır.
* **👀 Göz ile Tıklama:** Gözlerinizi bilinçli olarak kırparak tıklama veya çift tıklama yapın.
* **🤏 Pinch (Kıstırma) Modu:** Baş ve işaret parmağınızı birleştirerek tıklama veya "Sürükle-Bırak" (Drag & Drop) işlemi yapın.
* **⚡ Optimize Performans:** 60 FPS akıcılığında çalışır.

## 🛠️ Kurulum

Projeyi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

### Gereksinimler
Python 3.7 veya üzeri gereklidir.

```bash
pip install opencv-python mediapipe pyautogui face-recognition numpy pillow screeninfo
