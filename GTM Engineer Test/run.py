import subprocess
import sys
import time

print("🚀 Bootstrapping Catalyst GTM Platform...")

# 1. Spin up the background telemetry worker process
worker_process = subprocess.Popen([sys.executable, "pipeline/worker.py"])
print("🤖 Background time-series worker initiated.")

# 2. Execute the Streamlit UI as a python module (Fixes the FileNotFoundError)
try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/dashboard.py"])
except KeyboardInterrupt:
    pass
finally:
    # 3. Clean up
    print("\n🛑 Catching shutdown signal. Terminating background worker...")
    worker_process.terminate()
    worker_process.wait()
    print("🧹 System successfully halted clean.")