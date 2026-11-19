# herramientas.py — caja de herramientas del agente de Ingeniería de Alimentos
# Datos SINTÉTICOS aproximados, solo para fines académicos.
import ast, operator, datetime, os, glob

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
        ast.USub: operator.neg, ast.UAdd: operator.pos}

def _evaluar(n):  # NUNCA eval(): se valida el AST
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
        return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
        if isinstance(n.op, ast.Pow) and abs(_evaluar(n.right)) > 100:
            raise ValueError("exponente demasiado grande")
        return _OPS[type(n.op)](_evaluar(n.left), _evaluar(n.right))
    if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
        return _OPS[type(n.op)](_evaluar(n.operand))
    raise ValueError("solo aritmética simple")

def calculadora(expresion: str) -> str:
    if len(expresion) > 120:
        raise ValueError("expresión demasiado larga")
    return str(round(_evaluar(ast.parse(expresion, mode="eval").body), 4))

def hora() -> str:
    return "Hora del servidor: " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# ---- Base sintética por 100 g: prot (g), grasa (g), azuc (g), kcal, costo (USD/kg),
# ---- alerg (1 = alérgeno mayor), sost (1-5, mayor = mejor), disp (1-5)
ING = {
    "proteina de guisante": dict(prot=80, grasa=6,  azuc=1,  kcal=370, costo=5.5,  alerg=0, sost=5, disp=4),
    "proteina de soya":     dict(prot=85, grasa=4,  azuc=2,  kcal=360, costo=4.0,  alerg=1, sost=3, disp=5),
    "proteina de suero":    dict(prot=80, grasa=6,  azuc=6,  kcal=390, costo=12.0, alerg=1, sost=2, disp=5),
    "haba":                 dict(prot=26, grasa=1.5,azuc=3,  kcal=340, costo=2.2,  alerg=0, sost=5, disp=3),
    "avena":                dict(prot=13, grasa=7,  azuc=1,  kcal=380, costo=1.8,  alerg=0, sost=4, disp=5),
    "quinua":               dict(prot=14, grasa=6,  azuc=2,  kcal=370, costo=4.5,  alerg=0, sost=4, disp=3),
    "almendra":             dict(prot=21, grasa=50, azuc=4,  kcal=580, costo=11.0, alerg=1, sost=2, disp=4),
    "azucar":               dict(prot=0,  grasa=0,  azuc=100,kcal=387, costo=1.0,  alerg=0, sost=3, disp=5),
    "miel":                 dict(prot=0.3,grasa=0,  azuc=82, kcal=304, costo=7.0,  alerg=0, sost=3, disp=4),
    "aceite de girasol":    dict(prot=0,  grasa=100,azuc=0,  kcal=884, costo=2.5,  alerg=0, sost=3, disp=5),
}
PRIORIDADES = {  # pesos por criterio (se normaliza cada columna a 0-1)
    "proteina":       dict(prot=.6, costo=.2, sost=.1, disp=.1),
    "costo":          dict(prot=.2, costo=.6, sost=.1, disp=.1),
    "sostenibilidad": dict(prot=.2, costo=.1, sost=.6, disp=.1),
    "balanceado":     dict(prot=.35, costo=.25, sost=.2, disp=.2),
}

def comparar_materias(prioridad: str = "balanceado", sin_alergenos: str = "no") -> str:
    """Ranking multicriterio de materias primas (selección óptima)."""
    p = PRIORIDADES.get(prioridad.lower().strip())
    if not p:
        return f"ERROR: prioridad inválida. Usa: {', '.join(PRIORIDADES)}"
    ev = sin_alergenos.lower().strip() in ("si", "sí", "true", "1")
    c = {k: [v[k] for v in ING.values()] for k in ("prot", "costo", "sost", "disp")}
    def norm(k, x, inv=False):
        lo, hi = min(c[k]), max(c[k]); r = (x - lo) / (hi - lo)
        return 1 - r if inv else r
    fila = []
    for n, v in ING.items():
        if ev and v["alerg"]: continue
        if v["prot"] < 20: continue      # el ranking compara fuentes de proteína
        s = (p["prot"]*norm("prot", v["prot"]) + p["costo"]*norm("costo", v["costo"], True)
             + p["sost"]*norm("sost", v["sost"]) + p["disp"]*norm("disp", v["disp"]))
        fila.append((round(s*100), n, v["prot"], v["costo"]))
    fila.sort(reverse=True)
    top = "; ".join(f"{i}. {n} (puntaje {s}, {pr} g prot/100 g, {co} USD/kg)"
                    for i, (s, n, pr, co) in enumerate(fila[:3], 1))
    return f"Top 3 con prioridad '{prioridad}'" + (" y sin alérgenos" if ev else "") + f": {top}"

def formular(mezcla: str) -> str:
    """mezcla = 'avena=60,haba=30,miel=10' (gramos por cada 100 g). Calcula aporte y costo."""
    tot = dict(prot=0, grasa=0, azuc=0, kcal=0, costo=0); gramos = 0
    for par in mezcla.split(","):
        nombre, _, g = par.partition("=")
        nombre, g = nombre.strip().lower(), float(g)
        if nombre not in ING:
            raise ValueError(f"ingrediente desconocido '{nombre}'. Disponibles: {', '.join(ING)}")
        gramos += g
        for k in ("prot", "grasa", "azuc", "kcal"):
            tot[k] += ING[nombre][k] * g / 100
        tot["costo"] += ING[nombre]["costo"] * g / 1000
    return (f"Por {gramos:g} g de mezcla: proteína {tot['prot']:.1f} g, grasa {tot['grasa']:.1f} g, "
            f"azúcares {tot['azuc']:.1f} g, {tot['kcal']:.0f} kcal; costo {tot['costo']*10:.2f} USD/kg de mezcla")

def letalidad(temp_c: float, minutos: float, z: float = 10, d_ref: float = 0.2) -> str:
    """Valor F a 121.1 °C: F = t · 10^((T-121.1)/z). Reducciones log = F / D."""
    f = float(minutos) * 10 ** ((float(temp_c) - 121.1) / float(z))
    return (f"F{121.1} = {f:.2f} min (T={temp_c} °C, t={minutos} min, z={z}); "
            f"reducción ≈ {f/float(d_ref):.1f} ciclos log con D={d_ref} min")

def rendimiento(entrada_kg: float, salida_kg: float, costo_kg: float = 0) -> str:
    e, s = float(entrada_kg), float(salida_kg)
    if e <= 0: raise ValueError("la entrada debe ser > 0")
    merma = e - s
    return (f"Rendimiento {s/e*100:.1f} %, merma {merma:.2f} kg ({merma/e*100:.1f} %), "
            f"pérdida económica {merma*float(costo_kg):.2f} USD")

def buscar_apuntes(consulta: str) -> str:
    palabras = [p for p in consulta.lower().split() if len(p) > 3]
    mejores = []
    for ruta in glob.glob(os.path.join(os.path.dirname(__file__), "apuntes", "*.md")):
        with open(ruta, encoding="utf-8") as f:
            for parrafo in f.read().split("\n\n"):
                p = parrafo.strip()
                if len(p) < 40: continue
                pts = sum(1 for w in palabras if w in p.lower())
                if pts: mejores.append((pts, os.path.basename(ruta), p))
    mejores.sort(reverse=True)
    if not mejores: return "No hay nada sobre eso en los apuntes."
    return "\n\n".join(f"[{a}] {t[:400]}" for _, a, t in mejores[:3])

HERRAMIENTAS = {
    "hora": {"fn": hora, "desc": "Fecha y hora actuales", "args": {}},
    "calculadora": {"fn": calculadora, "desc": "Aritmética exacta (+ - * / % **)",
                    "args": {"expresion": "str, ej. '240*0.18'"}},
    "comparar_materias": {"fn": comparar_materias,
        "desc": "Ranking de fuentes de proteína para elegir materia prima",
        "args": {"prioridad": "proteina|costo|sostenibilidad|balanceado", "sin_alergenos": "si|no"}},
    "formular": {"fn": formular, "desc": "Aporte nutricional y costo de una formulación",
                 "args": {"mezcla": "str, ej. 'avena=60,haba=30,miel=10' (g por 100 g)"}},
    "letalidad": {"fn": letalidad, "desc": "Valor F y reducción logarítmica de un tratamiento térmico",
                  "args": {"temp_c": "num", "minutos": "num", "z": "num, opcional", "d_ref": "num, opcional"}},
    "rendimiento": {"fn": rendimiento, "desc": "Rendimiento, merma y pérdida económica de un proceso",
                    "args": {"entrada_kg": "num", "salida_kg": "num", "costo_kg": "num, opcional"}},
    "buscar_apuntes": {"fn": buscar_apuntes, "desc": "Busca en los apuntes del módulo",
                       "args": {"consulta": "str, palabras clave"}},
}

def catalogo() -> str:
    return "\n".join(f'- {n}: {h["desc"]} | args: {{{", ".join(f"""\"{k}\":<{v}>""" for k, v in h["args"].items())}}}'
                     for n, h in HERRAMIENTAS.items())

def ejecutar(nombre: str, args: dict) -> str:
    """Ejecuta una herramienta y SIEMPRE devuelve texto (también si hay error)."""
    if nombre not in HERRAMIENTAS:
        return f"ERROR: no existe la herramienta '{nombre}'"
    try:
        return str(HERRAMIENTAS[nombre]["fn"](**(args or {})))[:1500]
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"
