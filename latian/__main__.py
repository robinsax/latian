import sys
import asyncio

sys.path.insert(0, '.')

from latian import Exit, initialize

def main():
    try:
        asyncio.run(initialize().run())
    except (KeyboardInterrupt, Exit):
        pass

main()