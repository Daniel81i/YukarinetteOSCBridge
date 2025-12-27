import winreg
import requests
import logging

class YukariAPI:
    def __init__(self, config):
        self.config = config
        self.base_url = self._get_base_url()

    def _get_base_url(self):
        hive = winreg.HKEY_CURRENT_USER
        path = self.config["REGISTRY_PATH"]
        name = self.config["REGISTRY_VALUE_HTTP"]

        with winreg.OpenKey(hive, path) as key:
            port, _ = winreg.QueryValueEx(key, name)

        return f"http://127.0.0.1:{port}"

    async def set_mute(self, value):
        try:
            r = requests.post(f"{self.base_url}/api/mute", json={"mute": value}, timeout=1)
            return r.status_code == 200
        except:
            logging.error("Mute API failed")
            return False

    async def set_langid(self, value):
        try:
            r = requests.post(f"{self.base_url}/api/langid", json={"langid": value}, timeout=1)
            return r.status_code == 200
        except:
            logging.error("LangID API failed")
            return False
