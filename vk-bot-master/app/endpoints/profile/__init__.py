from .profile import endpoint as profile_endpoint
from .user_verification import (user_verif_edu_confirm_name_endpoint,
                                user_verif_edu_location_endpoint,
                                user_verif_edu_type_endpoint,
                                user_verif_endpoint
                                )
from .notification_settings import user_notification_settings_endpoint
from .games_accounts import (
    add_game_accounts_endpoint,
    add_clash_royale_account_endpoint,
    clash_royale_account_confirmation_endpoint,
    add_steam_account_endpoint,
    add_battlenet_account_endpoint
)
