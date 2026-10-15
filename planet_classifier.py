PLANET_TYPES = [
    {
        "name_ru": "Каменная (землеподобная)",
        "name_en": "Rocky (Earth-like)",
        "min_mass": 0.1, "max_mass": 5,
        "min_radius": 0.5, "max_radius": 1.6,
        "density_range": (4.0, 8.0),
        "description_ru": "Твёрдая каменистая поверхность с тонкой атмосферой.",
        "description_en": "Solid rocky surface with a thin atmosphere.",
        "color_hint_ru": "серо-голубая поверхность с коричневыми участками суши",
        "color_hint_en": "grayish-blue surface with brown landmasses",
    },
    {
        "name_ru": "Суперземля",
        "name_en": "Super-Earth",
        "min_mass": 2, "max_mass": 15,
        "min_radius": 1.2, "max_radius": 2.5,
        "density_range": (3.5, 10.0),
        "description_ru": "Каменистая планета с плотной атмосферой из водорода, гелия и водяного пара.",
        "description_en": "Rocky planet with a dense atmosphere of hydrogen, helium, and water vapor.",
        "color_hint_ru": "серо-синяя планета с плотными белыми облаками",
        "color_hint_en": "gray-blue planet with dense white clouds",
    },
    {
        "name_ru": "Мини-Нептун / газовый карлик",
        "name_en": "Mini-Neptune / Gas dwarf",
        "min_mass": 5, "max_mass": 40,
        "min_radius": 2.0, "max_radius": 6.0,
        "density_range": (0.8, 3.5),
        "description_ru": "Газовая планета с глубокой водородно-гелиевой атмосферой и облаками из метана и аммиака.",
        "description_en": "Gaseous planet with a deep hydrogen-helium atmosphere and methane/ammonia clouds.",
        "color_hint_ru": "синевато-зелёный шар с высотной дымкой",
        "color_hint_en": "bluish-green sphere with high-altitude haze",
    },
    {
        "name_ru": "Нептуноподобный (ледяной гигант)",
        "name_en": "Neptune-like (ice giant)",
        "min_mass": 10, "max_mass": 100,
        "min_radius": 3.5, "max_radius": 8.0,
        "density_range": (0.6, 2.0),
        "description_ru": "Ледяной гигант с атмосферой из водорода, гелия и метана, придающего насыщенный синий цвет.",
        "description_en": "Ice giant with a hydrogen-helium-methane atmosphere giving it a deep blue color.",
        "color_hint_ru": "насыщенный синий цвет с белыми облачными полосами",
        "color_hint_en": "deep blue color with white cloud bands",
    },
    {
        "name_ru": "Юпитероподобный (газовый гигант)",
        "name_en": "Jupiter-like (gas giant)",
        "min_mass": 50, "max_mass": 3000,
        "min_radius": 6.0, "max_radius": 20,
        "density_range": (0.2, 1.5),
        "description_ru": "Массивный газовый гигант с глубокой атмосферой из водорода и гелия, с облачными полосами и вихрями.",
        "description_en": "Massive gas giant with a deep hydrogen-helium atmosphere, cloud bands, and storms.",
        "color_hint_ru": "жёлто-коричневые и белые полосы, как у Юпитера",
        "color_hint_en": "yellow-brown and white bands, similar to Jupiter",
    },
    {
        "name_ru": "Горячий Юпитер",
        "name_en": "Hot Jupiter",
        "min_mass": 50, "max_mass": 5000,
        "min_radius": 8, "max_radius": 25,
        "density_range": (0.05, 0.8),
        "description_ru": "Раскалённый газовый гигант с раздутой атмосферой из тёмных облаков силикатов и железа.",
        "description_en": "Scorching gas giant with an inflated atmosphere of dark silicate and iron clouds.",
        "color_hint_ru": "тёмно-красный и коричневый с яркими горячими пятнами",
        "color_hint_en": "dark red and brown with bright hot spots",
    },
    {
        "name_ru": "Сверхмассивный газовый гигант",
        "name_en": "Super-massive gas giant",
        "min_mass": 1000, "max_mass": 20000,
        "min_radius": 10, "max_radius": 30,
        "density_range": (0.1, 2.0),
        "description_ru": "Огромная планета на грани коричневого карлика, с экстремальной гравитацией и тёмной атмосферой.",
        "description_en": "Enormous planet on the edge of a brown dwarf, with extreme gravity and a dark atmosphere.",
        "color_hint_ru": "тёмно-коричневый с красными оттенками",
        "color_hint_en": "dark brown with red tones",
    },
]

TEMPERATURE_ATMOSPHERE = [
    {
        "temp_min": 0, "temp_max": 400,
        "components_ru": "атмосфера из метана и азота с облаками из метанового льда",
        "components_en": "methane and nitrogen atmosphere with methane ice clouds",
        "color_hint_ru": "голубовато-зелёный шар с высотной дымкой",
        "color_hint_en": "bluish-green sphere with high-altitude haze",
    },
    {
        "temp_min": 400, "temp_max": 700,
        "components_ru": "плотная атмосфера из водяного пара и CO₂ с белыми облаками",
        "components_en": "dense atmosphere of water vapor and CO₂ with white clouds",
        "color_hint_ru": "белые плотные облака, серо-голубая поверхность",
        "color_hint_en": "dense white clouds, gray-blue surface",
    },
    {
        "temp_min": 700, "temp_max": 1200,
        "components_ru": "атмосфера из водяного пара, CO и CO₂ с жёлто-коричневыми облаками сульфидов",
        "components_en": "atmosphere of water vapor, CO, and CO₂ with yellow-brown sulfide clouds",
        "color_hint_ru": "жёлто-коричневые непрозрачные облака",
        "color_hint_en": "yellow-brown opaque clouds",
    },
    {
        "temp_min": 1200, "temp_max": 1800,
        "components_ru": "атмосфера из силикатов и железа с тёмными облаками",
        "components_en": "atmosphere of silicates and iron with dark clouds",
        "color_hint_ru": "тёмные облака с красновато-коричневым свечением",
        "color_hint_en": "dark clouds with reddish-brown glow",
    },
    {
        "temp_min": 1800, "temp_max": 5000,
        "components_ru": "атмосфера из паров металлов (железо, титан, ванадий) с облаками корунда",
        "components_en": "atmosphere of metal vapors (iron, titanium, vanadium) with corundum clouds",
        "color_hint_ru": "очень тёмная планета с красным свечением",
        "color_hint_en": "very dark planet with red glow",
    },
]

STAR_DATA = {
    "O": {"influence_ru": "интенсивное ультрафиолетовое и синее излучение", "influence_en": "intense ultraviolet and blue radiation", "color": "#9bb0ff"},
    "B": {"influence_ru": "сине-фиолетовое освещение", "influence_en": "blue-violet illumination", "color": "#a0b0ff"},
    "A": {"influence_ru": "голубовато-белое освещение", "influence_en": "bluish-white illumination", "color": "#dbeaff"},
    "F": {"influence_ru": "яркий белый свет с лёгким голубым оттенком", "influence_en": "bright white light with a slight blue cast", "color": "#f0f8ff"},
    "G": {"influence_ru": "бело-жёлтый свет, похожий на солнечный", "influence_en": "white-yellow light, similar to sunlight", "color": "#fff4cc"},
    "K": {"influence_ru": "оранжевый оттенок освещения", "influence_en": "orange-tinted illumination", "color": "#ffd9a3"},
    "M": {"influence_ru": "красноватый свет", "influence_en": "reddish light", "color": "#ff9999"},
    "D": {"influence_ru": "яркий белый свет", "influence_en": "bright white light", "color": "#e8f4fd"},
    "L": {"influence_ru": "тусклый красноватый свет", "influence_en": "dim reddish light", "color": "#cc6633"},
    "T": {"influence_ru": "очень тусклый инфракрасный свет", "influence_en": "very dim infrared light", "color": "#663300"},
    "Y": {"influence_ru": "практически невидимый свет", "influence_en": "nearly invisible light", "color": "#331100"},
}


def _extract_spectral_class(spectral_type):
    if not spectral_type:
        return None
    st = spectral_type.strip().upper()
    valid_classes = ["O", "B", "A", "F", "G", "K", "M", "D", "L", "T", "Y"]
    for cls in valid_classes:
        if cls in st:
            return cls
    first_char = st[0] if st else None
    if first_char in valid_classes:
        return first_char
    return None


class PlanetClassifier:

    @staticmethod
    def classify(mass_earth, radius_earth):
        if mass_earth is None or radius_earth is None or mass_earth <= 0 or radius_earth <= 0:
            return {
                "type_ru": "Неизвестный тип",
                "description_ru": "",
                "color_hint_ru": "",
                "type_en": "Unknown type",
                "description_en": "",
                "color_hint_en": "",
                "density": None
            }

        density = mass_earth / (radius_earth ** 3) * 5.51

        for ptype in PLANET_TYPES:
            if (ptype["min_mass"] <= mass_earth <= ptype["max_mass"] and
                ptype["min_radius"] <= radius_earth <= ptype["max_radius"]):
                d_min, d_max = ptype["density_range"]
                if d_min <= density <= d_max:
                    return {
                        "type_ru": ptype["name_ru"],
                        "description_ru": ptype["description_ru"],
                        "color_hint_ru": ptype["color_hint_ru"],
                        "type_en": ptype["name_en"],
                        "description_en": ptype["description_en"],
                        "color_hint_en": ptype["color_hint_en"],
                        "density": density
                    }

        for ptype in PLANET_TYPES:
            if (ptype["min_mass"] <= mass_earth <= ptype["max_mass"] and
                ptype["min_radius"] <= radius_earth <= ptype["max_radius"]):
                return {
                    "type_ru": ptype["name_ru"],
                    "description_ru": ptype["description_ru"],
                    "color_hint_ru": ptype["color_hint_ru"],
                    "type_en": ptype["name_en"],
                    "description_en": ptype["description_en"],
                    "color_hint_en": ptype["color_hint_en"],
                    "density": density
                }

        for ptype in PLANET_TYPES:
            d_min, d_max = ptype["density_range"]
            if d_min <= density <= d_max:
                return {
                    "type_ru": ptype["name_ru"] + " (по плотности)",
                    "description_ru": ptype["description_ru"],
                    "color_hint_ru": ptype["color_hint_ru"],
                    "type_en": ptype["name_en"] + " (by density)",
                    "description_en": ptype["description_en"],
                    "color_hint_en": ptype["color_hint_en"],
                    "density": density
                }

        if mass_earth < 5:
            return {
                "type_ru": "Каменная планета",
                "description_ru": "Маленькая планета с твёрдой поверхностью.",
                "color_hint_ru": "серо-голубая",
                "type_en": "Rocky planet",
                "description_en": "Small planet with solid surface.",
                "color_hint_en": "gray-blue",
                "density": density
            }
        elif mass_earth < 50:
            return {
                "type_ru": "Суперземля / Мини-Нептун",
                "description_ru": "Промежуточная планета с плотной атмосферой.",
                "color_hint_ru": "синеватая с облаками",
                "type_en": "Super-Earth / Mini-Neptune",
                "description_en": "Intermediate planet with dense atmosphere.",
                "color_hint_en": "bluish with clouds",
                "density": density
            }
        else:
            return {
                "type_ru": "Газовый гигант",
                "description_ru": "Массивная планета с глубокой атмосферой.",
                "color_hint_ru": "жёлто-коричневая",
                "type_en": "Gas giant",
                "description_en": "Massive planet with deep atmosphere.",
                "color_hint_en": "yellow-brown",
                "density": density
            }

    @staticmethod
    def get_atmosphere_by_temp(temp_k):
        if temp_k is None or temp_k <= 0:
            return None
        for rang in TEMPERATURE_ATMOSPHERE:
            if rang["temp_min"] <= temp_k < rang["temp_max"]:
                return {
                    "components_ru": rang["components_ru"],
                    "color_hint_ru": rang["color_hint_ru"],
                    "components_en": rang["components_en"],
                    "color_hint_en": rang["color_hint_en"]
                }
        last = TEMPERATURE_ATMOSPHERE[-1]
        return {
            "components_ru": last["components_ru"],
            "color_hint_ru": last["color_hint_ru"],
            "components_en": last["components_en"],
            "color_hint_en": last["color_hint_en"]
        }

    @staticmethod
    def get_star_influence(spectral_type):
        cls = _extract_spectral_class(spectral_type)
        if not cls:
            return "белое освещение", "white lighting"
        data = STAR_DATA.get(cls, {"influence_ru": "белое освещение", "influence_en": "white lighting"})
        return data["influence_ru"], data["influence_en"]

    @staticmethod
    def get_star_color(spectral_type):
        cls = _extract_spectral_class(spectral_type)
        if not cls:
            return "#f0f8ff"
        return STAR_DATA.get(cls, {}).get("color", "#f0f8ff")

    @staticmethod
    def generate_prompts(planet_row, star_row):
        mass = planet_row.get("pl_bmasse") or planet_row.get("pl_masse")
        radius = planet_row.get("pl_rade")
        temp = planet_row.get("pl_eqt")

        classification = PlanetClassifier.classify(mass, radius)
        atm = PlanetClassifier.get_atmosphere_by_temp(temp) if temp else None
        star_ru, star_en = PlanetClassifier.get_star_influence(star_row.get("st_spectype"))

        ru_parts = []
        ru_parts.append(f"Научная визуализация экзопланеты типа '{classification['type_ru']}'.")
        ru_parts.append(classification["description_ru"])

        if atm:
            ru_parts.append(f"Атмосфера состоит из: {atm['components_ru']}.")
            ru_parts.append(f"Внешний вид: {atm['color_hint_ru']}.")

        if temp is not None:
            if temp < 300:
                ru_parts.append("Поверхность покрыта льдом, холодный мир с бледными тонами.")
            elif temp < 600:
                ru_parts.append("Умеренный климат, плотные белые облака, серо-голубая поверхность.")
            elif temp < 1200:
                ru_parts.append("Горячая атмосфера с густыми жёлто-коричневыми облаками.")
            elif temp < 2000:
                ru_parts.append("Раскалённая поверхность с тёмными облаками и красным свечением.")
            else:
                ru_parts.append("Экстремально горячая планета с тёмной атмосферой и красным свечением.")

        if radius is not None:
            if radius < 1.5:
                ru_parts.append("Небольшая каменистая планета, размером с Землю или Марс.")
            elif radius < 4:
                ru_parts.append("Планета средних размеров, крупнее Земли.")
            elif radius < 10:
                ru_parts.append("Крупный газовый гигант, сравнимый с Сатурном или Юпитером.")
            else:
                ru_parts.append("Огромный сверх-Юпитер.")

        ru_parts.append(f"Планета освещена родительской звездой: {star_ru}.")
        ru_prompt = " ".join(ru_parts)

        style = (
            "A realistic scientific visualization of an exoplanet, "
            "in the style of NASA astronomical illustrations and "
            "professional space documentaries. Photorealistic rendering, "
            "physically accurate, no fantasy elements, no artistic embellishments."
        )

        subject = f"The planet is a {classification['type_en'].lower()}."

        surface_desc = ""
        if temp is not None:
            if temp < 300:
                surface_desc = (
                    "The surface is frozen and icy, with blue-white tones. "
                    "Thin atmosphere with methane and nitrogen ice crystals. "
                    "Cold, distant world with pale colors."
                )
            elif temp < 600:
                surface_desc = (
                    "A temperate world with dense white water-vapor clouds. "
                    "Gray-blue surface tones visible through gaps in the clouds. "
                    "Earth-like appearance with thick cloud cover."
                )
            elif temp < 1200:
                surface_desc = (
                    "A hot planet with thick yellow-brown cloud layers of sulfides. "
                    "Opaque atmosphere of water vapor, CO, and CO₂. "
                    "No visible surface through the dense atmosphere."
                )
            elif temp < 2000:
                surface_desc = (
                    "An extremely hot world with dark reddish-brown clouds "
                    "of silicates and iron. Faint molten glow visible through "
                    "gaps in the cloud cover. Menacing appearance."
                )
            else:
                surface_desc = (
                    "A hellish ultra-hot planet with metal vapor atmosphere "
                    "of iron and titanium oxide. Deep red and infrared glow. "
                    "Dark, ominous, with glowing hot spots on the surface."
                )
        else:
            if atm:
                surface_desc = f"The planet has {atm['components_en']}. Appearance: {atm['color_hint_en']}."
            else:
                surface_desc = f"{classification['description_en']}"

        size_desc = ""
        if radius is not None:
            if radius < 1.5:
                size_desc = "A small rocky world, similar in size to Earth or Mars."
            elif radius < 4:
                size_desc = "A medium-sized planet, larger than Earth but smaller than Neptune."
            elif radius < 10:
                size_desc = "A large gas giant, comparable to Saturn or Jupiter in our solar system."
            else:
                size_desc = "A massive super-Jupiter, enormous and imposing."

        lighting = (
            f"The planet is illuminated by its parent star with {star_en.lower()}. "
            f"Realistic lighting with a visible day-night terminator."
        )

        composition = (
            "The planet is shown as a full sphere viewed from space, "
            "occupying most of the frame. The background is deep space "
            "with distant stars and subtle nebula hints. "
            "The star is visible as a bright light source just outside the frame, "
            "casting realistic shadows and atmospheric scattering."
        )

        quality = (
            "Ultra high resolution, 8K detail, sharp focus, "
            "scientifically accurate colors and lighting. "
            "Professional astronomical illustration."
        )

        en_prompt = " ".join([style, subject, surface_desc, size_desc, lighting, composition, quality])

        return {"ru": ru_prompt, "en": en_prompt}