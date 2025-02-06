import threading
import asyncio
import rpc
import artwork_server
from monitor import start_monitor

if __name__ == "__main__":
    try:
        thread_rpc = threading.Thread(target=lambda: rpc.main(), daemon=True)
        thread_server = threading.Thread(target=lambda: artwork_server.launch(), daemon=True)
        thread_monitor = threading.Thread(target=lambda: asyncio.run(start_monitor()), daemon=True)

        thread_rpc.start()
        thread_server.start()
        thread_monitor.start()

        thread_rpc.join()
        thread_server.join()
        thread_monitor.join()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        exit(0)
