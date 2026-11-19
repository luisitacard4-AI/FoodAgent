# cerebro.py — el modelo es una pieza intercambiable (CEREBRO=reglas|ollama|api)
import os, requests

class CerebroReglas:
    """Línea base sin IA, para comparar en la evaluación."""
    nombre = "reglas"
    def pensar(self, mensajes):
        return '{"accion":"final","texto":"No tengo modelo activado. Usa /ayuda."}'

class CerebroOllama:
    nombre = "ollama"
    def __init__(self):
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.modelo = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    def pensar(self, mensajes):
        r = requests.post(f"{self.url}/api/chat", timeout=180, json={
            "model": self.modelo, "messages": mensajes, "stream": False,
            "options": {"temperature": 0.2, "num_predict": 350}})
        r.raise_for_status()
        return r.json()["message"]["content"]

class CerebroAPI:
    """Cualquier endpoint compatible con OpenAI (Groq, OpenRouter, Mistral, Google…)."""
    nombre = "api"
    def __init__(self):
        self.url, self.key = os.getenv("API_URL"), os.getenv("API_KEY")
        self.modelo = os.getenv("API_MODEL")
    def pensar(self, mensajes):
        r = requests.post(self.url, timeout=60, headers={"Authorization": f"Bearer {self.key}"},
                          json={"model": self.modelo, "messages": mensajes, "temperature": 0.2})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

def crear_cerebro():
    tipo = os.getenv("CEREBRO", "reglas").lower()
    if tipo == "ollama": return CerebroOllama()
    if tipo == "api": return CerebroAPI()
    return CerebroReglas()
