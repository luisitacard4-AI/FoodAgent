# canal_telegram.py — adaptador (long polling, sin servidor). NO contiene lógica de IA.
import time, requests

class CanalTelegram:
    def __init__(self, token: str, admins: list):
        self.api = f"https://api.telegram.org/bot{token}"
        self.admins = set(str(a) for a in admins if a)

    def enviar(self, chat, texto: str):
        texto = str(texto) or "(vacío)"
        for i in range(0, len(texto), 4000):  # límite Telegram: 4096
            try:
                requests.post(f"{self.api}/sendMessage",
                              json={"chat_id": chat, "text": texto[i:i+4000]}, timeout=20)
            except requests.RequestException as e:
                print("⚠️ no se pudo enviar:", e)

    def escuchar(self, manejador):
        requests.get(f"{self.api}/deleteWebhook", timeout=15)
        offset = None
        print("📡 Escuchando Telegram… (Ctrl+C para salir)")
        while True:
            try:
                r = requests.get(f"{self.api}/getUpdates",
                                 params={"timeout": 30, "offset": offset}, timeout=40)
                datos = r.json()
                if not datos.get("ok"):
                    print("⚠️ respuesta no ok:", datos); time.sleep(3); continue
                for u in datos["result"]:
                    offset = u["update_id"] + 1
                    m = u.get("message") or {}
                    texto, chat = m.get("text"), (m.get("chat") or {}).get("id")
                    if not texto or chat is None: continue
                    if self.admins and str(chat) not in self.admins:
                        print(f"⛔ BLOQUEADO chat_id={chat} → {texto[:40]}"); continue
                    self.enviar(chat, manejador(str(chat), texto))
            except requests.RequestException as e:
                print("🌐 red:", e); time.sleep(5)
            except KeyboardInterrupt:
                print("\n👋 parado"); break
