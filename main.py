import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import face_recognition
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import os
import math

# --- SİSTEM AYARLARI ---
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
pyautogui.MINIMUM_DURATION = 0

class HandEyeBackend:
    def __init__(self, user_photo_path):
        self.wCam, self.hCam = 640, 480
        self.frameR = 100 
        
        # --- HASSASİYET ---
        self.deadzone = 4.5
        self.mouse_sensitivity = 1.8
        self.mouse_acceleration = 0.8
        
        # SCROLL HIZI (Ne kadar yüksek olursa o kadar hızlı akar)
        self.scroll_speed = 25 
        
        # --- DURUM ---
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        
        # Click
        self.pinch_active = False 
        self.is_dragging = False
        
        # Göz
        self.eye_click_enabled = True 
        self.eye_ratio_closed = 0.22 
        self.blink_counter = 0
        self.last_blink_time = 0
        
        # Kalibrasyon
        self.is_calibrating = False
        self.calibration_data = []
        
        self.is_running = False
        self.is_locked = True
        self.user_photo_path = user_photo_path
        self.wScr, self.hScr = pyautogui.size()
        
        # --- AI ---
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, 
            model_complexity=1, 
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7
        )
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1, 
            refine_landmarks=True, 
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7
        )
        
        self.known_face_encodings = []
        self.load_user_face()

    def load_user_face(self):
        if os.path.exists(self.user_photo_path):
            try:
                user_image = face_recognition.load_image_file(self.user_photo_path)
                encs = face_recognition.face_encodings(user_image)
                if encs: self.known_face_encodings.append(encs[0])
            except: pass

    def calibrate_start(self):
        self.is_calibrating = True
        self.calibration_data = []

    def get_ear(self, landmarks, indices):
        p = [landmarks[i] for i in indices]
        v = (math.hypot(p[1].x-p[5].x, p[1].y-p[5].y) + math.hypot(p[2].x-p[4].x, p[2].y-p[4].y))
        h = math.hypot(p[0].x-p[3].x, p[0].y-p[3].y)
        return v / (2.0 * h) if h != 0 else 0

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        img_h, img_w, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        info_text = ""

        # --- GÜVENLİK ---
        if self.is_locked:
            cv2.putText(frame, "KILITLI", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb_small)
            if locs:
                encs = face_recognition.face_encodings(rgb_small, locs)
                for enc in encs:
                    if True in face_recognition.compare_faces(self.known_face_encodings, enc, tolerance=0.5):
                        self.is_locked = False
            return frame, info_text

        # --- GÖZ MODÜLÜ ---
        face_results = self.face_mesh.process(img_rgb)
        if face_results.multi_face_landmarks and self.eye_click_enabled:
            lms = face_results.multi_face_landmarks[0].landmark
            ear = (self.get_ear(lms, [33, 160, 158, 133, 153, 144]) + self.get_ear(lms, [362, 385, 387, 263, 373, 380])) / 2.0
            
            if self.is_calibrating:
                self.calibration_data.append(ear)
                cv2.putText(frame, "KALIBRE...", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
                if len(self.calibration_data) > 30:
                    self.eye_ratio_closed = (sum(self.calibration_data) / len(self.calibration_data)) * 0.70
                    self.is_calibrating = False
                    info_text = "OK"
            else:
                if ear < self.eye_ratio_closed:
                    self.blink_counter += 1
                else:
                    if self.blink_counter > 4:
                        if (time.time() - self.last_blink_time) < 0.6:
                            pyautogui.doubleClick()
                            info_text = "CIF TIK"
                        else:
                            pyautogui.click()
                            info_text = "TIK"
                        self.last_blink_time = time.time()
                    self.blink_counter = 0

        # --- EL MODÜLÜ ---
        hand_results = self.hands.process(img_rgb)
        if hand_results.multi_hand_landmarks:
            for hand_lms in hand_results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(hand_lms.landmark):
                    lmList.append([id, int(lm.x * img_w), int(lm.y * img_h)])
                
                # Koordinatlar
                x1, y1 = lmList[8][1], lmList[8][2] # İşaret
                x2, y2 = lmList[4][1], lmList[4][2] # Baş
                
                # --- PARMAK ANALİZİ ---
                fingers_open = []
                # İşaret, Orta, Yüzük, Serçe (4 parmak)
                for tip in [8, 12, 16, 20]:
                    if lmList[tip][2] < lmList[tip-2][2]: fingers_open.append(True) # Açık
                    else: fingers_open.append(False) # Kapalı
                
                # MODLARI BELİRLE
                
                # 1. MOD: YUMRUK (Hepsi Kapalı) -> SCROLL UP
                if not any(fingers_open): 
                    info_text = "SCROLL YUKARI"
                    pyautogui.scroll(self.scroll_speed) # Pozitif değer = Yukarı
                    cv2.putText(frame, "YUKARI AKIYOR...", (50, 250), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
                
                # 2. MOD: DUR / EL AÇIK (Hepsi Açık) -> SCROLL DOWN
                elif all(fingers_open):
                    info_text = "SCROLL ASAGI"
                    pyautogui.scroll(-self.scroll_speed) # Negatif değer = Aşağı
                    cv2.putText(frame, "ASAGI AKIYOR...", (50, 250), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

                # 3. MOD: POINTER (Sadece İşaret Parmağı Açık) -> MOUSE
                elif fingers_open[0] and not fingers_open[1] and not fingers_open[2] and not fingers_open[3]:
                    
                    # --- Mouse Hareketi ---
                    box_w = self.wCam - 2 * self.frameR
                    box_h = self.hCam - 2 * self.frameR
                    norm_x = (x1 - self.frameR) / box_w - 0.5
                    norm_y = (y1 - self.frameR) / box_h - 0.5
                    
                    accel_x = np.sign(norm_x) * (abs(norm_x) ** self.mouse_acceleration)
                    accel_y = np.sign(norm_y) * (abs(norm_y) ** self.mouse_acceleration)
                    
                    target_x = (accel_x * self.mouse_sensitivity + 0.5) * self.wScr
                    target_y = (accel_y * self.mouse_sensitivity + 0.5) * self.hScr
                    target_x = np.clip(target_x, 0, self.wScr)
                    target_y = np.clip(target_y, 0, self.hScr)
                    
                    move_dist = math.hypot(target_x - self.plocX, target_y - self.plocY)
                    if move_dist < self.deadzone:
                        target_x, target_y = self.plocX, self.plocY
                        smooth_val = 10
                    else:
                        smooth_val = max(2.0, 8.0 - (move_dist / 30.0))

                    self.clocX = self.plocX + (target_x - self.plocX) / smooth_val
                    self.clocY = self.plocY + (target_y - self.plocY) / smooth_val
                    
                    try: pyautogui.moveTo(self.clocX, self.clocY)
                    except: pass
                    self.plocX, self.plocY = self.clocX, self.clocY

                    # --- Click & Drag (Pinch) ---
                    palm_ref = math.hypot(lmList[0][1]-lmList[9][1], lmList[0][2]-lmList[9][2])
                    dist = math.hypot(x1-x2, y1-y2)
                    threshold = palm_ref * 0.18
                    
                    # Görsel
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.circle(frame, (cx, cy), 5, (200, 200, 200), cv2.FILLED)

                    if dist < threshold:
                        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                        if not self.pinch_active:
                            pyautogui.mouseDown()
                            self.pinch_active = True
                            self.is_dragging = True
                            info_text = "TIK / TUT"
                    else:
                        if dist > (threshold * 1.3):
                            if self.pinch_active:
                                pyautogui.mouseUp()
                                self.pinch_active = False
                                self.is_dragging = False
                                info_text = "BIRAKTI"
                    
                    # İşaretçi Görseli
                    cv2.circle(frame, (x1, y1), 8, (0, 255, 0), cv2.FILLED)

        return frame, info_text

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow Scroll OS")
        self.root.geometry("850x700")
        self.root.configure(bg="#222")
        self.backend = HandEyeBackend("ben.jpg")
        self.cap = None
        self.is_running = False
        
        tk.Label(root, text="Yumruk: YUKARI | Açık El: AŞAĞI | İşaret: MOUSE", bg="#222", fg="#0ff", font=("Arial", 14)).pack(pady=10)
        self.vid = tk.Label(root, bg="black", bd=2, relief="solid")
        self.vid.pack(pady=5)
        
        ctl_frm = tk.Frame(root, bg="#222", pady=10)
        ctl_frm.pack(fill="x", padx=20)
        
        tk.Button(ctl_frm, text="BAŞLAT", bg="#006400", fg="white", width=15, command=self.start).grid(row=0, column=0, padx=10)
        tk.Button(ctl_frm, text="GÖZ KALİBRE", bg="#ff8c00", fg="white", width=15, command=self.calib).grid(row=0, column=1, padx=10)
        tk.Button(ctl_frm, text="DURDUR", bg="#8b0000", fg="white", width=15, command=self.stop).grid(row=0, column=2, padx=10)
        
        self.lbl = tk.Label(root, text="Sistem Hazır", bg="#333", fg="cyan", anchor="w")
        self.lbl.pack(side="bottom", fill="x")

    def calib(self): self.backend.calibrate_start()
    def start(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.is_running = True
        self.loop()
    def stop(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.vid.config(image='')
    def loop(self):
        if self.is_running:
            ret, fr = self.cap.read()
            if ret:
                fr, inf = self.backend.process_frame(fr)
                if inf: self.lbl.config(text=inf)
                im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
                imt = ImageTk.PhotoImage(image=im)
                self.vid.imt = imt
                self.vid.config(image=imt)
            self.root.after(1, self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()