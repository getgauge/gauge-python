import subprocess
import sys
import os

try:
    import getgauge
except:
    subprocess.call([sys.executable, "-m", "pip", "install","getgauge"],stdout=open(os.devnull, 'wb'))