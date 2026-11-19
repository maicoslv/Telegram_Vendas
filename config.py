import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
VIP_GROUP_ID = int(os.getenv("VIP_GROUP_ID", "0"))

# Regras de negócio dos planos
VALOR_BASE_MENSAL = 50.00
PLANOS = {
    "teste_1min": {
        "nome": "Plano Teste (1 minuto)",
        "valor": 1.00,
        "dias": 0,
        "minutos": 1,
        "desconto": "TESTE"
    },
    "mensal": {
        "nome": "Plano Mensal (30 dias)",
        "valor": VALOR_BASE_MENSAL,
        "dias": 30,
        "minutos": 0,
        "desconto": "0%"
    },
    "trimestral": {
        "nome": "Plano Trimestral (90 dias)",
        "valor": round((VALOR_BASE_MENSAL * 3) * 0.90, 2),
        "dias": 90,
        "minutos": 0,
        "desconto": "10% OFF"
    },
    "semestral": {
        "nome": "Plano Semestral (180 dias)",
        "valor": round((VALOR_BASE_MENSAL * 6) * 0.85, 2),
        "dias": 180,
        "minutos": 0,
        "desconto": "15% OFF"
    }
}