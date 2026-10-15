from planet_classifier import PlanetClassifier


def get_planet_type(mass, radius):
    if mass is None or radius is None:
        return {
            'type_ru': 'Неизвестный тип',
            'type_en': 'Unknown type',
            'description_ru': '',
            'description_en': '',
            'color_hint_ru': '',
            'color_hint_en': ''
        }

    classifier = PlanetClassifier()
    return classifier.classify(mass, radius)


def get_atmosphere_info(temp):
    if temp is None:
        return None

    classifier = PlanetClassifier()
    return classifier.get_atmosphere_by_temp(temp)


def get_star_influence(spectral_type):
    classifier = PlanetClassifier()
    return classifier.get_star_influence(spectral_type)


def generate_prompt(planet_data, star_data):
    classifier = PlanetClassifier()
    return classifier.generate_prompts(planet_data, star_data)


def round_value(value, decimals=2):
    if value is None:
        return None
    return round(value, decimals)