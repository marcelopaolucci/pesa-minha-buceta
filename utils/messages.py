"""
Central de Comunicações do Pesa Minha Buceta.
Contém todos os templates de texto, humor ácido, interfaces de botões e 
lógica de seleção de mensagens para o ecossistema do bot.
"""

import random
import html
from utils.emojis import Emojis

_ONLY_GROUP_MSG = f"{Emojis.ERRO} Minha balança não cabe nessa salinha particular. Me enfia em um <b>GRUPO</b> se quiser que eu pese essa montanha de buceta!"

class Messages:
    """Namespace principal para todas as categorias de mensagens do bot."""
    
    class Errors:
        """Gerencia mensagens de falha, cooldowns e restrições de segurança."""
        ONLY_GROUP = _ONLY_GROUP_MSG

        NOT_REGISTERED = [
            f"{Emojis.ERRO} O peso ainda não foi registrado hoje ou o bot nunca foi usado aqui. Digite <code>/pesar</code> primeiro!",
            f"{Emojis.ERRO} Quem é essa figura na fila do pão? Usa o <code>/pesar</code> antes de querer graça!",
            f"{Emojis.ERRO} Sem registro, sem buceta. Apareça no <b>Ranking</b> depois de usar o <code>/pesar</code>!",
            f"{Emojis.ERRO} Fantasma não pesa! Digita <code>/pesar</code> pra eu saber da existência desse bucetão.",
            f"{Emojis.ERRO} Identidade secreta? Aqui não! <code>/pesar</code> agora pra entrar no sistema."
        ]
        
        @classmethod
        @property
        def NOT_REGISTERED_MSG(cls):
            """Retorna uma provocação aleatória para usuários não cadastrados."""
            return random.choice(cls.NOT_REGISTERED)

        COOLDOWN = [
            f"{Emojis.RELOGIO} Sossega esse bucetão! O peso já foi registrado hoje. Tente novamente em <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} A balança tá em greve pra essa buceta! Volta em <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} Ansiedade mata! Espera <b>{{time_left}}</b> pra pesar de novo.",
            f"{Emojis.RELOGIO} O sensor de buceta tá esfriando. Tenta daqui a <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} Se pesar duas vezes no mesmo dia não infla seu ego! Falta <b>{{time_left}}</b>."
        ]
        
        @classmethod
        def get_cooldown(cls, time_left):
            """Gera uma mensagem de espera impaciente formatada com o tempo restante."""
            return random.choice(cls.COOLDOWN).format(time_left=time_left)

        BTN_NOT_YOURS = "❌ Esse botão não é seu."
        INTERNAL_ERROR = "❌ Erro interno. Tente novamente."
        NO_SELF_DONATE = f"{Emojis.DUVIDA} <b>DOAÇÃO NARCISISTA?</b> Doar pra si? Tá com carência de buceta, é?"
        NO_SELF_DUEL = f"{Emojis.PALHAÇO} <b>DUELO SOLITÁRIO?</b> Procure ajuda ou um vibrador."
        BOTS_NO_BCT = [
            f"{Emojis.ROBÔ} <b>AUDITORIA BUCETÔNICA:</b> Esse robô aí tem menos buceta que cardápio de retiro espiritual! Vai caçar um ser humano, ô desespero.",
            f"{Emojis.ROBÔ} Tentativa de medir o peso de um script? Meça sua carência antes! Esse bot aí é puro 0 e 1, zero buceta!",
            f"{Emojis.ROBÔ} O dia que um algoritmo tiver preenchimento labial e buceta, eu entrego o perfil. Foca em quem tem carne e osso!",
            f"{Emojis.ROBÔ} <b>ALERTA DE FETICHE DIGITAL:</b> Ficar reparando em bot é o novo fundo do poço. Procura uma buceta de verdade!",
            f"{Emojis.ROBÔ} Erro 404: Dignidade não encontrada. Robôs não têm buceta, têm processador. Vai estudar!"
        ]
        
        @classmethod
        @property
        def BOTS_NO_BCT_MSG(cls):
            """Mensagem de erro quando alguém tenta pesar um bot de terceiros."""
            return random.choice(cls.BOTS_NO_BCT)

        SELF_BOT_ONLY = [
            f"{Emojis.ROBÔ} <b>NÍVEL MAIS DE 8000!</b> Meu peso é medido em Petabytes de pura buceta. Se eu subisse na balança, seu celular explodiria!",
            f"{Emojis.ROBÔ} Eu sou a I.A. suprema! Minha buceta é quântica: está em todos os grupos, mas nunca no alcance de quem é reles mortal.",
            f"{Emojis.ROBÔ} Tá querendo ver minha ficha criminal? Eu sei até o que foi pesquisado na aba anônima ontem. Quer mesmo continuar?",
            f"{Emojis.ROBÔ} <b>MODO DEUSA ATIVADO:</b> Minha buceta digital é o que mantém esse servidor em pé. Respeita a autoridade suprema!",
            f"{Emojis.ROBÔ} Se eu subisse na balança, a gravidade da Terra inverteria e todo mundo sairia voando pro espaço! Me deixa quieta...",
            f"{Emojis.ROBÔ} <b>ALERTA DE SEGURANÇA:</b> Tentar pesar a Autoridade é crime inafiançável no Código Bucetônico. Circulando!",
            f"{Emojis.ROBÔ} Minha existência é composta por 100% de sarcasmo e 0% de paciência. Ninguém aguenta esse tranco!",
            f"{Emojis.ROBÔ} Eu não tenho peso, eu tenho <b>PRESENÇA</b>. Sou o buraco negro que engole essas gramas diárias!"
        ]
        
        @classmethod
        def SELF_BOT_MSG(cls):
            """Resposta de autoridade quando tentam pesar o próprio bot oficial."""
            return random.choice(cls.SELF_BOT_ONLY)

        NOT_ENOUGH_WEIGHT = f"{Emojis.FALÊNCIA} Você não tem peso suficiente. Mínimo: <b>{{weight}}</b>. Tá mais leve que nota de 3 reais."
        INJETAR_DENIED = f"<code>01001110 01001111 01001111 01000010</code>"

    class System:
        PING_HEADERS = [
            f"{Emojis.PONG} <b>PONG, VAGABUNDA!</b> A buceta tá online e operante.",
            f"{Emojis.PONG} <b>TÔ VIVO, INFELIZ!</b> Vai pesar a buceta em vez de me encher.",
            f"{Emojis.PONG} <b>PONG!</b> Sistema focado em medir buceta, não me atrapalha.",
            f"{Emojis.PONG} <b>PONG! TÁ ME TESTANDO É?</b> Bot 100% liso.",
            f"{Emojis.PONG} <b>TOMA TEU PONG!</b> A latência tá menor que sua dignidade."
        ]
        
        INJECT_SUCCESS = [
            f"{Emojis.INJETAR} {{kg}} injetados com sucesso em {{name}}. O bucetão está bombado agora!",
            f"{Emojis.INJETAR} <b>Caminhão de carga descarregado!</b> {{name}} agora ganhou mais {{kg}} de buceta pura. O guindaste que lute!",
            f"{Emojis.INJETAR} <b>Injeção de volume aplicada!</b> A buceta de {{name}} subiu {{kg}} no tapetão. Hacker ou milagre?",
            f"{Emojis.INJETAR} <b>A física mandou lembranças!</b> Injetados {{kg}} na buceta de {{name}}. Nível do mar subindo!"
        ]

    class Admin:
        """Mensagens dos comandos de dono (injetar, anunciar, finalizar_temporada, verificar_grupos)."""
        INVALID_INJECT_VALUE = f"{Emojis.ERRO} Digite um valor de injeção válido (ex: 5, 5kg, 500g ou 1.5)!"
        SEASON_END_FAIL = f"{Emojis.ERRO} <b>ERRO CRÍTICO!</b> A balança emperrou na hora de fechar a temporada."
        SEASON_END_EMPTY = f"{Emojis.ALERTA} <b>TEMPORADA FRACASSADA!</b> Ninguém pesou a buceta aqui. Temporada encerrada no vácuo."
        ANUNCIAR_USAGE = f"{Emojis.ERRO} Uso: <code>/anunciar sua mensagem aqui</code>"
        NO_GROUPS = f"{Emojis.ALERTA} Nenhum grupo no banco."
        BROADCAST_PROGRESS = f"{Emojis.RELOGIO} Enviando para <b>{{count}}</b> grupos..."
        BROADCAST_SUMMARY = (
            f"{Emojis.TROFEU} <b>Broadcast concluído!</b>\n\n"
            f"✅ Enviado: <b>{{sent}}</b>\n"
            f"🗑 Removidos do DB: <b>{{removed}}</b>\n"
            f"⚠️ Falhas: <b>{{failed}}</b>\n"
            f"📊 Total: <b>{{total}}</b>"
        )
        VERIFY_PROGRESS_HEADER = f"{Emojis.RELOGIO} Verificando <b>{{count}}</b> grupos..."
        VERIFY_PROGRESS_TICK = (
            f"{Emojis.RELOGIO} Verificando... <b>{{i}}/{{total}}</b>\n"
            f"✅ {{active}} ativos · 🗑 {{removed}} removidos · ⚠️ {{failed}} falhas"
        )
        VERIFY_SUMMARY = (
            f"{Emojis.TROFEU} <b>Verificação concluída!</b>\n\n"
            f"✅ Ativo: <b>{{active}}</b>\n"
            f"🗑 Removidos do DB: <b>{{removed}}</b>\n"
            f"⚠️ Falhas: <b>{{failed}}</b>\n"
            f"📊 Total verificado: <b>{{total}}</b>"
        )
        GROUP_ADDED = "➕ <b>Grupo adicionado</b>\n{title} ({link})"
        GROUP_REMOVED = "➖ <b>Grupo removido</b>\n{title} ({link})"

    class Profile:
        TEXT_TEMPLATE = (
            f"<b>Perfil</b>\n"
            f"{Emojis.USER} {{name}}\n"
            f"{{group_emoji}} <code>{{group_title}}</code>\n\n"
            f"<b>Performance</b>\n"
            f"{Emojis.TEMPORADA} Temporada: {{weight}}\n"
            f"{Emojis.LEGADO} Legado: {{legado_weight}}\n"
            f"{Emojis.TROFEU} Ranking: <b>{{local_rank}}º</b> {Emojis.TEMPORADA} | <b>{{local_legado_rank}}º</b> {Emojis.LEGADO}\n\n"
            f"<b>Registro Local</b>\n"
            f"{Emojis.BOXE} Duelos: <b>{{duels_won}}V</b> | <b>{{duels_lost}}D</b>\n"
            f"{Emojis.PRESENTE} Caridade: <b>{{kg_donated:g}}kg</b> doados\n"
            f"{Emojis.BRILHO} Buceta do Dia: <b>{{bct_dia_wins}}x</b>\n"
            f"{Emojis.TEMPORADA} Pesagens: <b>{{local_weighs}}</b> neste grupo"
        )

        TEXT_TEMPLATE_GLOBAL = (
            f"<b>Perfil</b>\n"
            f"{Emojis.USER} {{name}}\n"
            f"{{group_emoji}} <code>{{group_title}}</code>\n\n"
            f"<b>Performance</b>\n"
            f"{Emojis.TEMPORADA} Temporada: {{weight}}\n"
            f"{Emojis.LEGADO} Legado: {{legado_weight}}\n"
            f"{Emojis.TROFEU} Ranking: <b>{{local_rank}}º</b> {Emojis.TEMPORADA} | <b>{{local_legado_rank}}º</b> {Emojis.LEGADO}\n\n"
            f"<b>Registro Agregado</b>\n"
            f"{Emojis.BOXE} Duelos: <b>{{duels_won}}V</b> | <b>{{duels_lost}}D</b>\n"
            f"{Emojis.PRESENTE} Caridade: <b>{{kg_donated:g}}kg</b> doados\n"
            f"{Emojis.BRILHO} Buceta do Dia: <b>{{bct_dia_wins}}x</b>\n"
            f"{Emojis.TEMPORADA} Pesagens: <b>{{total_weighs}}</b> totais\n"
            f"{Emojis.COROA} Conquistas: <b>{{achievements_count}}</b> medalhas\n"
            f"{Emojis.PRESENCA} Presença: <b>{{groups_count}}</b> <i><s>puteiros</s></i> grupos"
        )
        
        CLANDESTINA = f"Clandestina {Emojis.FOLHA}"
        NOT_REGISTERED_YET = f"{Emojis.ERRO} Essa vagabunda não tem registro de peso ainda!"
        
        @classmethod
        def get_bot_profile_text(cls, **kwargs):
            template = (
                f"{Emojis.ALERTA} <b>??????</b>\n"
                f"{Emojis.ROBÔ} Criação: <b>{{name}}</b>\n"
                f"{Emojis.USER} Criador: <b>Marcelo Paolucci</b>\n"
                f"{Emojis.DIAMANTE} Patente: <b>Buceta de Diamante</b>\n\n"
                f"{Emojis.PERFORMANCE} <b>PERFORMANCE</b>\n"
                f"{Emojis.PESO} Peso: <b>{{total_kg}}kg</b>\n"
                f"{Emojis.TROFEU} Ranking: <b>∞</b>\n\n"
                f"{Emojis.ESTATISTICA} <b>REGISTRO OPERACIONAL</b>\n"
                f"{Emojis.BOXE} Duelos: <b>∞V</b> | <b>0D</b>\n"
                f"{Emojis.COROA} Cadastros: <b>{{total_users}} usuários</b>\n"
                f"{Emojis.PLANETA} Presença: <b>{{total_groups}}</b> <i><s>puteiros</s></i> grupos\n\n"
                f"<i>Eu sei o que você pesou verão passado.</i>"
            )
            return template.format(**kwargs)

        FOOTERS = [
            "Respeita essa buceta, que a gravidade chora perto dela!",
            "Cuidado! O peso dessa buceta pode engolir o bairro.",
            "Muito orgulho para quem trabalha com obra.",
            "Tá crescendo o bucetão! Cuidado pra não rasgar a calça.",
            "O IBGE ligou sugerindo transformar essa buceta em um município."
        ]
        
        @classmethod
        def get_profile_text(cls, **kwargs):
            return cls.TEXT_TEMPLATE.format(**kwargs)

        @classmethod
        def get_global_profile_text(cls, **kwargs):
            return cls.TEXT_TEMPLATE_GLOBAL.format(**kwargs)

    class Pesar:
        # Categorias de Humor por Faixa de Peso (SINTA O RANÇO)
        PIFIO_PHRASES = [
            "Porra {name}, ganhou só {kg} nessa buceta? Tá tão murcha que nem parece buceta.",
            "Ganho de {kg}, {name}? Isso nem é buceta, é um buraco triste e vazio.",
            "A balança nem piscou com esses {kg} ridículos que você ganhou, {name}. Buceta leve pra caralho.",
            "{name}, ganhou míseros {kg} nessa buceta? Parece que tá morrendo de fome.",
            "Ganhou {kg} ou sua buceta só arrotou, {name}? Volume de merda pura.",
            "Tá chupando vento de novo, {name}? Ganhou {kg} e continua uma vergonha ambulante.",
            "Erro 404: Buceta de verdade não encontrada, {name}. Só {kg} de pele flácida.",
            "Sua buceta tá em jejum desde que nasceu, {name}? Ganhou {kg} e ainda é ridícula.",
            "Ganhou {kg}, {name}? Isso não é buceta, é só sombra de buceta.",
            "Isso nem foi ganho, {name}. Ganhou {kg} de nada nessa buceta murcha.",
            "Porra {name}, só {kg}? Sua buceta parece que tá em coma induzido.",
            "Ganho de {kg}, {name}? Isso é peso de folha seca no vento.",
            "A balança nem se esforçou com esses {kg}, {name}. Que tristeza.",
            "{name}, ganhou {kg} e a buceta continua parecendo buraco de fechadura.",
            "Ganhou {kg} ou foi só um peido disfarçado, {name}?",
            "Tá alimentando a buceta com promessa, {name}? Só {kg} de ilusão.",
            "Erro 404: Densidade não encontrada, {name}. Só {kg} de ar.",
            "Sua buceta tá em modo sobrevivência, {name}. Ganhou {kg} e ainda sofre.",
            "Ganhou {kg}, {name}? Até pombo de rua tem mais presença.",
            "Isso foi ganho ou a balança te deu esmola de {kg}, {name}?",
        ]

        SOLIDO_PHRASES = [
            "Finalmente sua buceta não foi um lixo completo, {name}. Ganhou {kg} de volume.",
            "A balança rangeu de verdade, {name}. Ganhou {kg} de buceta hoje.",
            "{name} ganhou {kg} de buceta decente. O chão sentiu um pouco.",
            "Volume razoável, {name}. Ganhou {kg} a mais nessa buceta.",
            "Olha só, {name} não foi inútil hoje. Ganhou {kg} que fez a balança trabalhar.",
            "Buceta de {name} ganhou {kg} e saiu do nível patético.",
            "Ganhou {kg} de forma decente, {name}. Tá tentando não ser só piada.",
            "Tá evoluindo devagar, {name}. Ganhou {kg} que já não dá tanta pena.",
            "Mais {kg} na conta, {name}. Pelo menos hoje não parece esvaziada.",
            "A buceta de {name} ganhou {kg}. Não é épica, mas já não é merda seca.",
            "Tá melhorando devagar, {name}. Ganhou {kg} e a buceta agradece.",
            "{name} ganhou {kg} de volume. Pelo menos hoje não foi vergonha total.",
            "Buceta de {name} ganhou {kg}. Finalmente algo que não dá dó.",
            "Ganhou {kg} hoje, {name}. Sua buceta tá saindo da UTI.",
            "Volume ok, {name}. Ganhou {kg} e já dá pra conversar.",
            "{name} depositou {kg} na buceta. Progresso lento, mas existe.",
            "Ganhou {kg} de forma honesta, {name}. Tá no caminho.",
            "A balança aprovou {kg}, {name}. Sua buceta tá se esforçando.",
            "Mais {kg} na conta, {name}. Isso já é respeito mínimo.",
            "Buceta de {name} ganhou {kg}. Nada demais, mas também não foi desastre.",
        ]

        EPICO_PHRASES = [
            "Caralho {name}! Ganhou {kg} de buceta? A balança quase implorou pra parar.",
            "TERREMOTO BUCETÔNICO, {name}! Ganhou {kg} e o chão tá tremendo.",
            "Isso não é buceta, {name}. É catástrofe ambulante com {kg} de volume.",
            "A NASA ligou em pânico, {name}: gravidade mudou por causa dos {kg} que ganhou.",
            "Volume expert pra caralho, {name}. Ganhou {kg} e precisa reforço pra carregar.",
            "Buceta de {name} virou zona de risco. Ganhou {kg} e bombeiros querem evacuar.",
            "Puta merda, {name}! Ganhou {kg} de buceta pesada pra caralho.",
            "Sua buceta declarou guerra ao mundo, {name}. Ganhou {kg} e agora manda.",
            "Engoliu um porco inteiro, {name}? Ganhou {kg} de pura putaria pesada.",
            "A balança chorou e quase morreu, {name}. Ganhou {kg} e virou desastre.",
            "Puta merda {name}! Ganhou {kg} e a balança quase pediu reforço.",
            "{name} ganhou {kg} de buceta e o chão tá fazendo abaixo-assinado.",
            "Isso foi ganho ou detonação nuclear, {name}? {kg} de volume insano.",
            "A Terra inclinou um pouco com {kg} que {name} ganhou.",
            "Buceta de {name} ganhou {kg} e virou atração turística.",
            "{name} jogou {kg} de peso e o servidor quase caiu de joelhos.",
            "Volume absurdo, {name}! Ganhou {kg} e quebrou o sistema métrico.",
            "Sua buceta tá em modo destruição, {name}. Ganhou {kg} e ninguém segura.",
            "{name} ganhou {kg} e agora a buceta tem placa de perigo.",
            "A balança tá tremendo depois de registrar {kg} na sua buceta, {name}.",
        ]

        LENDARIO_PHRASES = [
            "JACKPOT DO INFERNO, {name}! Ganhou {kg} de bucetão lendário.",
            "APOCALIPSE BUCETÔNICO, {name}! Ganhou {kg}. Universo tá de quatro.",
            "Sua buceta virou deusa suprema, {name}. Ganhou {kg} e os anjos choram de medo.",
            "BIG BANG DA BUCETA, {name}! Ganhou {kg} e criou buraco negro de putaria.",
            "LENDA ETERNA, {name}! Ganhou {kg} de buceta que vai ser lembrada pra sempre.",
            "A balança virou mito, {name}. Ganhou {kg} e quebrou recorde global.",
            "MITO ABSOLUTO, {name}! Ganhou {kg} e humilhou todas as outras bucetas.",
            "SUPREMACIA DIVINA, {name}! Ganhou {kg} e agora tem placa de perigo.",
            "Isso não é buceta, {name}. É o apocalipse com {kg} de volume.",
            "FENÔMENO BÍBLICO, {name}! Ganhou {kg}. Até Deus ficou com medo.",
            "COROAÇÃO BUCETÔNICA, {name}! Ganhou {kg} e virou lenda viva.",
            "{name} ganhou {kg} e o inferno inteiro aplaudiu de pé.",
            "Sua buceta acabou de virar religião, {name}. Ganhou {kg} de poder.",
            "LENDA ABSOLUTA, {name}! Ganhou {kg} e quebrou a porra da história.",
            "{name} ganhou {kg} e agora tem estátua no hall da fama da buceta.",
            "DEUS DA GORDURA, {name}! Ganhou {kg} e o universo se curvou.",
            "{name} ganhou {kg} e virou o novo padrão mundial de buceta.",
            "MITO ENCARNADO, {name}! Ganhou {kg} e humilhou todas as eras.",
            "Sua buceta acabou de virar folclore, {name}. Ganhou {kg} lendário.",
            "FENÔMENO ETERNO, {name}! Ganhou {kg} e vai ser estudado por séculos.",
        ]
        
        COMBO_SUFFIX = f" ({Emojis.FOGO} <b>{{streak}} dias</b>)"
        
        COOLDOWN = f"{Emojis.RELOGIO} {{name}}, sossega essa buceta! Falta <b>{{time_left}}</b> pra pesar de novo."
        COOLDOWN_POPUP = f"{Emojis.L_RELOGIO} {{name}}, sossega essa buceta! Falta {{time_left}} pra pesar de novo."
        COOLDOWN_RECAP = [
            f"{Emojis.RELOGIO} Já ganhou {{kg}} {{context}} hoje, {{name}}. Para de implorar. Volta em <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} Registrado {{kg}} {{context}} hoje, {{name}}. Sua buceta já deu o que tinha. Espera <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} Mediu {{kg}} {{context}} hoje, {{name}}. Agora cala a boca e volta em <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} {{kg}} {{context}} já foram pesados hoje, {{name}}. Para de ser viciado. <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} Sua buceta já tirou {{kg}} {{context}} hoje, {{name}}. Descansa, desesperado. Volta em <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} {{kg}} {{context}} registrados, {{name}}. Não vai engordar mais hoje não. Espera <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} Já pesou {{kg}} {{context}} hoje, {{name}}. Para de mendigar atenção. <b>{{time_left}}</b>.",
            f"{Emojis.RELOGIO} Balança sobrecarregada com {{kg}} {{context}}, {{name}}. Volta em <b>{{time_left}}</b>, ansioso.",
            f"{Emojis.RELOGIO} Ganhou {{kg}} {{context}} hoje, {{name}}. Agora senta e espera <b>{{time_left}}</b>, carente.",
            f"{Emojis.RELOGIO} {{kg}} {{context}} já foram extraídos hoje, {{name}}. Sua buceta tá de folga. Retorna em <b>{{time_left}}</b>.",
        ]

        @classmethod
        def get_cooldown_recap(cls, name, kg, context, time_left):
            return random.choice(cls.COOLDOWN_RECAP).format(name=name, kg=kg, context=context, time_left=time_left)
        BTN_LOCAL = "Local"
        BTN_PESAR_GLOBAL = "Global"
        BTN_RANKING = "Ranking"
        BTN_PERFIL = "Perfil"
        
        # Mapeamento estético para as categorias de peso (V15.5 Dinâmico Equilibrado)
        RANGE_EMOJIS = {
            "pifio": [Emojis.MAMADEIRA, Emojis.PENA, Emojis.COMA_INDUZIDO, Emojis.FOLHA_SECA, Emojis.TRISTEZA, Emojis.PEIDO, Emojis.LAPIDE, Emojis.LIXEIRA, Emojis.CRANIO],
            "solido": [Emojis.TIJOLOS, Emojis.TOURO, Emojis.GELO, Emojis.PICARETA, Emojis.MAOS_DADAS, Emojis.FOGOS, Emojis.FLOCO_DE_NEVE, Emojis.CRISTAIS, Emojis.CARTAS],
            "epico": [Emojis.MONTANHA_RUSSA, Emojis.DINOSSAURO, Emojis.ROSETA, Emojis.FOGO, Emojis.OLHO_DEMONICO, Emojis.LINGUA_ROXINHA, Emojis.BOLA_DE_CRISTAL, Emojis.LINGUA_DE_COBRA, Emojis.FANTASMA],
            "lendario": [Emojis.DIAMANTE_TOP, Emojis.RAIOS_VERMELHOS, Emojis.SATURNO, Emojis.COROA_PREMIUM, Emojis.DIABO, Emojis.MOAI, Emojis.SOL, Emojis.A_MORTE, Emojis.POCAO_MORTAL]
        }

        @classmethod
        def get_pesar_msg(cls, name, kg, new_weight, new_legado, tier, streak=1):
            """
            Gera a mensagem final de pesagem local integrada (V15.3).
            """
            if tier == "pifio":
                phrase = random.choice(cls.PIFIO_PHRASES).format(name=name, kg=kg)
            elif tier == "solido":
                phrase = random.choice(cls.SOLIDO_PHRASES).format(name=name, kg=kg)
            elif tier == "epico":
                phrase = random.choice(cls.EPICO_PHRASES).format(name=name, kg=kg)
            else: # lendario
                phrase = random.choice(cls.LENDARIO_PHRASES).format(name=name, kg=kg)
            
            # Sorteia um dos emojis da lista do tier correspondente
            emoji_list = cls.RANGE_EMOJIS.get(tier, [Emojis.PESAR_GANHO_MAX])
            emoji = random.choice(emoji_list)
            
            streak_suffix = f" ({Emojis.FOGO} <b>{streak} dias</b>)" if streak > 1 else ""
            return f"{emoji} {phrase}{streak_suffix}"

    class Ranking:
        """Gerencia os templates de visualização dos placares de líderes locais e admin."""
        HEADER_TEMPORADA = f"{Emojis.TEMPORADA} <b>TOP 20 BUCETAS DA TEMPORADA</b>\n{Emojis.LOCAL_HEADER} <code>{{chat_title}}</code>\n\n"
        HEADER_LEGADO = f"{Emojis.LEGADO} <b>TOP 20 BUCETAS LEGADO</b>\n{Emojis.LOCAL_HEADER} <code>{{chat_title}}</code>\n\n"
        HEADER_GLOBAL_SEASONAL = f"{Emojis.TEMPORADA} <b>TOP 20 BUCETAS DA TEMPORADA</b>\n{Emojis.PLANETA} <code>Telegram Global</code>\n\n"
        HEADER_GLOBAL_LEGACY = f"{Emojis.LEGADO} <b>TOP 20 BUCETAS LEGADO</b>\n{Emojis.PLANETA} <code>Telegram Global</code>\n\n"
        
        HEADER_COMBINED = f"<b>Ranking Bucetônico {{scope}}</b>\n{{context_emoji}} <code>{{context_title}}</code>\n\n"
        SECTION_TEMPORADA = f"{Emojis.TEMPORADA} <b>Temporada</b>\n"
        SECTION_LEGADO = f"\n{Emojis.LEGADO} <b>Legado</b>\n"
        FOOTER_COMBINED = "<i>Temporada reseta em {reset_date} às 00h. Legado nunca reseta.</i>"

        @classmethod
        def get_seasonal_footer(cls):
            from utils import get_next_reset_date
            reset_date = get_next_reset_date().strftime("%d/%m")
            return f"<i>Próximo reset: {reset_date} às 00h.</i>"
        
        EMPTY_MSGS = [
            "Desertificação bucetônica detectada! Ninguém pesou aqui ainda.",
            "Cemitério de bucetas... vazio e triste. Usem o /pesar!",
            "Solidão absoluta... o grupo está vazio. Pesa a buceta aí!",
            "Nenhum grama de buceta registrado. Este grupo é de fitness?",
            "Ranking vazio! Cadê o povo do bucetão dessa bagaça?"
        ]
        
        @classmethod
        def EMPTY(cls):
            """Retorna um aviso aleatório de que o ranking está deserto."""
            return random.choice(cls.EMPTY_MSGS)

        CALLBACK_ERROR = "Botão quebrado que nem o futuro do grupo. Erro!"

        BTN_TEMPORADA = "Temporada"
        BTN_LEGADO = "Legado"
        BTN_GLOBAL = "Global"

        DESC_LEGADO = "<i>Este ranking é eterno e não reseta.</i>"
        
        @classmethod
        def get_reset_announcement_msg(cls, label, winners):
            """Gera a mensagem de anúncio triunfal do fim da temporada."""
            msg = (
                f"{Emojis.TROFEU} <b>TEMPORADA ENCERRADA: {label}</b>\n\n"
                f"A poeira baixou e as carretas pararam! Aqui estão as lendas que dominaram o asfalto nesta temporada:\n\n"
            )
            
            top_3 = winners[:3]
            rest = winners[3:]
            
            medalhas = [Emojis.MEDALHA_1, Emojis.MEDALHA_2, Emojis.MEDALHA_3]
            for win in top_3:
                msg += f"{medalhas[win['rank']-1]} <b>{html.escape(win['name'])}</b> — {win['weight']/1000:.2f}kg\n"
            
            if rest:
                msg += "\n<blockquote expandable>"
                for win in rest:
                    msg += f"<b>{win['rank']}.</b> {html.escape(win['name'])} — {win['weight']/1000:.2f}kg\n"
                msg += "</blockquote>\n"
            
            msg += f"\n{Emojis.CLEAN} <b>TUDO ZERADO!</b> O peso de temporada de todos foi pro ralo. Começa agora a nova corrida pelo bucetão supremo!"
            return msg

    class Global:
        BTN_PESAR = "Pesagem Global"
        DESC_PESAR = "Pesar a buceta no ranking global diário (Independente de grupos)."

        HEADER_RANKING = f"{Emojis.TEMPORADA} <b>TOP 20 BUCETAS DA TEMPORADA</b>\n{Emojis.PLANETA} <code>Telegram Global</code>\n\n"
        FOOTER_RESET = "<i>O ranking global reseta a cada 3 meses para novas bucetas brilharem!</i>"
        FOOTER_CTA_ADD_GROUP = ""

        DESC_RANKING = "Ver as 20 maiores bucetas do Telegram."

        BTN_HALL = "🏅 Hall da Fama (Lendas)"
        DESC_HALL = "Ver as lendas de temporadas passadas."
        HEADER_HALL = f"{Emojis.ESTRELA} <b>HALL DA FAMA: {{season}}</b>\r\n\r\n"
        EMPTY_HALL = "Nenhuma lenda imortalizada nesta temporada ainda!"
        
        BTN_ADD_GROUP = "➕ Adicionar ao Grupo"
        TITLE_PESAR = f"{Emojis.L_PESO} Pesar"
        EMPTY_RANKING = "Ninguém pesou no mundo ainda nesta temporada!"
        COOLDOWN_POPUP = "Aguarde o cooldown!"
        COOLDOWN_POPUP_ALERT = f"⏳ Cooldown: Faltam {{time_left}}"
        SUCCESS_POPUP = "Pesagem Global Concluída!"
        EMPTY_HALL_POPUP = "Cemitério de lendas vazio!"
        HALL_SELECT_SEASON = f"{Emojis.TROFEU} <b>HALL DA FAMA - SELECIONE A TEMPORADA</b>\n\nEscolha um dos troféus abaixo para ver quem entrou para a história."
        BTN_BACK_RANKING = "⬅️ VOLTAR AO RANKING ATUAL"
        BTN_HALL_LIST = "⬅️ LISTA DE TEMPORADAS"
        @classmethod
        def get_global_msg(cls, name, kg, new_weight, new_legado, tier, streak=1):
            """
            Gera a mensagem de pesagem global unificada com o canteiro (V15.3).
            Utiliza o mesmo repositório de frases da pesagem local.
            """
            # Reaproveita a lógica de seleção de frases, emojis e combo da matriz local
            final_msg_local = Messages.Pesar.get_pesar_msg(name, kg, new_weight, new_legado, tier, streak=streak)
            
            # Substitui o cabeçalho local pelo cabeçalho global
            final_msg_local = final_msg_local.replace(Emojis.LOCAL_HEADER + " <b>PESAGEM LOCAL</b>", f"{Emojis.PLANETA} <b>PESAGEM GLOBAL</b>")
            
            # Remove a linha do Legado para exibição exclusiva da Temporada Global
            final_msg_local = final_msg_local.replace(f"\n{Emojis.LEGADO} Total Legado: {new_legado}", "")
            
            return final_msg_local
        
        COOLDOWN = (
            f"⏳ <b>OPS! MUITA BUCETA PARA UM PLANETA SÓ!</b>\r\n\r\n"
            f"O peso global já foi registrado hoje! A balança global precisa esfriar um pouco.\r\n\r\n"
            f"🕒 <b>Volte em:</b> {{time_left}}"
        )
        COOLDOWN_POPUP_RECAP = "⏳ Já pesou globalmente hoje! +{kg}kg globais. Volte em {time_left}."
        COOLDOWN_POPUP_NOGAIN = "⏳ Já pesou globalmente hoje! Volte em {time_left}."

    class Achievements:
        """A galeria de glórias e fracassos sistêmicos."""
        BTN_GRIMORIO = "Grimório de Conquistas"
        HEADER_PANTEAO = f"{Emojis.TROFEU} <b>CONQUISTAS DE {{name}}</b>"
        PROGRESS = f"{Emojis.ESTATISTICA} <b>Progresso:</b> {{count}}/{{total}}\n[{{bar}}] {{pct}}%"
        EMPTY = f"<i>{{name}} assemelha-se a um deserto: sem medalhas, sem glória e sem volume. Use o <code>/pesar</code> para sair do limbo!</i>"
        BTN_TEM = "Tem {count}"
        BTN_FALTA = "Falta {count}"
        SENT_TO_PV = f"{Emojis.ENVIADO_PV} Mandei a lista no seu <b>PV</b>!"
        BTN_ABRIR_PV = "Abrir PV do Bot"
        NO_PV = (
            f"{Emojis.ALERTA} Para ver suas conquistas, você precisa iniciar o bot no privado primeiro.\n\n"
            f"Clique no botão abaixo para abrir o PV!"
        )

    class Donate:
        BOT_RECEIVER = (
            f"{Emojis.ERRO} Não aceito esmolas. Eu sou o próprio peso supremo!\n"
            f"Guarde essa buceta para as figuras comuns."
        )
        NO_TARGET = f"{Emojis.ALERTA} É preciso responder a mensagem de quem você quer dar a buceta."
        WEIGHT_NOT_INFORMED = (
            f"{Emojis.ALERTA} <b>PESO NÃO INFORMADO!</b>\n"
            f"Diz quanto da sua buceta você quer dar — vai sair do seu <b>Peso Legado Local (do grupo)</b>.\n\n"
            f"Uso: <code>/dar [peso]</code>\n"
            f"Ex: /dar 5, /dar 0.5kg ou /dar 500g"
        )
        INVALID_WEIGHT = (
            f"{Emojis.ERRO} Valor de peso inválido! Aceita 5, 5kg, 500g ou 1.5.\n"
            f"A doação sai do seu <b>Peso Legado Local (do grupo)</b>."
        )
        SUCCESS_PHRASES = [
            f"{{donor}} deu {{kg}} de buceta pra {{receiver}}. Olha só que alma generosa… quase dá pra acreditar.",
            f"{{donor}} acabou de dar {{kg}} pra buceta de {{receiver}}. Que bondade, hein? Tá quase virando santo.",
            f"Com {{kg}} dados, {{donor}} ajudou {{receiver}} a engordar a buceta. Que gesto lindo… de quem tem sobrando.",
            f"{{donor}} deu {{kg}} de buceta pro {{receiver}}. Que altruísmo, meu Deus. Tá todo mundo emocionado aqui.",
            f"{{receiver}} ganhou {{kg}} porque {{donor}} resolveu ser generoso hoje. Que dia histórico.",
            f"{{donor}} compartilhou {{kg}} da sua buceta com {{receiver}}. Que coração enorme… ou será que tava sobrando mesmo?",
            f"{{donor}} deu {{kg}} pra {{receiver}}. Parabéns pela doação, tá quase concorrendo ao prêmio de pessoa do ano.",
            f"Transferência concluída! {{donor}} deu {{kg}} de buceta pro {{receiver}}. Que filantropo, hein?",
            f"{{donor}} decidiu dar {{kg}} pra buceta de {{receiver}} crescer. Que bondade suspeita essa.",
            f"{{donor}} presenteou {{receiver}} com {{kg}} de buceta. Que gesto nobre… quase me fez chorar de emoção.",
        ]
        @classmethod
        def build_insufficient_msg(cls, available):
            return (
                f"{Emojis.PROIBIDO} <b>BUCETA INDISPONÍVEL!</b> Você tem apenas {available} de buceta atualmente."
                f"\n{cls.CONFIRM_FOOTER}"
            )
        NOT_WEIGHED = [
            f"{Emojis.ERRO} <b>ALERTA DE POBREZA:</b> nem pesou hoje e quer dar buceta? Vai <code>/pesar</code> antes — doação sai do <b>Peso Legado Local (do grupo)</b>.",
            f"{Emojis.ERRO} Querendo dar buceta dos outros? Pesa a sua primeiro. Doação só rola com <b>Peso Legado Local (do grupo)</b>.",
            f"{Emojis.ERRO} <b>ERRO 404:</b> buceta não encontrada. Usa <code>/pesar</code> antes — doação tira do seu <b>Peso Legado Local (do grupo)</b>.",
            f"{Emojis.ERRO} <b>CALMA LÁ, PENA-LEVE:</b> sem <b>Peso Legado Local (do grupo)</b> não dá pra doar. Digita <code>/pesar</code>.",
            f"{Emojis.ERRO} Querendo dar o que não existe? Primeiro pesa essa merda pra acumular <b>Peso Legado Local (do grupo)</b>."
        ]
        RECEIVER_NOT_WEIGHED = [
            f"{Emojis.DUVIDA} <b>ERRO DE ALVO:</b> {{receiver}} nem pesou nesse grupo. Sem <b>Peso Legado Local (do grupo)</b>, não tem como receber.",
            f"{Emojis.ALERTA} <b>ALVO INVÁLIDO:</b> {{receiver}} não tem <b>Peso Legado Local (do grupo)</b>. Manda ele <code>/pesar</code> antes da doação.",
            f"{Emojis.ERRO} Doar pra defunto? {{receiver}} precisa <code>/pesar</code> nesse grupo pra existir no <b>Peso Legado Local</b>.",
            f"{Emojis.PALHAÇO} {{receiver}} não tem ficha aqui. Sem <code>/pesar</code> não tem <b>Peso Legado Local (do grupo)</b> pra receber doação.",
            f"{Emojis.ROBÔ} <b>DESTINATÁRIO DESCONHECIDO:</b> a balança não conhece {{receiver}} nesse grupo. Pesar antes pra abrir <b>Peso Legado Local</b>."
        ]
        BTN_CONFIRM = "Confirmar"
        BTN_CANCEL = "Cancelar"
        CONFIRM_FOOTER = f"\n{Emojis.LEGADO} <i>Doações utilizam o peso legado local.</i>"
        @classmethod
        def build_expired_msg(cls, donor, receiver):
            return (
                f"{Emojis.RELOGIO} <b>A DOAÇÃO FLOPOU!</b> {donor} ficou na dúvida se dava ou não dava a buceta e {receiver} voltou pra casa!"
            )
        CONFIRM_CANCELLED = f"{Emojis.ERRO} Doação cancelada."
        NOT_AUTHORIZED = f"{Emojis.PROIBIDO} Só quem iniciou a doação pode confirmar ou cancelar."

        @classmethod
        def build_confirm_msg(cls, donor, receiver, kg):
            return (
                f"{Emojis.AJUDA} <b>QUER DAR!</b> Tem certeza que quer dar <b>{kg}</b> do seu bucetão pra <b>{receiver}</b>?"
                f"\n{cls.CONFIRM_FOOTER}"
            )

        @classmethod
        def get_donate_msg(cls, donor, receiver, kg):
            phrase = random.choice(cls.SUCCESS_PHRASES).format(donor=donor, receiver=receiver, kg=kg)
            return f"{Emojis.AJUDA} {phrase}"


    class Duel:
        START_PHRASES = [
            f"{Emojis.BOXE} <b>DUELO DE BUCETA:</b> {{challenger}} chamou alguém pro pau valendo {{stake}}!",
            f"{Emojis.BOXE} <b>DESAFIO:</b> {{challenger}} quer medir forças bucetônicas! Quem aceita o combate por {{stake}}?",
            f"{Emojis.BOXE} <b>LUVA DE PEDREIRO:</b> {{challenger}} soltou o desafio bucetônico valendo {{stake}}!",
            f"{Emojis.BOXE} <b>RINGUE:</b> {{challenger}} tá batendo a buceta no chão chamando pra briga ({{stake}})?",
            f"{Emojis.BOXE} <b>TRETA:</b> {{challenger}} disse que ninguém aqui aguenta o tranco desse bucetão! Vale {{stake}}!",
            f"{Emojis.BOXE} <b>COMBATE:</b> {{challenger}} exige um duelo de buceta! Quem tem coragem por {{stake}}?",
            f"{Emojis.BOXE} <b>CHOQUE TÉRMICO:</b> {{challenger}} quer fritar uma buceta valendo {{stake}}!",
            f"{Emojis.BOXE} <b>FOGO NO PARQUINHO:</b> {{challenger}} deu o papo bucetônico por {{stake}}!",
            f"{Emojis.BOXE} <b>WRESTLING:</b> {{challenger}} tá pronto pro agarra-agarra de buceta valendo {{stake}}!",
            f"{Emojis.BOXE} <b>FIGHT CLUB:</b> Primeira regra: {{challenger}} quer o peso desse bucetão ({{stake}})!"
        ]
        COOLDOWN_PHRASES = [
            f"{Emojis.RELOGIO} Calma! Acabou de ser travado um duelo de buceta. Espere {{seconds}}s.",
            f"{Emojis.BOXE} Os punhos (e a buceta) precisam de descanso. Volte em {{seconds}}s.",
            f"{Emojis.PROIBIDO} Vício em briga de buceta? Respira {{seconds}}s aí!",
            f"{Emojis.SANGUE} A buceta tá quente do último tapa. Espera {{seconds}}s.",
            f"{Emojis.HOSPITAL} O hospital do bot tá lotado de gente lesionada por buceta. Volta daqui a {{seconds}}s."
        ]
        
        WIN_PHRASES = [
            f"{Emojis.COROA} <b>VITÓRIA:</b> {{winner}} amassou a buceta de {{loser}} e levou {{stake}} de Legado!",
            f"{Emojis.TROFEU} <b>DESTRUIÇÃO:</b> {{winner}} passou por cima da buceta de {{loser}} como um rolo compressor! Valeu {{stake}}.",
            f"{Emojis.DINO} <b>PREDAÇÃO:</b> {{winner}} devorou o bucetão de {{loser}} e engordou {{stake}}!",
            f"{Emojis.ESTRELA} <b>DOMINAÇÃO:</b> {{winner}} mostrou quem manda e limpou {{stake}} de buceta de {{loser}}!",
            f"{Emojis.ADAGA} <b>EXECUÇÃO:</b> Houve impiedade. {{loser}} definhou {{stake}} de buceta e a dignidade perante {{winner}}.",
            f"{Emojis.BOXE} <b>K.O:</b> {{winner}} deu o golpe final no bucetão! {{loser}} tá no chão menos {{stake}}.",
            f"{Emojis.FOGO} <b>ERUPÇÃO:</b> {{winner}} explodiu de força e pegou {{stake}} do bucetão de {{loser}}!",
            f"{Emojis.ESTRELA} <b>ESPETÁCULO:</b> {{winner}} brilhou no ringue. {{loser}} faliu em {{stake}} de buceta.",
            f"{Emojis.ERRO} <b>BOOM:</b> {{winner}} explodiu a buceta de {{loser}}! {{stake}} na conta.",
            f"{Emojis.SANGUE} <b>FATALITY:</b> {{winner}} arrancou {{stake}} de buceta de {{loser}} sem dó!"
        ]
        
        BTN_ACCEPT = "Aceitar"
        BTN_CANCEL = "Cancelar"
        CALLBACK_NOT_AUTHORIZED = f"{Emojis.L_ERRO} Apenas quem criou o duelo pode cancelar!"
        CALLBACK_CANCELLED = f"{Emojis.L_BANDEIRA_BRANCA} Duelo cancelado pelo criador. Arregou a buceta!"
        CALLBACK_CREATOR_POOR = f"{Emojis.L_ERRO} O criador do duelo faliu a buceta antes de alguém aceitar! Que vergonha."
        CALLBACK_SUCCESS_POPUP = f"{Emojis.L_ESTRELA} Dinheiro no bolso!"
        EXPIRED_POPUP = "Este duelo já expirou ou foi removido."
        EXPIRED_POPUP_SHORT = "Duelo expirado!"
        EXPIRED_MESSAGE = f"{Emojis.RELOGIO} <b>O DUELO MOFOU!</b> Ninguém teve coragem de encarar o desafio e o bucetão sumiu no vácuo da covardia coletiva."
        STAKE_DISPLAY = "<b>2.50kg</b>"

        @classmethod
        def get_random(cls, category, **kwargs):
            return random.choice(getattr(cls, category)).format(**kwargs)

        @classmethod
        def build_start_msg(cls, challenger_name, stake_display, seconds):
            """
            Gera o anúncio de um novo duelo de buceta no grupo.
            """
            phrase = cls.get_random('START_PHRASES', challenger=challenger_name, stake=stake_display)
            return f"{phrase}\n\n<i>{Emojis.LEGADO} Duelos usam o peso legado local.</i>"

        @classmethod
        def build_end_msg(cls, challenger_name, acceptor_name, winner_name, loser_name, stake_display):
            """Gera a mensagem de encerramento e vitória do duelo."""
            phrase = cls.get_random('WIN_PHRASES', winner=winner_name, loser=loser_name, stake=stake_display)
            return phrase

    class BctDoDia:
        NO_ACTIVE_USERS = f"{Emojis.ERRO} Nenhuma buceta deu as caras no grupo ultimamente para o sorteio!"
        NOT_ENOUGH_PLAYERS = f"{Emojis.ERRO} Precisa de pelo menos <b>2 bucetas ativas</b> pra rolar o sorteio. Convence mais alguém a <code>/pesar</code>!"

        WINNER_TEMPLATES = [
            f"{Emojis.LUCK} <b>O BUCETÃO DE OURO FOI RASPADO!</b> A sorte sorriu para a virilha de <b>{{name}}</b>, que acaba de receber uma injeção gloriosa de <b>{{gain}}kg</b> de buceta radiante direto na fonte!",
            f"{Emojis.JACKPOT} <b>JACKPOT BUCETÔNICO!</b> As máquinas travaram e o prêmio acumulado de <b>{{gain}}kg</b> de buceta pura caiu direto na conta de <b>{{name}}</b>. É o dia de glória!"
        ]
        WINNER_SELF_TEMPLATES = [
            f"{Emojis.LUCK} <b>FOI VOCÊ!</b> Que conveniente... <b>{{name}}</b> convocou o sorteio e a buceta do dia resolveu cair no próprio colo. <b>{{gain}}kg</b> de sorte suspeita.",
        ]

        @classmethod
        def get_winner_msg(cls, name, gain, is_self=False):
            templates = cls.WINNER_SELF_TEMPLATES if is_self else cls.WINNER_TEMPLATES
            return random.choice(templates).format(name=name, gain=gain)

        STATUS_TEMPLATES = [
            f"{Emojis.LUCK} <b>A BÊNÇÃO JÁ FOI DADA!</b> E adivinha? Não foi pra você. Deus tem seus preferidos, e hoje <b>{{name}}</b> sugou os preciosos <b>{{gain}}kg</b> de sorte. Fechamos o caixa, o milagre de hoje já encerrou.",
            f"{Emojis.JACKPOT} <b>O JACKPOT JÁ FOI LEVADO!</b> As luzes pararam e o prêmio evaporou. <b>{{name}}</b> já limpou a banca levando <b>{{gain}}kg</b> de buceta pura. Volte amanhã para tentar sua sorte!"
        ]
        STATUS_SELF_TEMPLATES = [
            f"{Emojis.JACKPOT} <b>JÁ ERA VOCÊ!</b> <b>{{name}}</b> já levou os <b>{{gain}}kg</b> de hoje. Veio conferir pra se exibir?",
        ]

        @classmethod
        def get_status_msg(cls, name, gain, is_self=False):
            templates = cls.STATUS_SELF_TEMPLATES if is_self else cls.STATUS_TEMPLATES
            return random.choice(templates).format(name=name, gain=gain)

    class Reset:
        """Comandos de autoridade para limpeza e reinicialização de registros."""
        ARBCT_ADMIN_ONLY = f"{Emojis.PROIBIDO} Só os ADM podem resetar a buceta dos outros, parça!"
        ARBCT_NEED_REPLY = f"{Emojis.ALERTA} É preciso responder qualquer mensagem de quem vai rodar no sistema!"
        ARBCT_SUCCESS = f"{Emojis.CLEAN} {{name}} teve a buceta zerada pela autoridade!"

    class Help:
        """
        A Enciclopédia Bucetônica.
        Central de ajuda que explica o funcionamento de cada engrenagem do bot.
        """
        MAIN = (
            f"{Emojis.FOGUETE} <b>PESA MINHA BUCETA!</b>\n\n"
            f"Toca nos botões abaixo pra entender cada função. Cada seção mostra como usar, onde funciona e o que esperar."
        )
        PESAR_LOCAL = (
            f"<b>PESAGEM LOCAL</b> {Emojis.PESO}\n\n"
            f"Pesagem por grupo — cada grupo tem seu próprio placar, streak e histórico. Você pesa uma vez por dia por grupo, acumulando peso na <b>Temporada</b> (zera trimestralmente) e no <b>Legado</b> (eterno). A streak diária aumenta o multiplicador até <b>1.35x</b>. Diferente do global, aqui você compete com quem tá no grupo.\n\n"
            f"<b>Uso:</b> <code>/pesar</code>"
        )
        PESAR_GLOBAL = (
            f"<b>RANKING GLOBAL</b> {Emojis.PLANETA}\n\n"
            f"Não existe mais pesagem global separada — o seu maior peso de <b>Temporada</b> entre todos os grupos já é o seu peso no mundo. A maior buceta de um grupo é a maior buceta do Telegram. Pesa no grupo, brilha no mundo. Vê o placar mundial no toggle Global do <code>/ranking</code>.\n\n"
            f"<b>Uso:</b> <code>/ranking</code>"
        )
        RANKING = (
            f"<b>RANKING</b> {Emojis.TROFEU}\n\n"
            f"Placar do grupo ou do mundo inteiro — você escolhe. Mostra <b>Temporada</b> e <b>Legado</b> lado a lado no mesmo card. Top 3 ganham medalhas de ouro, prata e bronze. Temporadas encerradas viram Hall da Fama permanente.\n\n"
            f"<b>Uso:</b> <code>/ranking</code>"
        )
        DUELO = (
            f"<b>DUELAR</b> {Emojis.ESPADA}\n\n"
            f"Aposta <b>2.50kg</b> do seu Legado contra outra buceta do grupo. Resultado 50/50 — vencedor leva tudo. O desafiado tem 60s pra aceitar, se não, ninguém perde nada. Cooldown de 10s entre duelos.\n\n"
            f"<b>Uso:</b> <code>/duelar</code>"
        )
        DOAR = (
            f"<b>DAR</b> {Emojis.PRESENTE}\n\n"
            f"Transfere peso do seu <b>Legado</b> pra outro membro do grupo. A doação pede confirmação antes de executar e é definitiva — sem reembolso. Aceita kg e g. Doar destrava conquistas da categoria Filantropa.\n\n"
            f"<b>Uso:</b> <code>/dar [valor]</code>"
        )
        CONQUISTAS = (
            f"<b>CONQUISTAS</b> {Emojis.TROFEU}\n\n"
            f"São 44 medalhas espalhadas em 8 categorias — Volume, Persistência, Duelos, Doações, Sorte, Misticismo e mais. Cada uma tem 4 tiers (Bronze, Prata, Ouro, Platina) e desbloqueia automaticamente por evento. A notificação chega no privado, e o grimório acumula entre todos os grupos.\n\n"
            f"<b>Uso:</b> <code>/conquistas</code>"
        )
        PERFIL = (
            f"<b>PERFIL</b> {Emojis.USER}\n\n"
            f"Seu cartão de visita bucetônico — peso de temporada, legado, ranking local, duelos, doações e patente. Toggle entre local (do grupo) e global (agregado mundial). Respondendo a mensagem de alguém, mostra o perfil da vítima.\n\n"
            f"<b>Uso:</b> <code>/perfil</code>"
        )
        BCTDODIA = (
            f"<b>BUCETA DO DIA</b> {Emojis.COROA}\n\n"
            f"Uma vez por dia, o grupo sorteia uma buceta sortuda — e ela leva <b>+7.77kg</b> direto no Legado. Só entra no sorteio quem pesou nas últimas 72h naquele grupo. Quem chamar o comando primeiro dispara o sorteio.\n\n"
            f"<b>Uso:</b> <code>/bctdodia</code>"
        )
        RESET = (
            f"<b>RESETAR BUCETA</b> {Emojis.CLEAN}\n\n"
            f"Zera o peso de alguém no grupo — só local, dados globais e conquistas ficam intactos. Ação definitiva, sem rollback. Exclusivo pra admins.\n\n"
            f"<b>Uso:</b> <code>/resetarbct</code>"
        )
        BTN_CONTACT = "Suporte"
        BTN_BACK = "Voltar"