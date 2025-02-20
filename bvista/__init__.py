from .notebook_integration import show  # ✅ Keep `show` available


from .server_manager import start_backend

# Start backend automatically on import
start_backend()
