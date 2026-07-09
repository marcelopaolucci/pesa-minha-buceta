from .ajuda import cmd_ajuda, cmd_start, welcome_new_chat, process_help_callback
from .conquistas import cmd_conquistas, callback_show_achievements, process_achievements_callback
from .pesar import cmd_pesar, on_pesar_btn_ranking, on_pesar_btn_perfil
from .ranking import cmd_ranking
from .resetarbct import cmd_resetarbct
from .doar import cmd_doar, callback_dar
from .duelar import cmd_duelar, callback_duelo
from .admin import cmd_injetar, cmd_finalizar_temporada, cmd_anunciar, on_bot_chat_member, cmd_verificar_grupos
from .perfil import cmd_perfil, on_perfil_btn_local, on_perfil_btn_global
from .ping import cmd_ping
from .bctdodia import cmd_bctdodia
from .triggers import router as triggers_router