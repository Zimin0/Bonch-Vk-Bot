from app.endpoint import BackwardButton, Button
from app.endpoints.utils import chunks_generators


async def create_edu_location_keyboard(edu_location, edu_type_id, page):
    edu_location_dict = {location['name']: location
                         for location in edu_location.data}
    new_list = []
    if 'Санкт-Петербург' in edu_location_dict:
        new_list.append(edu_location_dict['Санкт-Петербург'])
        del edu_location_dict['Санкт-Петербург']

    if 'Москва' in edu_location_dict:
        new_list.append(edu_location_dict['Москва'])
        del edu_location_dict['Москва']

    for location in edu_location_dict:
        new_list.append(edu_location_dict[location])

    edu_location = list(chunks_generators(new_list, 14))
    keyboard = list(
        chunks_generators(
            [
                Button(
                    "user_verif_edu_confirm_name",
                    item["name"],
                    {
                        "edu_location_id": item["id"],
                        "edu_type_id": edu_type_id,
                    },
                )
                for item in edu_location[page]
            ],
            2,
        )
    )
    if len(edu_location) > 1:
        if page == 0:
            keyboard += [
                [
                    Button(
                        "user_verif_edu_location",
                        ">>",
                        {"edu_type_id": edu_type_id, "page": page + 1},
                    )
                ],
            ]
        elif page == len(edu_location) - 1:
            keyboard += [
                [
                    Button(
                        "user_verif_edu_location",
                        "<<",
                        {"edu_type_id": edu_type_id, "page": page - 1},
                    )
                ],
            ]
        else:
            keyboard += [
                [
                    Button(
                        "user_verif_edu_location",
                        "<<",
                        {"edu_type_id": edu_type_id, "page": page - 1},
                    ),
                    Button(
                        "user_verif_edu_location",
                        ">>",
                        {"edu_type_id": edu_type_id, "page": page + 1},
                    ),
                ],
            ]

    keyboard += [
        [BackwardButton("user_verif_edu_type")],
    ]
    return keyboard
