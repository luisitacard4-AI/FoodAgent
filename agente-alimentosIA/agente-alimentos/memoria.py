# memoria.py — SQLite: memoria conversacional persistente (borrable con /reset)
import sqlite3, time, os
from contextlib import closing
os.makedirs("datos", exist_ok=True)
DB = os.path.join("datos", "agente.sqlite3")

def _con():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS mensajes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat TEXT NOT NULL, rol TEXT NOT NULL, texto TEXT NOT NULL, ts REAL NOT NULL)""")
    return con

def guardar(chat, rol, texto):
    with closing(_con()) as con:
        con.execute("INSERT INTO mensajes(chat,rol,texto,ts) VALUES(?,?,?,?)",
                    (str(chat), rol, texto[:2000], time.time()))
        con.commit()

def historial(chat, n=6):
    with closing(_con()) as con:
        filas = con.execute("SELECT rol,texto FROM mensajes WHERE chat=? ORDER BY id DESC LIMIT ?",
                            (str(chat), n)).fetchall()
    return [{"role": r, "content": t} for r, t in reversed(filas)]

def borrar(chat):
    with closing(_con()) as con:
        con.execute("DELETE FROM mensajes WHERE chat=?", (str(chat),))
        con.commit()
