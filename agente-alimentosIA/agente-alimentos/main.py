# main.py — arranca el agente y elige canal: consola | telegram | sms
import os, time, argparse
from collections import defaultdict, deque
from dotenv import load_dotenv
load_dotenv()
import agente

_ventanas = defaultdict(deque)
LIMITE = int(os.getenv("MAX_MSG_MIN", "10"))

def manejador(chat, texto):  # guardarraíles: rate limit + longitud
    ahora = time.time(); q = _ventanas[chat]
    while q and ahora - q[0] > 60: q.popleft()
    if len(q) >= LIMITE: return "⏳ Demasiadas peticiones. Espera un minuto."
    q.append(ahora)
    if len(texto) > 1500: return "✂️ Mensaje demasiado largo (máx. 1500 caracteres)."
    return agente.responder(chat, texto)

class CanalConsola:
    def escuchar(self, manejador):
        print("🤖 Canal consola. 'salir' para terminar.")
        while True:
            try: texto = input("tú> ").strip()
            except (EOFError, KeyboardInterrupt): break
            if texto.lower() in ("salir", "exit"): break
            if texto: print("🤖", manejador("local", texto))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--canal", choices=["consola", "telegram", "sms"], default="consola")
    canal = p.parse_args().canal
    if canal == "consola":
        return CanalConsola().escuchar(manejador)
    if canal == "sms":
        from canal_sms_sim import CanalSMS
        return CanalSMS().escuchar(manejador)
    token = os.getenv("TELEGRAM_TOKEN")
    if not token: raise SystemExit("❌ Falta TELEGRAM_TOKEN en .env")
    admins = [x.strip() for x in os.getenv("TELEGRAM_ADMINS", "").split(",") if x.strip()]
    if not admins: print("⚠️ TELEGRAM_ADMINS vacío: nadie será autorizado. Escribe al bot y mira la consola.")
    from canal_telegram import CanalTelegram
    CanalTelegram(token, admins).escuchar(manejador)

if __name__ == "__main__":
    main()
