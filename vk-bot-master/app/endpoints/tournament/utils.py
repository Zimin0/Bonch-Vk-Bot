import collections
from pprint import pprint

from app import User
from app.db import Game, Team
from app.db.utils import Time
from app.endpoint import BackwardButton, Button
from app.endpoints.utils import chunks_generators
from app.settings import CORE_API_URL
from app.vk import get_upload_server, upload_photo

event_name = {
    1: "Зарегистрироваться",
    2: "Подтвердить участие",
    3: "Текущий матч",
}

en_event_name = {
    1: "registration",
    2: "confirmation",
    3: "happening",
}

tournament_buttons = (
    ("Информация о турнире", "detail"),
    ("Список участников", "players"),
    ("Турнирная сетка", "grid"),
)


async def add_current_event_buttons(current_event, tournament, id_user_team):
    return [
        Button(
            "tournament_" + str(en_event_name[current_event]),
            event_name[current_event],
            {
                "id"     : tournament.data["id"],
                "team_id": id_user_team,
            },
        )
    ]


def is_team_registration(current_event, ids_user_teams, tournament):
    return current_event == 1 and not (
            set(ids_user_teams) & set(tournament.data["registered_teams"])
    )


def is_team_confirmation(current_event, ids_user_teams, tournament):
    return current_event == 2 and not (
            set(ids_user_teams) & set(tournament.data["confirmed_teams"]))


async def is_team_participates(
        state, current_event, ids_user_teams, tournament
):
    teams = list(set(ids_user_teams) & set(tournament.data["confirmed_teams"]))
    if current_event == 3 and teams:
        match = await tournament.get_team_match(
            state.aiohttp_session, teams[0]
        )
        if match.data:
            return teams[0]
    return None


async def create_buttons_current_event(
        current_event, ids_user_teams, tournament, ids_allowed_teams, state
):
    if current_event:
        if current_event in event_name:
            if is_team_registration(current_event, ids_user_teams, tournament):
                teams = list(set(ids_user_teams) & set(ids_allowed_teams))
                return await add_current_event_buttons(
                    current_event, tournament, teams
                )
            if is_team_confirmation(current_event, ids_user_teams, tournament):
                teams = list(set(ids_user_teams) & set(ids_allowed_teams))
                if not teams:
                    teams = [None]

                return await add_current_event_buttons(
                    current_event, tournament, teams[0]
                )
            team_participates = await is_team_participates(
                state, current_event, ids_user_teams, tournament
            )
            if team_participates:
                return await add_current_event_buttons(
                    current_event, tournament, team_participates
                )
    return []


async def create_keyboard_tournament(tournament, state):
    data = state.message.payload_data
    current_event = await tournament.get_current_event(state.aiohttp_session)

    if current_event:
        current_event = current_event["type"]

    if current_event == 1:
        allowed_teams = await tournament.get_allowed_register_teams(
            state.aiohttp_session
        )
        ids_allowed_teams = [team.data["id"] for team in allowed_teams]
    else:
        ids_allowed_teams = tournament.data['registered_teams']

    if current_event == 3:
        user_teams = await state.user.get_teams(state.aiohttp_session)
    else:
        user_teams = await state.user.get_captain_teams(state.aiohttp_session)
    ids_user_teams = [team.data["id"] for team in user_teams]

    keyboard = await create_buttons_current_event(
        current_event, ids_user_teams, tournament, ids_allowed_teams, state
    )
    for button in tournament_buttons:
        keyboard.append(
            Button(
                "tournament",
                button[0],
                {
                    "id"  : data["id"],
                    "info": button[1]
                },
            )
        )
    keyboard = list(chunks_generators(keyboard, 2))
    game = await Game.find_by_id(
        tournament.data['game'], state.aiohttp_session
    )
    keyboard += [[
        BackwardButton(
            "tournaments",
            payload={
                'game_id': tournament.data['game'],
                'game_name': game.data['name']
            }
        )
    ]]
    return keyboard


async def select_team_names(match, team_names):
    teams_name = []
    for team in match["teams"]:
        team["name"] = team["name"].replace('$', '')
        if team["name"] in team_names:
            team["name"] = team_names[team["name"]]
        if "winner" in match:
            if team["id"] == match["winner"]:
                team["name"] = "(w) " + team["name"]
        teams_name.append(team["name"])
    while len(teams_name) < 2:
        teams_name.append(" TBA ")
    return teams_name


async def create_tournament_grid(state, tournament):
    grid = tournament.get_grid()
    if grid:
        return grid

    link = CORE_API_URL + f"tournaments/grid/{tournament.id}/"
    try:
        async with state.aiohttp_session.get(link) as resp:
            if resp.status != 200:
                return "Отсутствует"
            image = await resp.read()
    except Exception:
        return "Отсутствует"
    attachment = await upload_photo(
        state.aiohttp_session,
        state.message.peer_id,
        image
    )

    if tournament.data['winner']:
        tournament.set_grid(attachment, Time.MONTH)
    else:
        tournament.set_grid(attachment)
    return attachment


async def create_description_tournaments(state, tournament):
    data = state.message.payload_data
    if data["info"] == "detail":
        return tournament.data["description"]
    if data["info"] == "players":
        tournament_players = await tournament.get_string_name_teams(state)
        if not tournament_players:
            return "Тут пока что никого нету"
        res = [f"{count + 1}. {tournament_players[team]}"
               for count, team in enumerate(tournament_players)]
        return "\n".join(res)

    if data["info"] == "grid":
        current_event = await tournament.get_current_event(
            state.aiohttp_session
        )
        if not tournament.data['winner']:
            if not current_event:
                return "Турнирная сетка генерируется после начала турнира"

            if current_event['type'] != 3:
                return "Турнирная сетка генерируется после начала турнира"

        grid = await create_tournament_grid(state, tournament)
        return grid
    return ""


async def create_description_match(
        state, match_teams, match, match_rounds, count_teams
):
    if match.data["number"] == 1:
        stage = "Финал"
    else:
        stage = f"1/{2 ** (match.data['number'] - 1)}"
    description = (
        f"-----------Матч-----------\n"
        f"Стадия - {stage} "
        f"(BO{len(match_rounds)})\n\n"
    )
    teams_name = {team.data["id"]: team.data["name"] for team in match_teams}
    for m_round in match_rounds:
        if m_round.data["winner"]:
            description += (
                f"В {m_round.data['number']} раунде "
                f"победил {teams_name[m_round.data['winner']]}\n"
            )
    for team in match_teams:
        description += f"\nСостав команды {team.data['name']}:\n"
        players = await team.get_string_name_players(state)
        players = "\n".join(players)
        description += f"{players}\n\n"
    if len(match_teams) < count_teams:
        description += "\nВаш соперник еще не определен!\n"
    return description


async def create_keyboard_match(
        match_rounds, match, data, teams_match, count_teams, is_captain
):
    keyboard = []
    if len(teams_match) >= count_teams and is_captain:
        current_rounds = {
            match_round.data["number"]: match_round
            for match_round in match_rounds
            if match_round.data["winner"] is None
        }
        current_round = current_rounds[min(current_rounds.keys())]
        keyboard += [
            Button(
                "tournament_round",
                "Текущий раунд",
                {
                    **data,
                    **{
                        "round_id": current_round.data["id"],
                        "match_id": match.data["id"],
                    },
                },
            ),
            Button(
                "tournament_round_appeal_winner",
                "Вызвать судью",
                {
                    **data,
                    **{
                        "match_id": match.data["id"],
                    },
                },
            ),
        ]

    keyboard.append(
        Button(
            "tournament_match_chat",
            "Беседа матча",
            {
                **data, **{
                "match_id": match.data["id"]
            }
            },
        )
    )
    keyboard = list(chunks_generators(keyboard, 2))
    keyboard += [
        [BackwardButton(
            "tournament", {
                "id": data["id"]
            }
        )],
    ]
    return keyboard


async def create_keyboard_confirm_round_winner(
        state, data, t_round, round_winner
):
    round_winner = await t_round.get_winning_team(
        state.aiohttp_session, round_winner[0]
    )
    return [
        [
            Button(
                "tournament_round_confirm_winner",
                "Подтвердить",
                {
                    **data,
                    **{
                        "team_winner_id": round_winner.data["id"],
                        "round_id"      : t_round.data["id"],
                    },
                },
            ),
            Button("tournament_round_appeal_winner", "Аппелировать", data),
        ]
    ]


async def create_keyboard_select_round_winner(data, teams_round):
    return list(
        chunks_generators(
            [
                Button(
                    "tournament_round_add_winner",
                    item.data["name"],
                    {
                        **data, **{
                        "team_winner_id": item.data["id"]
                    }
                    },
                )
                for item in teams_round
            ],
            2,
        )
    )


async def create_keyboard_round_winner(
        state, round_winner, data, t_round, teams_round
):
    keyboard = []
    if round_winner:
        if str(data["team_id"]) not in round_winner:
            keyboard = await create_keyboard_confirm_round_winner(
                state, data, t_round, round_winner
            )
    else:
        keyboard = await create_keyboard_select_round_winner(data, teams_round)
    keyboard += [
        [
            BackwardButton(
                "tournament_round",
                data,
            )
        ],
    ]
    return keyboard


async def create_description_round_winner(state, round_winner, data, t_round):
    if round_winner:
        if str(data["team_id"]) in round_winner:
            return (
                "Вы ввели результат,"
                " ожидайте подтверждения от вашего соперника."
            )
        round_winner = await t_round.get_winning_team(
            state.aiohttp_session, round_winner[0]
        )
        return (
            f"Ваш соперник уже ввел результаты раунда!\n"
            f"Победитель - {round_winner.data['name']}?"
        )
    return f"Кто выиграл в {t_round.data['number']} раунде?"


async def send_round_results(state, team_id):
    data = state.message.payload_data
    team = await Team.find_by_id(team_id, state.aiohttp_session)
    captain = await User.find_by_id(
        team.data["captain"], state.aiohttp_session
    )
    state_data = data.copy()
    state_data["team_id"] = team_id
    data = {
        "text"     : "Ваш соперник ввел результаты раунда!",
        "endpoints": [
            {
                "name"   : "tournament_round_winner",
                "title"  : "Посмотреть",
                "payload": state_data,
            }
        ],
    }
    await captain.send_notification(state.aiohttp_session, data)


async def create_tournaments_keyboard(tournaments, data, endpoint_name, game_id):
    page = 0
    if data:
        if 'page' in data:
            page = data['page']

    keyboard = []

    if len(tournaments) >= 1:
        tournaments = list(chunks_generators(tournaments, 8))

        keyboard = list(
            chunks_generators(
                [Button(
                    "tournament", item["name"], {
                        "id": item["id"]
                    }
                )
                    for item in tournaments[page]],
                2,
            )
        )
        if len(tournaments) > 1:
            if page == 0:
                keyboard += [
                    [Button(
                        endpoint_name, ">>", {
                            "page": page + 1,
                            "game_id": game_id
                        }
                    )],
                ]
            elif page == len(tournaments) - 1:
                keyboard += [
                    [Button(
                        endpoint_name, "<<", {
                            "page": page - 1,
                            "game_id": game_id
                        }
                    )],
                ]
            else:
                keyboard += [
                    [Button(
                        endpoint_name, "<<", {
                            "page": page - 1,
                            "game_id": game_id
                        }
                    ),
                        Button(
                            endpoint_name, ">>", {
                                "page": page + 1,
                                "game_id": game_id
                            }
                        )],
                ]

    keyboard.append([BackwardButton("tournaments_by_game")])
    return keyboard
