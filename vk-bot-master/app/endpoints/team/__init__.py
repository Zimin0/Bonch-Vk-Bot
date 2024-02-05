from .add_player import add_player as team_add_player_endpoint
from .add_player import add_player_confirm as team_add_player_confirm_endpoint
from .add_player import (add_player_invite_endpoint,
                         team_add_player_invite_accept_endpoint)
from .create_team import \
    create_team_confirm_name as team_create_team_confirm_name_endpoint
from .create_team import \
    create_team_enter_name as team_create_enter_name_endpoint
from .create_team import \
    create_team_select_game as team_create_select_game_endpoint
from .create_team import \
    create_team_select_player_count as team_create_team_player_count_endpoint
from .disband_team import disband as team_disband_endpoint
from .kick_player import kick_player as team_kick_player_endpoint
from .kick_player import \
    kick_player_confirm as team_kick_player_confirm_endpoint
from .new_captain import new_captain as team_new_captain_endpoint
from .new_captain import \
    new_captain_confirm as team_new_captain_confirm_endpoint
from .team import team_endpoint
from .team import team_list as team_list_endpoint
from .teams import teams as teams_endpoint, \
    teams_by_game as teams_by_game_endpoint
