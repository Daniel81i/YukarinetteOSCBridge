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

    # ---------------------------
    # Mute
    # ---------------------------
    async def set_mute(self, value):
        try:
            if value == 1:
                url = self.base_url + self.config["YUKACONE_MUTE_ON"]
            else:
                url = self.base_url + self.config["YUKACONE_MUTE_OFF"]
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"[API REQUEST] POST {url}")

            r = requests.post(url, timeout=1)
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                body = r.text
                if len(body) > 200:
                    body = body[:200] + "...(truncated)"
                logging.debug(f"[API RESPONSE] status={r.status_code}, body={body}")
            return r.status_code == 200

        except Exception as e:
            logging.error(f"Mute API failed: {e}")
            return False

    # ---------------------------
    # LangID
    # ---------------------------
    def _build_langid_url(self, item_no):
        presets = self.config["LANG_PRESETS"]
        preset = next((p for p in presets if p["ItemNo"] == item_no), None)
        if not preset:
            return None

        base = self.config["YUKACONE_LANGID_BASE"]
        lang = preset["language"]
        engine = preset["engine"]

        return f"{self.base_url}{base}&language={lang}&engine={engine}"

    async def set_langid(self, item_no):
        try:
            url = self._build_langid_url(item_no)
            if not url:
                logging.error("LangID preset not found")
                return False
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"[API REQUEST] POST {url}")

            r = requests.post(url, timeout=1)
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                body = r.text
                if len(body) > 200:
                    body = body[:200] + "...(truncated)"
                logging.debug(f"[API RESPONSE] status={r.status_code}, body={body}")
            return r.status_code == 200

        except Exception as e:
            logging.error(f"LangID API failed: {e}")
            return False
