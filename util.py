from subprocess import Popen, PIPE
import json

def get_version():
    proc = Popen(['gauge', '-v', '--machine-readable'], stdout=PIPE, stderr=PIPE)
    out, _ = proc.communicate()
    data = json.loads(str(out.decode()))
    for plugin in data['plugins']:
        if plugin['name'] == 'python':
            return plugin['version']
    return ''