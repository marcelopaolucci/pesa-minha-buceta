# Pesa Minha Buceta

Bot de zoeira e gamificação para grupos do Telegram. Usuários pesam a buceta diariamente, acumulam peso fictício e competem em rankings.

## Funcionalidades

- **`/pesar`** — Pesagem diária com sistema de tiers (pífio → sólido → épico → lendário), streak e pity
- **`/duelar`** — Duelo de peso entre usuários com stake de 2.5kg
- **`/doar`** — Transferência de peso entre usuários
- **`/ranking`** — Rankings legado, temporada, semanal e mensal
- **`/perfil`** — Perfil com estatísticas, conquistas e patente
- **Buceta do Dia** — Sorteio diário de usuária ativa com ganho de 7.77kg
- **Conquistas** — Sistema de achievements desbloqueados automaticamente por eventos
- **Temporadas** — Reset trimestral com Hall da Fama por grupo

## Stack

- Python 3.12
- [aiogram](https://github.com/aiogram/aiogram) 3.x
- SQLite + aiosqlite (WAL mode)
- systemd (deploy em VPS)

## Estrutura

```
database/     # camada de dados modular
handlers/     # lógica de cada comando
utils/        # helpers, RNG, formatação, teclados
services/     # cache e perfil
middleware/   # rastreamento de atividade
```

## Self-hosting

```bash
# 1. Clone e crie o venv
git clone https://github.com/marcelopaolucci/PesaMinhaBuceta.git
cd PesaMinhaBuceta
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure o .env
cp .env.example .env
# edite o .env com seu BOT_TOKEN e demais variáveis

# 3. Rode
python bot.py
```

## Deploy

CI/CD via GitHub Actions:

| Branch | Ambiente |
|--------|----------|
| `staging` | `/opt/pmbb/staging/` |
| `main` | `/opt/pmbb/prod/` |

## Licença

Projeto pessoal. Uso livre para fins não comerciais.
