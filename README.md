# Agente IA de Ingeniería de Alimentos

Agente por mensajería (Telegram / consola / SMS simulado) que ayuda en innovación de productos, selección de materias primas y optimización de procesos. Coste: 0 €. Datos sintéticos.

## Arranque en 5 pasos
1. `python -m venv .venv` y activar (`source .venv/bin/activate`; en Windows `.venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. `cp .env.example .env` y poner `CEREBRO=ollama` (tras `ollama pull llama3.2:3b`)
4. `python main.py` (consola) o `python main.py --canal telegram` (con token de @BotFather)
5. `python tests/evaluar.py` para medir el agente con los 3 cerebros (cambia `CEREBRO` en `.env`)

## Herramientas
`calculadora` · `comparar_materias` · `formular` · `letalidad` · `rendimiento` · `buscar_apuntes` · `hora`

## Contrato de canal
Todo canal implementa `escuchar(manejador)` y `enviar(chat, texto)`; el agente no sabe por cuál habla.

## Seguridad
Token en `.env` (nunca en Git), allowlist de chats, AST en la calculadora, límites de pasos/caracteres, rate limit, `/reset` borra el historial.
