from pprint import pprint

from app.db import Tournament
from app.db.models.core import Match
from app.db.models.core.csgo import Csgo
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.tournament.utils import create_description_match
from app.endpoints.utils import chunks_generators


async def tournament_csgo_peak_stage_handler(state):
    data = state.message.payload_data
    session = state.aiohttp_session
    tournament = await Tournament.find_by_id(data["id"], session)
    tournament.del_grid()

    match = await tournament.get_team_match(session, data["team_id"])
    match_rounds = await match.get_match_rounds(session)
    peaks = await Csgo.get_peak_stages(session=session, match_id=match.id)

    teams_match = await match.get_teams_match(session)

    captain = False
    user_team = {}
    for team in teams_match:
        for player in team.data['players']:
            if state.user.id == player:
                user_team['id'] = team.data['id']
                user_team['name'] = team.data['name']
                if state.user.id == team.data['captain']:
                    captain = True

    description = await create_description_match(
        state,
        teams_match,
        match,
        match_rounds,
        tournament.data["number_teams_match"],
    )

    peak_text = '\n'.join(
        [f'{peak["id"]}. {peak["team"]["name"]} {peak["type"]} '
         f'{peak["map"]["name"] if peak["map"]["name"] else "-"}'
         for peak in peaks['items']]
    )
    description += (f"\nСейчас идет стадия пиков: \n"
                    f"{peak_text}")
    tournament_csgo_peak_stage_endpoint.description = description

    keyboard = []

    if captain:
        keyboard.append(
            [
                Button(
                    "tournament_csgo_peak_stage_select_map",
                    "Выбрать/Забанить карту",
                    {
                        "team": user_team,
                        "match": match.id
                    }
                )
            ]
        )
    keyboard.append(
        [BackwardButton(
            "tournament", {
                "id": data["id"]
            }
        )]
    )

    tournament_csgo_peak_stage_endpoint.keyboard = keyboard


tournament_csgo_peak_stage_endpoint = Endpoint(
    name="tournament_csgo_peak_stage",
    title="стадия пиков",
    description="стадия пиков",
    handler=tournament_csgo_peak_stage_handler,
    keyboard=None,
)


async def tournament_csgo_peak_stage_select_map_handler(state):
    data = state.message.payload_data
    session = state.aiohttp_session

    match = await Match.find_by_id(data['match'], session)

    peaks = await Csgo.get_peak_stages(session=session, match_id=match.id)

    current_peak = None
    for peak in peaks['items']:
        if peak['id'] == peaks['next_peak']:
            current_peak = peak

    peak_text = '\n'.join(
        [f'{peak["id"]}. {peak["team"]["name"]} {peak["type"]} '
         f'{peak["map"]["name"] if peak["map"]["name"] else "-"}'
         for peak in peaks['items']]
    )
    description = (f"\nСейчас идет стадия пиков: \n"
                   f"{peak_text}"
                   f"\n\nСейчас выбирает {current_peak['team']['name']}")

    tournament_csgo_peak_stage_select_map_endpoint.description = description

    keyboard = []

    if current_peak['team']['id'] == data['team']['id']:
        selected_maps_ids = [item['map']['id'] for item in peaks['items']]
        maps = await Csgo.get_maps(session)
        maps_list = [cs_map for cs_map in maps
                     if cs_map['id'] not in selected_maps_ids]
        keyboard_maps = list(
            chunks_generators(
                [Button(
                    "tournament_csgo_confirm_map",
                    f"{'Пик' if current_peak['type'] == 'peak' else 'Бан'} "
                    f"{cs_map['name']}",
                    {
                        "team": data['team'],
                        "map": cs_map,
                        "type": current_peak['type'],
                        "match": data['match']
                    }
                )
                    for cs_map in maps_list],
                2
            )
        )

        keyboard += keyboard_maps

    keyboard.append(
        [BackwardButton(
            "tournament_happening", {
                "id": match.data['tournament'],
                "team_id": data['team']['id']
            }
        )]
    )

    tournament_csgo_peak_stage_select_map_endpoint.keyboard = keyboard


tournament_csgo_peak_stage_select_map_endpoint = Endpoint(
    name="tournament_csgo_peak_stage_select_map",
    title="Пикнуть карты",
    description="стадия пиков",
    handler=tournament_csgo_peak_stage_select_map_handler,
    keyboard=None,
)


async def tournament_csgo_peak_stage_confirm_map_handler(state):
    data = state.message.payload_data
    session = state.aiohttp_session
    data = {
        "map": data["map"]["id"],
        "selected": data["type"] == "peak",
        "team": data["team"]["id"],
        "match": data["match"]
    }
    await Csgo.create_peak(session, data)
    return tournament_csgo_peak_stage_select_map_endpoint


tournament_csgo_peak_stage_confirm_map_endpoint = Endpoint(
    name="tournament_csgo_confirm_map",
    title="Пикнуть карты",
    description="стадия пиков",
    handler=tournament_csgo_peak_stage_confirm_map_handler,
    keyboard=None,
)
