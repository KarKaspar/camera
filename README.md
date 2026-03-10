# camera
Karl Kaspar Mahoni

See on töö on tehtud viruaalses masinas, windows termnaliga.

Lihtne Python rakendus, mis avab kaamera ja tuvastab objekte reaalajas YOLOv11 abil.
Nõuded

Python 3.8+
Veebikaamera (sisseehitatud või USB)


# 1. Virtuaalkeskkond
py -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Sõltuvused
pip install opencv-python ultralytics numpy

# 3. Käivita
py camera.py

pip install opencv-python ultralytics numpy
Käivitamine
py camera.py

Esimesel käivitusel laaditakse YOLOv11 mudel automaatselt alla (~6 MB).

Klahvid
KlahvTegevusSPACESalvesta kaader (salvestused/ kausta)SLülita AI sisse / väljaQ / ESCVälju
Seadistamine
Muuda faili ülaosas olevaid konstante:
pythonCAMERA_INDEX   = 0          # 0 = sisseehitatud, 1 = USB kaamera
FRAME_WIDTH    = 1280
FRAME_HEIGHT   = 720
CONF_THRESHOLD = 0.45       # tuvastuse usaldusnivoo (0.0–1.0)
YOLO_MODEL     = "yolo11n.pt"  # n=kiire, s/m/l/x=täpsem
Väljund
Iga SPACE vajutus loob kaks faili kausta salvestused/:
20250310_143022_originaal.jpg   ← töötlemata kaader
20250310_143022_yolo.jpg        ← YOLO kastide ja siltidega
