import json
import os
import logging

STATE_FILE = "scan_state.json"
logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self):
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"last_index": 0, "total_scanned": 0}
        return {"last_index": 0, "total_scanned": 0}

    def get_start_index(self):
        return self.state.get("last_index", 0)

    def update_state(self, current_index, scanned_count):
        self.state["last_index"] = current_index
        self.state["total_scanned"] += scanned_count
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f)
        logger.info(f"💾 Hafıza Güncellendi: İndeks {current_index} kaydedildi.")

    def reset_state(self):
        """Liste bittiğinde başa dönmek için"""
        self.state = {"last_index": 0, "total_scanned": self.state.get("total_scanned", 0)}
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f)
        logger.info("♻️ Liste bitti, başa dönülüyor...")
