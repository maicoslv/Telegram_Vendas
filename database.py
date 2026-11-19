import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "assinaturas.db"


def inicializar_banco():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assinantes (
                user_id INTEGER PRIMARY KEY,
                nome TEXT,
                plano TEXT,
                data_expiracao TEXT,
                invite_link TEXT,
                ativo INTEGER DEFAULT 1
            )
        """)
        # Garante a coluna caso o banco já tenha sido criado anteriormente
        try:
            conn.execute("ALTER TABLE assinantes ADD COLUMN invite_link TEXT")
        except sqlite3.OperationalError:
            pass


def registrar_assinatura(
    user_id: int,
    nome: str,
    plano: str,
    invite_link: str,
    data_expiracao: datetime
):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO assinantes (user_id, nome, plano, data_expiracao, invite_link, ativo)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                nome = excluded.nome,
                plano = excluded.plano,
                data_expiracao = excluded.data_expiracao,
                invite_link = excluded.invite_link,
                ativo = 1
        """, (user_id, nome, plano, data_expiracao.isoformat(), invite_link))


def obter_nova_expiracao(user_id: int, dias: int = 0, minutos: int = 0) -> datetime:
    agora = datetime.now()
    delta = timedelta(days=dias, minutes=minutos)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT data_expiracao, ativo FROM assinantes WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()

        if row and row[1] == 1:
            exp_atual = datetime.fromisoformat(row[0])
            base = exp_atual if exp_atual > agora else agora
        else:
            base = agora

    return base + delta


def buscar_expirados() -> list[tuple[int, str, str | None]]:
    agora = datetime.now().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT user_id, nome, invite_link FROM assinantes WHERE ativo = 1 AND data_expiracao <= ?",
            (agora,)
        )
        return cursor.fetchall()


def marcar_como_removido(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE assinantes SET ativo = 0 WHERE user_id = ?",
            (user_id,)
        )