# canal_sms_sim.py — SMS simulado: muestra límites y coste reales del canal
LIMITE = 160              # GSM-7. Con acentos/emoji (UCS-2) baja a 70.
PRECIO_ORIENTATIVO = 0.07 # €/segmento, solo para el ejercicio

class CanalSMS:
    def __init__(self): self.coste = 0.0
    def enviar(self, chat, texto):
        segs = [texto[i:i+LIMITE] for i in range(0, len(texto), LIMITE)] or [""]
        self.coste += len(segs) * PRECIO_ORIENTATIVO
        print(f"\n📩 SMS a {chat} — {len(segs)} segmento(s) — acumulado {self.coste:.2f} €")
        for i, s in enumerate(segs, 1): print(f"  [{i}/{len(segs)}] {s}")
    def escuchar(self, manejador):
        print("📱 SMS simulado. 'salir' para terminar.")
        while True:
            t = input("SMS> ").strip()
            if t.lower() == "salir": break
            if t: self.enviar("+570000000000", manejador("sms", t))
