from functools import lru_cache

import phonenumbers
import pycountry


@lru_cache(maxsize=1)
def country_code_choices():
    choices = []
    for calling_code, regions in sorted(
        phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items()
    ):
        if calling_code < 1:
            continue
        country_names = []
        for region in regions:
            if region == "001":
                country_names.append("International services")
                continue
            country = pycountry.countries.get(alpha_2=region)
            if country and country.name not in country_names:
                country_names.append(country.name)
        label = f"+{calling_code}"
        if country_names:
            label += f" — {country_names[0]}"
            if len(country_names) > 1:
                label += f" (+{len(country_names) - 1} shared regions)"
        choices.append((f"+{calling_code}", label))
    return tuple(choices)
