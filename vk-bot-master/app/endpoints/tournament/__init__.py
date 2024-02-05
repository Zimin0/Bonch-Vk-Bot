from .confirmation import tournament_confirmation_endpoint
from .match import tournament_match_endpoint
from .match_chat import tournament_match_chat_endpoint
from .registration import tournament_registration_endpoint
from .round import tournament_round_endpoint
from .round_appeal import tournament_round_appeal_endpoint
from .round_winner import (tournament_round_add_winner_endpoint,
                           tournament_round_confirm_winner_endpoint,
                           tournament_round_winner_endpoint
                           )
from .tournament import tournament_endpoint
from .tournaments import tournaments_by_game_endpoint, tournaments_endpoint
from .tournaments_all import all_tournaments_endpoint
from .tournaments_allow import allow_tournaments_endpoint
from .tournaments_archive import archive_tournaments_endpoint
from .csgo import (
    tournament_csgo_peak_stage_endpoint,
    tournament_match_csgo_endpoint,
    tournament_csgo_peak_stage_select_map_endpoint,
    tournament_csgo_peak_stage_confirm_map_endpoint
)
