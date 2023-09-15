import sys
import asyncio

sys.path.insert(0, '.')

from latian import Exit, create_application

def main():
    application = create_application()
    try:
        asyncio.run(application())
    except (KeyboardInterrupt, Exit):
        pass

main()
