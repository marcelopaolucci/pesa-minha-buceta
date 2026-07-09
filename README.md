# Pesa Minha Buceta

Bot de gamificação para grupos do Telegram. Usuários fazem uma pesagem diária que rende peso fictício, acumulam ranking e competem entre grupos — mecânica simples, projetada para retenção.

**Bot:** [@PesaMinhaBuceta2Bot](https://t.me/PesaMinhaBuceta2Bot)

## Números

*(julho/2026, produção)*

| Métrica | Valor |
|---|---|
| Grupos ativos | 800+ |
| Usuários registrados | 22.000+ |
| Pesagens processadas | 150.000+ |
| Stickiness (DAU/MAU) | ~27% |

Operação em uma única VPS com SQLite — custo de infraestrutura próximo de zero.

## Mecânica

- **Pesagem diária** — roll aleatório com tiers de raridade, multiplicador de streak e sistema de pity (garante recompensa após sequência de rolls ruins)
- **Duelos e doações** — transferência de peso entre usuários, com stake
- **Rankings** — por grupo (temporada e histórico) e global unificado: o peso global de um usuário é a sua melhor temporada entre todos os grupos
- **Temporadas trimestrais** — reset com Hall da Fama permanente por grupo
- **Conquistas** — 44 medalhas em 8 categorias, desbloqueio automático por evento
- **Sorteio diário** — premiação entre os usuários ativos de cada grupo

## Decisões de design

- **Reset de temporada lazy** — a primeira pesagem da nova temporada finaliza a anterior; nenhum cron job tocando o banco
- **Ranking global derivado** — calculado por agregação do estado local (`MAX` por usuário), sem estado duplicado para manter em sincronia
- **Pesagem em transação atômica única** — roll, streak, pity e persistência num commit só
- **SQLite em WAL** com conexão singleton e lock re-entrante por task — concorrência async sem deadlock em conexões aninhadas
- **Textos e templates isolados** da lógica (`utils/messages.py`) — handlers nunca contêm copy

## Stack

Python 3.12 · [aiogram](https://github.com/aiogram/aiogram) 3.x · SQLite (aiosqlite, WAL) · systemd · GitHub Actions (CI/CD)

```
database/     camada de dados (facade + submódulos)
handlers/     um módulo por comando
utils/        RNG, formatação, teclados, textos
services/     cache e agregação de perfil
middleware/   rastreamento de atividade
```

## Self-hosting

```bash
git clone https://github.com/marcelopaolucci/PesaMinhaBuceta.git
cd PesaMinhaBuceta
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha BOT_TOKEN e demais variáveis
python bot.py
```

## Licença

Projeto pessoal. Uso livre para fins não comerciais.
