# camera
Karl Kaspar Mahoni

See on töö on tehtud viruaalses masinas, windows termnaliga.

Lihtne Python rakendus, mis avab kaamera ja tuvastab objekte reaalajas YOLOv11 abil.
Nõuded

Python 3.8+
Veebikaamera (sisseehitatud või USB)

Installimine
bashgit clone https://github.com/sinu-kasutajanimi/camera-ai-app
cd camera-ai-app

python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate       # Linux / Mac

pip install opencv-python ultralytics numpy
Käivitamine
bashpython camera_ai_app.py

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
