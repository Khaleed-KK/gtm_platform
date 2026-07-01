import time
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from pipeline.ingestion import run_pipeline

# Targets the exact, official public handle for HubSpot
TARGET_CLIENT_CHANNEL = "@HubSpot-CRM"

if __name__ == "__main__":
    print("🤖 Self-Sustaining Catalyst Background Worker Activated...")
    print(f"Tracking metrics over time for: {TARGET_CLIENT_CHANNEL}")
    print("Press Ctrl+C to safely stop the daemon loop.")

    while True:
        try:
            resolved_name = run_pipeline(target_identifier=TARGET_CLIENT_CHANNEL)
            if resolved_name:
                print(f"✅ Metrics ledger snapshot updated successfully for {resolved_name}.")
            else:
                print("⚠️ Pipeline execution cycled with no data returned.")

            print("💤 Sleeping for 60 seconds...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n🛑 Worker safely shut down.")
            break
        except Exception as e:
            print(f"❌ Worker Core Error: {e}")
            time.sleep(10)