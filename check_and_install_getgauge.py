import subprocess
import sys
import os
import util

try:
    import getgauge
except:
    python_plugin_version = util.get_version()
    getgauge_with_version = "getgauge"
    if "nightly" in python_plugin_version:
        version = python_plugin_version.replace('nightly','').replace('-','')
        getgauge_with_version += "==" + version[:6] + "dev" + version[6:]
        subprocess.call([sys.executable, "-m", "pip", "install", "--pre", getgauge_with_version],stdout=open(os.devnull, 'wb'))
    else:    
        subprocess.call([sys.executable, "-m", "pip", "install",getgauge_with_version],stdout=open(os.devnull, 'wb'))