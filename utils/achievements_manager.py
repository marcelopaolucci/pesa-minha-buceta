from datetime import datetime
from database import (
    register_global_achievement,
    get_global_user_stats,
    get_global_peso_legado_total,
    get_groups_count,
    get_user_name,
    get_total_weighs_from_history,
)
from utils.emojis import Emojis

class AchievementTiers:
    BRONZE = f"{Emojis.MEDALHA_3} Bronze"
    SILVER = f"{Emojis.MEDALHA_2} Prata"
    GOLD = f"{Emojis.MEDALHA_1} Ouro"
    PLATINUM = f"{Emojis.DIAMANTE} Platina"


def _build_achievement_msg(user_name: str, ach: dict) -> str:
    tier_str = ach["tier"]
    parts = tier_str.split("</tg-emoji>")
    tier_emoji = (parts[0] + "</tg-emoji>") if len(parts) >= 2 else tier_str

    return (
        f"<b>CONQUISTA DESBLOQUEADA!</b>\n\n"
        f"{tier_emoji} <b>{ach['name']}</b>\n"
        f"{ach['desc']}\n\n"
        f"Use /conquistas em seus grupos para ver sua coleção completa!"
    )

# Definição Global de Conquistas
ACHIEVEMENTS_DEFS = {
    # --- VOLUME BUCETÔNICO ---
    "first_weigh": {
        "name": "Estreia Patética",
        "desc": "Fez a sua primeira pesagem. A jornada começou!",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.PESO} Assídua"
    },
    "bcto_25": {
        "name": "Peso Mínimo",
        "desc": "Atingiu 25kg. Já dá pra sentir o peso das decisões.",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_50": {
        "name": "Buceta Fraca",
        "desc": "Atingiu 50kg. O asfalto já tá ruidoso...",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_100": {
        "name": "Saiu da Anemia",
        "desc": "Atingiu 100kg. A balança começou a chorar!",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_150": {
        "name": "Estrutura Fraca",
        "desc": "Atingiu 150kg. Já tem gravidade própria.",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_250": {
        "name": "Monstro do Bairro",
        "desc": "Atingiu 250kg. Se pular, o prédio vira um anão!",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_400": {
        "name": "Desastre Natural",
        "desc": "Atingiu 400kg. Mapas começam a marcar sua posição.",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_500": {
        "name": "Aberração da Física",
        "desc": "Atingiu 500kg. Tem seu próprio fuso horário!",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_650": {
        "name": "Buraco Negro Vivo",
        "desc": "Atingiu 650kg. Objetos ao redor começam a orbitar.",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_800": {
        "name": "Fenômeno",
        "desc": "Atingiu 800kg. A luz não escapa mais desse volume!",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },
    "bcto_1000": {
        "name": "Lenda Viva",
        "desc": "Atingiu 1 Tonelada de buceta! O universo bucetônico nunca mais será o mesmo.",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.PESO} Volume Bucetônico"
    },

    # --- PERSISTÊNCIA (STREAK) ---
    "streak_3": {
        "name": "Vício Patético",
        "desc": "Pesou 3 dias seguidos. Já não tem mais volta.",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.TIMER} Persistência"
    },
    "streak_7": {
        "name": "Semana de Merda",
        "desc": "Streak de 7 dias. Uma semana inteira de devoção bucetônica.",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.TIMER} Persistência"
    },
    "streak_30": {
        "name": "Mês de Obsessão",
        "desc": "30 dias seguidos. Comprometimento de atleta olímpico.",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.TIMER} Persistência"
    },
    "streak_100": {
        "name": "Cem Dias de Loucura",
        "desc": "100 dias consecutivos. Isso é uma religião, não um jogo.",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.TIMER} Persistência"
    },

    # --- ASSÍDUA (PESAGENS) ---
    "weigh_10": {
        "name": "Humilhações Contadas",
        "desc": "10 pesagens realizadas. Já faz parte da rotina.",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.PESO} Assídua"
    },
    "weigh_100": {
        "name": "Dedicação Total",
        "desc": "100 pesagens. Isso não é hobby, é estilo de vida.",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.PESO} Assídua"
    },
    "weigh_200": {
        "name": "Vício Declarado",
        "desc": "200 pesagens. A balança já te reconhece pelo cheiro.",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.PESO} Assídua"
    },

    # --- GLADIADORA (DUELOS) ---
    "first_duel": {
        "name": "Primeira Surra",
        "desc": "Participou de um duelo. Sentiu o cheiro da pólvora!",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.ESPADA} Gladiadora (Duelos)"
    },
    "duels_10": {
        "name": "Matador de Bucetas",
        "desc": "Venceu 10 duelos. A raba alheia já conhece sua mão!",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.ESPADA} Gladiadora (Duelos)"
    },
    "duels_25": {
        "name": "Fantasma Matador",
        "desc": "Venceu 25 duelos. Ninguém aceita mais briga contigo!",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.ESPADA} Gladiadora (Duelos)"
    },

    "duels_50": {
        "name": "Açougueiro de Bucetas",
        "desc": "Venceu 50 duelos. Seu nome é sussurrado com medo!",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.ESPADA} Gladiadora (Duelos)"
    },

    # --- FILANTROPA (DOAÇÕES) ---
    "first_donate": {
        "name": "Deu a Buceta",
        "desc": "Fez sua primeira doação. Compartilhando a banha!",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.PRESENTE} Filantropa (Doações)"
    },
    "donated_25": {
        "name": "Bondade em Excesso",
        "desc": "Doou um total de 25kg para os colegas. Alimentando o grupo!",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.CORACAO} Filantropa (Doações)"
    },
    "donated_50": {
        "name": "Filantropia no Sangue",
        "desc": "Doou um total de 50kg. O peso é seu, mas a caridade é nossa!",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.CORACAO} Filantropa (Doações)"
    },
    "donated_100": {
        "name": "Buceta Santa",
        "desc": "Doou 100kg ao total. Canonizada pelo Vaticano Bucetônico.",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.CORACAO} Filantropa (Doações)"
    },

    # --- ABENÇOADA (SORTE) ---
    "bct_dia_1": {
        "name": "Sortuda",
        "desc": "Ganhou a 'Buceta do Dia' uma vez. As estrelas brilharam pra você!",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.COROA} Abençoada (Sorte)"
    },
    "bct_dia_5": {
        "name": "Mascote",
        "desc": "Ganhou a 'Buceta do Dia' 5 vezes. O bot te ama, né?",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.TREVO} Abençoada (Sorte)"
    },
    "bct_dia_10": {
        "name": "Esquema Armado",
        "desc": "Ganhou 10 vezes. É armação! Vou chamar a perícia!",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.TREVO} Abençoada (Sorte)"
    },
    "bct_dia_25": {
        "name": "Marcelo Tem Favoritos",
        "desc": "Ganhou 25 vezes. Você não joga, você é a empresa.",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.TREVO} Abençoada (Sorte)"
    },

    # --- MISTICISMO (HORÁRIOS) ---
    # Bronze (3): expediente, tarde, novela
    "hora_expediente": {
        "name": "Manhã de Merda",
        "desc": "Pesou entre 05:00 e 11:59. A manhã é sua.",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    "hora_tarde": {
        "name": "Aguentando a Tarde",
        "desc": "Pesou entre 15:00 e 17:59. A hora mais longa do dia.",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    "hora_novela": {
        "name": "Noite da Buceta",
        "desc": "Pesou entre 18:00 e 22:59. Do happy hour à novela, a balança não dorme.",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    # Silver (3): noturna, lunch, virada
    "hora_noturna": {
        "name": "Madrugada Desesperada",
        "desc": "Pesou entre 00:00 e 02:59. O mundo dormia, você pesava.",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    "hour_lunch": {
        "name": "Hora do Almoço",
        "desc": "Pesou entre 12:00 e 14:59. Aproveitou bem o intervalo.",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    "hora_virada": {
        "name": "Último Suspiro",
        "desc": "Pesou entre 23:45 e 23:59. No último segundo.",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    # Gold (3): leet, punctual, exata
    "hora_leet": {
        "name": "Hacker de Merda",
        "desc": "Pesou exatamente às 13:37. Você sabe o que fez.",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    "hour_punctual": {
        "name": "Obcecado do Relógio",
        "desc": "Pesou no minuto :59 de qualquer hora. Na pressão do tempo!",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    "hora_exata": {
        "name": "Pontualidade Doentia",
        "desc": "Pesou no minuto :00 exato de qualquer hora. Preciso como um relógio.",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },
    # Platinum (1): pacto
    "hora_pacto": {
        "name": "Ritual Meio Satânico",
        "desc": "Pesou exatamente às 03:33. O capiroto assinou o contrato.",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.LUA} Misticismo (Horários)"
    },

    # --- DOMINAÇÃO GLOBAL (DIVULGAÇÃO) ---
    "nomade_3": {
        "name": "Buceta Sem Lar",
        "desc": "Pesou em 2 grupos diferentes. Espalhando a palavra!",
        "tier": AchievementTiers.BRONZE,
        "category": f"{Emojis.PLANETA} Dominação Global"
    },
    "expansion_10": {
        "name": "Embaixador da Vergonha",
        "desc": "Pesou em 5 grupos diferentes. A fama tá subindo!",
        "tier": AchievementTiers.SILVER,
        "category": f"{Emojis.PLANETA} Dominação Global"
    },
    "queen_puteiros": {
        "name": "Figurinha Repetida",
        "desc": "Pesou em 10 grupos diferentes. Você é presença obrigatória!",
        "tier": AchievementTiers.GOLD,
        "category": f"{Emojis.PLANETA} Dominação Global"
    },
    "monopoly_banha": {
        "name": "Império da Buceta",
        "desc": "Pesou em 20 grupos diferentes. O mundo ficou pequeno pra você!",
        "tier": AchievementTiers.PLATINUM,
        "category": f"{Emojis.PLANETA} Dominação Global"
    }
}

async def check_achievements(user_id, chat_id, event_type, bot=None, context=None):
    """
    Verifica e desbloqueia novas conquistas para o usuário baseado no evento ocorrido.
    Retorna lista de dicionários das conquistas desbloqueadas agora.
    """
    if context is None:
        context = {}

    unlocked_now = []
    stats = await get_global_user_stats(user_id)
    current_weight = await get_global_peso_legado_total(user_id)

    # 1. Checagem de Peso (Sempre checa)
    weight_map = [
        (25000, "bcto_25"), (50000, "bcto_50"), (100000, "bcto_100"),
        (150000, "bcto_150"), (250000, "bcto_250"), (400000, "bcto_400"),
        (500000, "bcto_500"), (650000, "bcto_650"), (800000, "bcto_800"), (1000000, "bcto_1000")
    ]
    for limit, ach_id in weight_map:
        if current_weight >= limit:
            if await register_global_achievement(user_id, ach_id):
                unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])

    # 2. Checagem de Dominação (Chat Count)
    if event_type == "weigh":
        groups_count = await get_groups_count(user_id)
        domination_map = [
            (2, "nomade_3"), (5, "expansion_10"), (10, "queen_puteiros"), (20, "monopoly_banha")
        ]
        for limit, ach_id in domination_map:
            if groups_count >= limit:
                if await register_global_achievement(user_id, ach_id):
                    unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])

        # 3. Misticismo (Horários)
        now = datetime.now()
        h, m = now.hour, now.minute

        hora_checks = [
            (h <= 2,                                "hora_noturna"),
            (h == 3 and m == 33,                    "hora_pacto"),
            (5 <= h <= 11,                          "hora_expediente"),
            (12 <= h <= 14,                         "hour_lunch"),
            (15 <= h <= 17,                         "hora_tarde"),
            (18 <= h <= 22,                         "hora_novela"),
            (h == 23 and m >= 45,                   "hora_virada"),
            (h == 13 and m == 37,                   "hora_leet"),
            (m == 59,                               "hour_punctual"),
            (m == 0,                                "hora_exata"),
        ]
        for condition, ach_id in hora_checks:
            if condition:
                if await register_global_achievement(user_id, ach_id):
                    unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])

        # 4. Streak
        max_streak = context.get("max_streak", 0)
        streak_map = [
            (3, "streak_3"), (7, "streak_7"), (30, "streak_30"), (100, "streak_100")
        ]
        for limit, ach_id in streak_map:
            if max_streak >= limit:
                if await register_global_achievement(user_id, ach_id):
                    unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])

        # 5. Pesagens totais (fonte: weight_history — toda a história do bot)
        total_weighs = await get_total_weighs_from_history(user_id)
        weighs_map = [
            (10, "weigh_10"), (100, "weigh_100"), (200, "weigh_200")
        ]
        for limit, ach_id in weighs_map:
            if total_weighs >= limit:
                if await register_global_achievement(user_id, ach_id):
                    unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])

        # Primeira pesagem
        if await register_global_achievement(user_id, "first_weigh"):
            unlocked_now.append(ACHIEVEMENTS_DEFS["first_weigh"])

    # 6. Checagem de Duelos
    if event_type == "duel_result":
        if await register_global_achievement(user_id, "first_duel"):
            unlocked_now.append(ACHIEVEMENTS_DEFS["first_duel"])

        wins = stats["duels_won"]
        duel_map = [
            (10, "duels_10"), (25, "duels_25"), (50, "duels_50")
        ]
        for limit, ach_id in duel_map:
            if wins >= limit:
                if await register_global_achievement(user_id, ach_id):
                    unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])


    # 7. Checagem de Doações
    if event_type == "donate":
        if await register_global_achievement(user_id, "first_donate"):
            unlocked_now.append(ACHIEVEMENTS_DEFS["first_donate"])

        kg_total = stats["kg_donated"]
        donate_map = [
            (25, "donated_25"), (50, "donated_50"), (100, "donated_100")
        ]
        for limit, ach_id in donate_map:
            if kg_total >= limit:
                if await register_global_achievement(user_id, ach_id):
                    unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])


    # 8. Sorte (Bct do Dia)
    if event_type == "bct_dia":
        wins = stats["bct_dia_wins"]
        luck_map = [
            (1, "bct_dia_1"), (5, "bct_dia_5"), (10, "bct_dia_10"), (25, "bct_dia_25")
        ]
        for limit, ach_id in luck_map:
            if wins >= limit:
                if await register_global_achievement(user_id, ach_id):
                    unlocked_now.append(ACHIEVEMENTS_DEFS[ach_id])

    # Notificar se houver bot disponível e conquistas novas
    if bot and unlocked_now:
        user_name = await get_user_name(user_id, chat_id) or "Guerreiro"

        for ach in unlocked_now:
            msg = _build_achievement_msg(user_name, ach)
            try:
                await bot.send_message(chat_id=user_id, text=msg, parse_mode="HTML")
            except Exception:
                pass

    return unlocked_now
