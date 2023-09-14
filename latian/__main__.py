import sys

sys.path.insert(0, '.')

from latian import initialize

try:
    initialize().run()
except KeyboardInterrupt:
    print('exit')
