"""
Kaamera + AI reaalajas töötlus
==============================
Kasutab OpenCV kaamerat ja YOLOv8 objektide tuvastamiseks.

Nõuded (installi enne käivitamist):
    pip install opencv-python ultralytics numpy pillow

Käivitamine:
    python camera_ai_app.py

Klahvid töötamise ajal:
    SPACE  - salvesta hetkel töödeldud pilt
    S      - lülita AI töötlus sisse/välja
    Q/ESC  - välju programmist
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime
from pathlib import Path

# ── Seaded ──────────────────────────────────────────────────────────────────
CAMERA_INDEX   = 0          # 0 = sisseehitatud kaamera, 1 = väliskaamera jne.
FRAME_WIDTH    = 1280
FRAME_HEIGHT   = 720
SAVE_DIR       = "salvestused"   # kaust, kuhu pildid salvestatakse
YOLO_MODEL     = "yolo11n.pt"    # väike kiire mudel (~6 MB, alla laetakse automaatselt)
CONF_THRESHOLD = 0.45            # minimaalne usaldusnivoo
# ────────────────────────────────────────────────────────────────────────────


def load_yolo():
    """Laadi YOLOv8 mudel. Esimesel käivitusel laaditakse alla automaatselt."""
    try:
        from ultralytics import YOLO
        print("[INFO] Laen YOLO mudelit …")
        model = YOLO(YOLO_MODEL)
        print("[INFO] YOLO mudel laetud!")
        return model
    except ImportError:
        print("[VIGA] ultralytics pole installitud.")
        print("       Käivita:  pip install ultralytics")
        return None
    except Exception as e:
        print(f"[VIGA] Mudeli laadimine ebaõnnestus: {e}")
        return None


def process_frame_yolo(frame, model, conf=CONF_THRESHOLD):
    """
    Käivita YOLO järeldus ühel kaadril.
    Tagastab annoteeritud kaadri + tuvastuste nimekirja.
    """
    results = model(frame, conf=conf, verbose=False)[0]
    annotated = results.plot()          # YOLO joonistab kastid + sildid ise

    detections = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        label  = model.names[cls_id]
        conf_v = float(box.conf[0])
        detections.append({"label": label, "confidence": conf_v})

    return annotated, detections


def draw_overlay(frame, detections, ai_enabled, fps, saved_msg):
    """Joonista info-riba kaadri peale."""
    h, w = frame.shape[:2]

    # Taust ülareas
    cv2.rectangle(frame, (0, 0), (w, 45), (20, 20, 20), -1)

    # FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 120), 2)

    # AI olek
    ai_txt   = "AI: SEES" if ai_enabled else "AI: VALJAS"
    ai_color = (0, 255, 120) if ai_enabled else (60, 60, 200)
    cv2.putText(frame, ai_txt, (150, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, ai_color, 2)

    # Tuvastuste arv
    cv2.putText(frame, f"Objektid: {len(detections)}", (330, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 220, 0), 2)

    # Salvestusteade
    if saved_msg:
        cv2.putText(frame, saved_msg, (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

    # Klahvid (alumine riba)
    hint = "SPACE=salvesta  S=lylita AI  Q/ESC=välju"
    cv2.putText(frame, hint, (w - 520, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 160, 160), 1)

    return frame


def save_frame(frame_raw, frame_processed, save_dir):
    """Salvesta nii originaal- kui töödeldud kaader."""
    os.makedirs(save_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:22]
    p_raw  = os.path.join(save_dir, f"{ts}_originaal.jpg")
    p_proc = os.path.join(save_dir, f"{ts}_yolo.jpg")
    cv2.imwrite(p_raw,  frame_raw)
    cv2.imwrite(p_proc, frame_processed)
    return p_proc


def main():
    # ── Loo salvestuste kaust ──────────────────────────────────────────────
    os.makedirs(SAVE_DIR, exist_ok=True)

    # ── Laadi YOLO ────────────────────────────────────────────────────────
    model = load_yolo()

    # ── Ava kaamera ───────────────────────────────────────────────────────
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[VIGA] Kaamerat ei leitud (indeks {CAMERA_INDEX}).")
        print("       Proovi muuta CAMERA_INDEX väärtust (0, 1, 2 …)")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[INFO] Kaamera avatud  {actual_w}×{actual_h}")
    print("[INFO] Klahvid:  SPACE=salvesta  S=AI sisse/välja  Q/ESC=välju\n")

    # ── Muutujad ──────────────────────────────────────────────────────────
    ai_enabled  = model is not None
    fps_prev    = time.time()
    fps_display = 0.0
    saved_msg   = ""
    saved_until = 0.0
    frame_count = 0

    # ── Peaahel ───────────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[VIGA] Kaadri lugemine ebaõnnestus.")
            break

        frame_count += 1
        now = time.time()

        # FPS arvutus (liugkeskmine)
        elapsed = now - fps_prev
        if elapsed > 0:
            fps_display = 0.8 * fps_display + 0.2 * (1.0 / elapsed)
        fps_prev = now

        frame_raw = frame.copy()

        # ── AI töötlus ────────────────────────────────────────────────────
        if ai_enabled and model is not None:
            processed, detections = process_frame_yolo(frame, model)
        else:
            processed  = frame.copy()
            detections = []

        # ── Salvestusteade ────────────────────────────────────────────────
        if now < saved_until:
            pass   # teade on veel aktiivne
        else:
            saved_msg = ""

        # ── Overlay ───────────────────────────────────────────────────────
        display = draw_overlay(processed, detections, ai_enabled,
                               fps_display, saved_msg)

        # ── Kuva ──────────────────────────────────────────────────────────
        cv2.imshow("Kaamera + YOLO AI  (Q=välju)", display)

        # ── Klahvid ───────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key in (ord('q'), 27):           # Q või ESC → välju
            break

        elif key == ord('s'):               # S → lülita AI
            if model is None:
                print("[HOIATUS] Mudel pole laetud, AI ei saa sisse lülitada.")
            else:
                ai_enabled = not ai_enabled
                state = "SEES" if ai_enabled else "VÄLJAS"
                print(f"[INFO] AI töötlus: {state}")

        elif key == ord(' '):               # SPACE → salvesta
            path = save_frame(frame_raw, display, SAVE_DIR)
            saved_msg   = f"Salvestatud: {os.path.basename(path)}"
            saved_until = now + 2.5
            print(f"[INFO] Salvestatud → {path}")

    # ── Koristus ──────────────────────────────────────────────────────────
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[INFO] Programm lõpetatud. Salvestused: ./{SAVE_DIR}/")


if __name__ == "__main__":
    main()
