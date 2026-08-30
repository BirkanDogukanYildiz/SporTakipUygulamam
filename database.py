import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "veriler.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS olcumler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT NOT NULL,
            kilo REAL,
            yag_orani REAL,
            kas_orani REAL,
            bel_cevresi REAL,
            gogus_cevresi REAL,
            kol_cevresi REAL,
            not_ TEXT
        )
    """)
    conn.commit()
    conn.close()


def kayit_ekle(tarih, kilo, yag_orani, kas_orani, bel_cevresi, gogus_cevresi, kol_cevresi, not_):
    conn = get_connection()
    conn.execute(
        """INSERT INTO olcumler
           (tarih, kilo, yag_orani, kas_orani, bel_cevresi, gogus_cevresi, kol_cevresi, not_)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (tarih, kilo, yag_orani, kas_orani, bel_cevresi, gogus_cevresi, kol_cevresi, not_),
    )
    conn.commit()
    conn.close()


def kayit_sil(kayit_id):
    conn = get_connection()
    conn.execute("DELETE FROM olcumler WHERE id = ?", (kayit_id,))
    conn.commit()
    conn.close()


def tum_kayitlari_getir():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM olcumler ORDER BY tarih ASC").fetchall()
    conn.close()
    return rows
