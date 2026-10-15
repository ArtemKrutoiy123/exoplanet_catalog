import os
import re
import streamlit as st
import requests
from urllib.parse import urlencode
from config import API_BASE_URL
from config import DEFAULT_PER_PAGE
from planet_classifier import PlanetClassifier

st.set_page_config(page_title="Каталог экзопланет", layout="wide", page_icon="logo.png")


@st.cache_data
def load_css_content():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()


css_content = load_css_content()
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None

if "page_num" not in st.session_state:
    st.session_state.page_num = 1


@st.cache_data(ttl=60, show_spinner=False)
def api_get(endpoint, params=None):
    url = f"{API_BASE_URL}{endpoint}"
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return None


def api_post(endpoint, data, params=None, method="POST", timeout=10):
    url = f"{API_BASE_URL}{endpoint}"
    if params:
        url += "?" + urlencode(params)

    if method == "PUT":
        resp = requests.put(url, json=data, timeout=timeout)
    elif method == "DELETE":
        resp = requests.delete(url, timeout=timeout)
    else:
        resp = requests.post(url, json=data, timeout=timeout)

    if resp.status_code == 200:
        return resp.json()
    else:
        try:
            error_data = resp.json()
            return {"error": True, "detail": error_data.get("detail", "Неизвестная ошибка"), "status_code": resp.status_code}
        except:
            return {"error": True, "detail": f"HTTP {resp.status_code}", "status_code": resp.status_code}


def validate_username(username):
    if not username or len(username) < 3 or len(username) > 50:
        return False, "Имя должно содержать от 3 до 50 символов"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Имя может содержать только буквы, цифры и подчёркивания"
    return True, ""


def validate_email(email):
    if not email:
        return False, "Email обязателен"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Введите корректный email (например: user@example.com)"
    return True, ""


def validate_password(password):
    if not password or len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    return True, ""


def show_header():
    logo_col, title_col, user_col = st.columns([0.5, 2, 1])

    with logo_col:
        st.image("logo.png", width=100)

    with title_col:
        header_html = '<div class="header-logo-text" style="padding-top: 0.5rem;">Каталог экзопланет</div>'
        st.markdown(header_html, unsafe_allow_html=True)

    with user_col:
        if st.session_state.logged_in:
            if st.session_state.role == "admin":
                role_badge = "[Админ]"
            else:
                role_badge = "[Пользователь]"

            user_html = f"""
                <div class="user-info" style="text-align: right; padding-top: 0.5rem;">
                    {role_badge} <strong>{st.session_state.username}</strong>
                </div>
            """
            st.markdown(user_html, unsafe_allow_html=True)

            if st.button("Выйти", key="logout_btn"):
                st.session_state.update({
                    "logged_in": False,
                    "user_id": None,
                    "username": None,
                    "role": None
                })
                st.session_state.page = "login"
                st.rerun()
        else:
            st.markdown(
                '<div class="user-info" style="text-align: right; padding-top: 0.5rem;">Не авторизован</div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)


def get_planet_color(planet_type_ru):
    color_map = {
        "Каменная (землеподобная)": "#4facfe",
        "Суперземля": "#3b9eff",
        "Мини-Нептун": "#6c8cbf",
        "Нептуноподобный": "#2c6e9e",
        "Юпитероподобный": "#d4a373",
        "Горячий Юпитер": "#bc6c25",
        "Каменная планета": "#5dade2",
        "Газовый гигант": "#d68910",
        "Сверхмассивный газовый гигант": "#7d3c98",
    }
    for key, col in color_map.items():
        if key in planet_type_ru:
            return col
    return "#95a5a6"


def get_card_bg_color(planet_type_ru):
    color_map = {
        "Каменная (землеподобная)": "rgba(30, 60, 90, 0.6)",
        "Суперземля": "rgba(25, 50, 85, 0.6)",
        "Мини-Нептун": "rgba(35, 55, 80, 0.6)",
        "Нептуноподобный": "rgba(20, 45, 75, 0.6)",
        "Юпитероподобный": "rgba(70, 50, 30, 0.6)",
        "Горячий Юпитер": "rgba(80, 40, 25, 0.6)",
        "Каменная планета": "rgba(30, 55, 85, 0.6)",
        "Газовый гигант": "rgba(65, 45, 25, 0.6)",
        "Сверхмассивный газовый гигант": "rgba(50, 30, 60, 0.6)",
    }
    for key, col in color_map.items():
        if key in planet_type_ru:
            return col
    return "rgba(40, 50, 70, 0.6)"


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image("logo.png", width=200)
        st.markdown('<div style="text-align: center; margin-bottom: 1rem;">', unsafe_allow_html=True)
        st.title("Каталог экзопланет")
        st.markdown("### Вход в систему")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")

        if st.form_submit_button("Войти"):
            if username and password:
                data = api_post("/api/login", {"username": username, "password": password})

                if data and data.get("success"):
                    st.session_state.update({
                        "logged_in": True,
                        "user_id": data["user_id"],
                        "username": data["username"],
                        "role": data["role"]
                    })
                    st.success("Успешный вход!")
                    st.rerun()
                else:
                    st.error("Неверное имя или пароль")
            else:
                st.warning("Заполните все поля")

    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("Регистрация", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()


def register_page():
    st.image("logo.png", width=100)

    st.markdown('<div style="text-align: center; margin-bottom: 2rem; margin-top: 4rem;">', unsafe_allow_html=True)
    st.title("Регистрация")
    st.markdown("### Создание учётной записи")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("register_form"):
        username = st.text_input("Имя пользователя", help="3-50 символов, только буквы, цифры и _")
        email = st.text_input("Email", help="example@domain.com")
        password = st.text_input("Пароль", type="password", help="Минимум 6 символов")
        confirm = st.text_input("Подтвердите пароль", type="password")

        if st.form_submit_button("Зарегистрироваться"):
            valid_user, msg_user = validate_username(username)
            if not valid_user:
                st.error(msg_user)
                return

            valid_email, msg_email = validate_email(email)
            if not valid_email:
                st.error(msg_email)
                return

            valid_pass, msg_pass = validate_password(password)
            if not valid_pass:
                st.error(msg_pass)
                return

            if password != confirm:
                st.error("Пароли не совпадают")
                return

            data = api_post("/api/register", {
                "username": username,
                "email": email,
                "password": password
            })

            if data and data.get("success"):
                login_data = api_post("/api/login", {"username": username, "password": password})

                if login_data and login_data.get("success"):
                    st.session_state.update({
                        "logged_in": True,
                        "user_id": login_data["user_id"],
                        "username": login_data["username"],
                        "role": login_data["role"],
                        "page": "catalog"
                    })
                    st.success("Регистрация успешна! Добро пожаловать!")
                    st.rerun()
                else:
                    st.session_state.page = "login"
                    st.rerun()
            else:
                st.error("Ошибка регистрации: возможно, пользователь уже существует")

    if st.button("Назад к входу"):
        st.session_state.page = "login"
        st.rerun()


def catalog_page():
    show_header()

    if st.session_state.role == "admin":
        if st.button("Добавить новую планету", type="primary", use_container_width=True):
            st.session_state.page = "add_planet"
            st.rerun()
        st.markdown("---")

    st.title("Каталог экзопланет")
    st.caption("Исследуйте далёкие миры и генерируйте их изображения")

    st.sidebar.header("Фильтры")
    search = st.sidebar.text_input("Поиск по названию")

    sort_options = {
        "По умолчанию": "completeness",
        "Масса": "mass",
        "Радиус": "radius",
        "Температура": "temp",
        "Расстояние": "distance"
    }
    sort_by_label = st.sidebar.selectbox("Сортировка по", list(sort_options.keys()))
    sort_by = sort_options[sort_by_label]

    if sort_by != "completeness":
        sort_order_label = st.sidebar.selectbox("Порядок", ["По возрастанию", "По убыванию"])
        if sort_order_label == "По возрастанию":
            sort_order = "asc"
        else:
            sort_order = "desc"
    else:
        sort_order = "desc"

    page = st.session_state.page_num
    data = api_get("/api/planets", {
        "page": page,
        "per_page": DEFAULT_PER_PAGE,
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    })

    if not data:
        st.error("Не удалось загрузить планеты. Проверьте API и БД.")
        return

    planets = data.get("planets", [])
    total_pages = data.get("total_pages", 1)

    if page > total_pages:
        st.session_state.page_num = 1
        page = 1

    if not planets:
        st.info("Планеты не найдены. Попробуйте изменить фильтры.")
        return

    cols = st.columns(3)
    for idx, p in enumerate(planets):
        with cols[idx % 3]:
            try:
                classification = PlanetClassifier.classify(p.get("pl_bmasse"), p.get("pl_rade"))
            except:
                classification = {"type_ru": "Неизвестный тип"}

            planet_type = classification.get("type_ru", "Неизвестный тип")
            planet_color = get_planet_color(planet_type)
            bg = get_card_bg_color(planet_type)

            star_color = PlanetClassifier.get_star_color(p.get("st_spectype"))
            star_color_dark = star_color + "88"

            card_html = f"""
                <div class="card" style="background: {bg}; border-color: {planet_color}40;">
                    <div style="display:flex;justify-content:center;align-items:center;gap:20px;margin-bottom:1.5rem;position:relative;">
                        <div class="planet-visual" style="background:radial-gradient(circle at 30% 30%,{planet_color},{planet_color}88);box-shadow:0 0 20px {planet_color}40;"></div>
                        <div class="star-visual star-small" style="--star-color:{star_color};--star-color-dark:{star_color_dark};" title="Звезда: {p.get('hostname', 'N/A')}"></div>
                    </div>
                    <div class="card-title">{p['pl_name']}</div>
                    <div class="card-type">{planet_type}</div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            if p.get('pl_bmasse'):
                mass_text = f"{p['pl_bmasse']:.2f} масс Земли"
            else:
                mass_text = "?"
            col1.metric("Масса", mass_text)

            if p.get('pl_rade'):
                radius_text = f"{p['pl_rade']:.2f} радиусов Земли"
            else:
                radius_text = "?"
            col2.metric("Радиус", radius_text)

            if p.get('sy_dist'):
                distance_text = f"{p['sy_dist']:.1f} парсек"
            else:
                distance_text = "?"
            col3.metric("Расстояние", distance_text)

            if st.button("Подробнее", key=f"btn_{p['id']}", use_container_width=True):
                st.session_state.selected_planet_id = p['id']
                st.session_state.page = "planet_detail"
                st.rerun()

    if total_pages > 1:
        st.markdown('<div style="margin-top:2rem;"></div>', unsafe_allow_html=True)
        col_left, col_center, col_right = st.columns([1, 2, 1])

        with col_left:
            if st.button("Назад", disabled=(page == 1)):
                st.session_state.page_num -= 1
                st.rerun()

        with col_center:
            page_html = f'<div style="text-align:center;padding:0.5rem;">Страница {page} из {total_pages}</div>'
            st.markdown(page_html, unsafe_allow_html=True)

        with col_right:
            if st.button("Вперёд", disabled=(page == total_pages)):
                st.session_state.page_num += 1
                st.rerun()


def planet_detail_page(planet_id):
    show_header()
    planet = api_get(f"/api/planets/{planet_id}")

    if not planet:
        st.error("Планета не найдена")
        return

    if st.button("Вернуться в каталог"):
        st.session_state.page = "catalog"
        st.rerun()
        return

    if st.session_state.get("edit_mode") and st.session_state.role == "admin":
        st.title(f"Редактирование: {planet['pl_name']}")

        with st.form("edit_planet_form"):
            col1, col2 = st.columns(2)

            with col1:
                nm = st.text_input("Название", value=planet.get("pl_name", ""))
                hs = st.text_input("Звезда", value=planet.get("hostname", ""))
                mb = st.number_input("Масса (M Земли)", min_value=0.0, step=0.01, value=float(planet.get("pl_bmasse") or 0))
                rd = st.number_input("Радиус (R Земли)", min_value=0.0, step=0.01, value=float(planet.get("pl_rade") or 0))
                tp = st.number_input("Температура (K)", min_value=0, step=1, value=int(planet.get("pl_eqt") or 0))
                ds = st.number_input("Расстояние (пк)", min_value=0.0, step=0.1, value=float(planet.get("sy_dist") or 0))
                op = st.number_input("Период обращения (дней)", min_value=0.0, step=0.01, value=float(planet.get("pl_orbper") or 0))
                sm = st.number_input("Большая полуось (а.е.)", min_value=0.0, step=0.001, value=float(planet.get("pl_orbsmax") or 0))
                ec = st.number_input("Эксцентриситет", min_value=0.0, max_value=1.0, step=0.01, value=float(planet.get("pl_orbeccen") or 0))
                inc = st.number_input("Наклонение орбиты (град)", min_value=0.0, max_value=180.0, step=0.1, value=float(planet.get("pl_orbincl") or 0))

            with col2:
                ms = st.number_input("Масса (точное значение)", min_value=0.0, step=0.01, value=float(planet.get("pl_masse") or 0))
                dn = st.number_input("Плотность (г/см³)", min_value=0.0, step=0.01, value=float(planet.get("pl_dens") or 0))
                ins = st.number_input("Инсоляция (относительно Земли)", min_value=0.0, step=0.01, value=float(planet.get("pl_insol") or 0))
                td = st.number_input("Глубина транзита", min_value=0.0, step=0.0001, value=float(planet.get("pl_trandep") or 0))
                dur = st.number_input("Длительность транзита (часы)", min_value=0.0, step=0.01, value=float(planet.get("pl_trandur") or 0))
                imp = st.number_input("Параметр удара", min_value=0.0, step=0.01, value=float(planet.get("pl_imppar") or 0))
                mt = st.text_input("Метод обнаружения", value=planet.get("discoverymethod", ""))
                yr = st.number_input("Год открытия", min_value=1900, max_value=2100, step=1, value=int(planet.get("disc_year") or 2000))
                cf = st.checkbox("Контроверсиальная", value=bool(planet.get("pl_controv_flag", False)))

            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if st.form_submit_button("Сохранить изменения", type="primary", use_container_width=True):
                    data = {
                        "pl_name": nm,
                        "hostname": hs,
                        "pl_bmasse": mb or None,
                        "pl_rade": rd or None,
                        "pl_eqt": tp or None,
                        "sy_dist": ds or None,
                        "pl_orbper": op or None,
                        "pl_orbsmax": sm or None,
                        "pl_orbeccen": ec or None,
                        "pl_orbincl": inc or None,
                        "pl_masse": ms or None,
                        "pl_dens": dn or None,
                        "pl_insol": ins or None,
                        "pl_trandep": td or None,
                        "pl_trandur": dur or None,
                        "pl_imppar": imp or None,
                        "discoverymethod": mt or None,
                        "disc_year": yr or None,
                        "pl_controv_flag": cf
                    }
                    res = api_post(
                        f"/api/admin/planets/{planet_id}",
                        data,
                        params={"user_id": st.session_state.user_id},
                        method="PUT"
                    )
                    if res and res.get("success"):
                        st.success("Изменения сохранены!")
                        st.session_state.edit_mode = False
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Ошибка сохранения")

            with btn_col2:
                if st.form_submit_button("Отмена", use_container_width=True):
                    st.session_state.edit_mode = False
                    st.rerun()
        return

    st.title(planet['pl_name'])
    classification = PlanetClassifier.classify(planet.get("pl_bmasse"), planet.get("pl_rade"))
    planet_type = classification.get("type_ru", "Неизвестный тип")
    planet_color = get_planet_color(planet_type)
    star_color = PlanetClassifier.get_star_color(planet.get("star_info", {}).get("st_spectype"))
    star_color_dark = star_color + "88"

    type_html = f'<span style="color:{planet_color};font-weight:600;">Тип: {planet_type}</span>'
    st.markdown(type_html, unsafe_allow_html=True)

    col_img, col_info = st.columns([1, 2])

    with col_img:
        st.markdown("#### Схематичная визуализация")

        visual_html = f"""
            <div style="display:flex;justify-content:center;align-items:center;gap:30px;margin:1rem 0;padding:2rem;background:rgba(15,23,42,0.5);border-radius:10px;border:1px solid rgba(148,163,184,0.15);position:relative;">
                <div class="planet-visual" style="width:180px;height:180px;background:radial-gradient(circle at 30% 30%,{planet_color},{planet_color}88);box-shadow:0 0 30px {planet_color}50;"></div>
                <div class="star-visual star-large" style="--star-color:{star_color};--star-color-dark:{star_color_dark};" title="Звезда: {planet.get('hostname', 'N/A')}"></div>
            </div>
        """
        st.markdown(visual_html, unsafe_allow_html=True)
        st.caption("Приблизительный вид на основе физических параметров")

        st.markdown("---")

        images_data = api_get(f"/api/planets/{planet_id}/images")

        if images_data:
            images = images_data.get("images", [])
        else:
            images = []

        real_images = [img for img in images if not img.get("is_illustrative")]
        has_generated_image = len(real_images) > 0

        if has_generated_image:
            latest_image = real_images[0]
            image_path = latest_image.get("file_path")

            if image_path and os.path.exists(image_path):
                st.markdown("#### Сгенерированное изображение")
                st.image(image_path, use_container_width=True)
                created_at = latest_image.get('created_at', '')[:19]
                st.caption(f"Сгенерировано: {created_at}")
            else:
                st.info("Файл изображения не найден на диске.")

            st.markdown("#### Управление изображением")
            regen_info_html = """
                <div style="text-align:center;color:#94a3b8;padding:0.8rem;margin-bottom:1rem;
                background:rgba(14,165,233,0.05);border-radius:8px;
                border:1px solid rgba(14,165,233,0.2);font-size:0.85rem;">
                Можно заменить текущее изображение на новое
                </div>
            """
            st.markdown(regen_info_html, unsafe_allow_html=True)

            regenerating_key = f"regenerating_{planet_id}"
            is_regenerating = st.session_state.get(regenerating_key, False)

            if st.button(
                "Сгенерировать заново",
                type="secondary",
                use_container_width=True,
                key=f"regen_img_{planet_id}",
                disabled=is_regenerating
            ):
                st.session_state[regenerating_key] = True

                with st.spinner("Генерация нового изображения..."):
                    response = api_post(
                        f"/api/planets/{planet_id}/regenerate-image",
                        {},
                        params={"user_id": st.session_state.user_id},
                        timeout=180
                    )

                    st.session_state[regenerating_key] = False

                    if response and response.get("success"):
                        st.cache_data.clear()
                        st.success("Изображение успешно обновлено!")
                        st.rerun()
                    else:
                        if response:
                            error_msg = response.get("detail", "Неизвестная ошибка")
                        else:
                            error_msg = "Ошибка соединения с API"
                        st.error(f"Ошибка перегенерации: {error_msg}")
        else:
            st.markdown("#### Генерация изображения")

            gen_info_html = """
                <div style="text-align:center;color:#94a3b8;padding:0.8rem;margin-bottom:1rem;
                background:rgba(14,165,233,0.05);border-radius:8px;
                border:1px solid rgba(14,165,233,0.2);font-size:0.85rem;">
                Создайте уникальное изображение планеты с помощью нейросети
                </div>
            """
            st.markdown(gen_info_html, unsafe_allow_html=True)

            generating_key = f"generating_{planet_id}"
            is_generating = st.session_state.get(generating_key, False)

            if st.button(
                "Сгенерировать изображение",
                type="primary",
                use_container_width=True,
                key=f"gen_img_{planet_id}",
                disabled=is_generating
            ):
                st.session_state[generating_key] = True

                with st.spinner("Генерация изображения..."):
                    response = api_post(
                        f"/api/planets/{planet_id}/generate-image",
                        {},
                        params={"user_id": st.session_state.user_id},
                        timeout=180
                    )

                    st.session_state[generating_key] = False

                    if response and response.get("success"):
                        st.cache_data.clear()
                        st.success("Изображение успешно сгенерировано!")
                        st.rerun()
                    else:
                        if response:
                            error_msg = response.get("detail", "Неизвестная ошибка")
                        else:
                            error_msg = "Ошибка соединения с API"
                        st.error(f"Ошибка генерации: {error_msg}")

    with col_info:
        st.subheader("Параметры планеты")

        with st.expander("Орбита", expanded=True):
            if planet.get('pl_orbper'):
                st.write(f"**Период обращения:** {planet.get('pl_orbper')} дней")
            else:
                st.write("**Период обращения:** —")

            if planet.get('pl_orbsmax'):
                st.write(f"**Большая полуось:** {planet.get('pl_orbsmax')} а.е.")
            else:
                st.write("**Большая полуось:** —")

            if planet.get('pl_orbeccen'):
                st.write(f"**Эксцентриситет:** {planet.get('pl_orbeccen')}")
            else:
                st.write("**Эксцентриситет:** —")

            if planet.get('pl_orbincl'):
                st.write(f"**Наклонение:** {planet.get('pl_orbincl')}°")
            else:
                st.write("**Наклонение:** —")

        with st.expander("Физические характеристики", expanded=True):
            if planet.get('pl_rade'):
                st.write(f"**Радиус:** {planet.get('pl_rade')} R⊕")
            else:
                st.write("**Радиус:** —")

            if planet.get('pl_bmasse'):
                st.write(f"**Масса (мин.):** {planet.get('pl_bmasse')} M⊕")
            else:
                st.write("**Масса (мин.):** —")

            if planet.get('pl_masse'):
                st.write(f"**Масса (точная):** {planet.get('pl_masse')} M⊕")
            else:
                st.write("**Масса (точная):** —")

            if planet.get('pl_dens'):
                st.write(f"**Плотность:** {planet.get('pl_dens')} г/см³")
            else:
                st.write("**Плотность:** —")

            if planet.get('pl_eqt'):
                st.write(f"**Температура:** {planet.get('pl_eqt')} K")
            else:
                st.write("**Температура:** —")

            if planet.get('pl_insol'):
                st.write(f"**Инсоляция:** {planet.get('pl_insol')}")
            else:
                st.write("**Инсоляция:** —")

        with st.expander("Транзитные данные"):
            if planet.get('pl_trandep'):
                st.write(f"**Глубина транзита:** {planet.get('pl_trandep')}")
            else:
                st.write("**Глубина транзита:** —")

            if planet.get('pl_trandur'):
                st.write(f"**Длительность транзита:** {planet.get('pl_trandur')} ч")
            else:
                st.write("**Длительность транзита:** —")

            if planet.get('pl_imppar'):
                st.write(f"**Параметр удара:** {planet.get('pl_imppar')}")
            else:
                st.write("**Параметр удара:** —")

        with st.expander("Открытие"):
            if planet.get('discoverymethod'):
                st.write(f"**Метод:** {planet.get('discoverymethod')}")
            else:
                st.write("**Метод:** —")

            if planet.get('disc_year'):
                st.write(f"**Год:** {planet.get('disc_year')}")
            else:
                st.write("**Год:** —")

            cf = planet.get('pl_controv_flag')
            if cf:
                st.write("**Контроверсиальная:** Да")
            else:
                st.write("**Контроверсиальная:** Нет")

            if planet.get('sy_dist'):
                st.write(f"**Расстояние:** {planet.get('sy_dist')} пк")
            else:
                st.write("**Расстояние:** —")

        star = planet.get("star_info", {})
        if star.get("st_spectype"):
            with st.expander("Параметры звезды", expanded=True):
                st.write(f"**Спектральный тип:** {star.get('st_spectype')}")

                if star.get('st_teff'):
                    st.write(f"**Температура:** {star.get('st_teff')} K")
                else:
                    st.write("**Температура:** —")

                if star.get('st_rad'):
                    st.write(f"**Радиус:** {star.get('st_rad')} R☉")
                else:
                    st.write("**Радиус:** —")

                if star.get('st_mass'):
                    st.write(f"**Масса:** {star.get('st_mass')} M☉")
                else:
                    st.write("**Масса:** —")

                if star.get('st_met'):
                    st.write(f"**Металличность:** {star.get('st_met')}")
                else:
                    st.write("**Металличность:** —")

                if star.get('st_logg'):
                    st.write(f"**log g:** {star.get('st_logg')}")
                else:
                    st.write("**log g:** —")

                if star.get('st_lum'):
                    st.write(f"**Светимость:** {star.get('st_lum')} L☉")
                else:
                    st.write("**Светимость:** —")

                if star.get('st_age'):
                    st.write(f"**Возраст:** {star.get('st_age')} млрд лет")
                else:
                    st.write("**Возраст:** —")

                if star.get('ra'):
                    st.write(f"**RA:** {star.get('ra')}°")
                else:
                    st.write("**RA:** —")

                if star.get('dec'):
                    st.write(f"**Dec:** {star.get('dec')}°")
                else:
                    st.write("**Dec:** —")

    st.markdown('<div style="margin-top:2rem;"></div>', unsafe_allow_html=True)
    st.subheader("Атмосфера и характеристики")

    star_info = planet.get("star_info", {})
    star_ru, _ = PlanetClassifier.get_star_influence(star_info.get("st_spectype"))
    atm = PlanetClassifier.get_atmosphere_by_temp(planet.get("pl_eqt"))

    if classification.get('description_ru'):
        st.write(f"Описание: {classification['description_ru']}")

    if atm:
        st.write(f"Атмосфера: {atm.get('components_ru')}")
        st.write(f"Цвет: {atm.get('color_hint_ru')}")

    st.write(f"Свет звезды: {star_ru}")

    with st.expander("Промпт для нейросети"):
        prompt = api_get(f"/api/planets/{planet_id}/generate-prompt")

        if prompt and prompt.get("success"):
            st.markdown("**Русский промпт:**")
            st.text_area(
                "ru_prompt",
                value=prompt.get("prompt_ru", ""),
                height=100,
                label_visibility="collapsed"
            )
            st.markdown("**English prompt (используется для генерации):**")
            st.text_area(
                "en_prompt",
                value=prompt.get("prompt_en", ""),
                height=100,
                label_visibility="collapsed"
            )
        else:
            st.info("Недостаточно данных для генерации промпта.")

    if st.session_state.role == "admin":
        st.markdown("---")
        st.subheader("Управление администратора")

        ac1, ac2 = st.columns(2)

        with ac1:
            if st.button("Редактировать параметры", type="primary", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

        with ac2:
            if st.button("Удалить планету", type="secondary", use_container_width=True):
                st.session_state.confirm_delete = True

        if st.session_state.get("confirm_delete"):
            st.warning("Вы уверены, что хотите удалить эту планету? Это действие помечает запись как удалённой.")

            del_c1, del_c2 = st.columns(2)

            with del_c1:
                if st.button("Да, удалить", type="primary"):
                    res = api_post(
                        f"/api/admin/planets/{planet_id}",
                        {},
                        params={"user_id": st.session_state.user_id},
                        method="DELETE"
                    )
                    if res and res.get("success"):
                        st.success("Планета удалена")
                        st.session_state.page = "catalog"
                        st.session_state.page_num = 1
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Ошибка удаления")

            with del_c2:
                if st.button("Отмена"):
                    st.session_state.confirm_delete = False
                    st.rerun()

        st.markdown("---")

    if st.button("Назад в каталог"):
        st.session_state.page = "catalog"
        st.session_state.page_num = 1
        st.rerun()


def add_planet_page():
    show_header()

    if st.session_state.role != "admin":
        st.error("Доступ запрещён")
        st.session_state.page = "catalog"
        st.rerun()

    st.title("Добавить новую планету")

    with st.form("add_planet_form"):
        col1, col2 = st.columns(2)

        with col1:
            nm = st.text_input("Название планеты")
            hs = st.text_input("Звезда (хостнейм)")
            mb = st.number_input("Масса (в массах Земли)", min_value=0.0, step=0.01)
            rd = st.number_input("Радиус (в радиусах Земли)", min_value=0.0, step=0.01)
            tp = st.number_input("Температура (K)", min_value=0, step=1)
            ds = st.number_input("Расстояние (парсек)", min_value=0.0, step=0.1)
            op = st.number_input("Период обращения (дней)", min_value=0.0, step=0.01)
            sm = st.number_input("Большая полуось (а.е.)", min_value=0.0, step=0.001)
            ec = st.number_input("Эксцентриситет", min_value=0.0, max_value=1.0, step=0.01)
            inc = st.number_input("Наклонение орбиты (град)", min_value=0.0, max_value=180.0, step=0.1)

        with col2:
            ms = st.number_input("Масса (точное значение)", min_value=0.0, step=0.01)
            dn = st.number_input("Плотность (г/см³)", min_value=0.0, step=0.01)
            ins = st.number_input("Инсоляция", min_value=0.0, step=0.01)
            td = st.number_input("Глубина транзита", min_value=0.0, step=0.0001)
            dur = st.number_input("Длительность транзита (часы)", min_value=0.0, step=0.01)
            imp = st.number_input("Параметр удара", min_value=0.0, step=0.01)
            mt = st.text_input("Метод обнаружения")
            yr = st.number_input("Год открытия", min_value=1900, max_value=2100, step=1)
            cf = st.checkbox("Контроверсиальная")

        if st.form_submit_button("Создать планету", type="primary", use_container_width=True):
            if nm and hs:
                data = {
                    "pl_name": nm,
                    "hostname": hs,
                    "pl_bmasse": mb or None,
                    "pl_rade": rd or None,
                    "pl_eqt": tp or None,
                    "sy_dist": ds or None,
                    "pl_orbper": op or None,
                    "pl_orbsmax": sm or None,
                    "pl_orbeccen": ec or None,
                    "pl_orbincl": inc or None,
                    "pl_masse": ms or None,
                    "pl_dens": dn or None,
                    "pl_insol": ins or None,
                    "pl_trandep": td or None,
                    "pl_trandur": dur or None,
                    "pl_imppar": imp or None,
                    "discoverymethod": mt or None,
                    "disc_year": yr or None,
                    "pl_controv_flag": cf
                }
                res = api_post(
                    "/api/admin/planets",
                    data,
                    params={"user_id": st.session_state.user_id}
                )
                if res and res.get("success"):
                    st.success(f"Планета '{nm}' успешно добавлена в каталог!")
                    st.session_state.page = "catalog"
                    st.cache_data.clear()
                    st.rerun()
                else:
                    if res and res.get("error"):
                        st.error(f"Ошибка создания планеты: {res.get('detail')}")
                    else:
                        st.error("Ошибка создания планеты")
            else:
                st.error("Заполните обязательные поля: Название и Звезда")

    if st.button("Отмена"):
        st.session_state.page = "catalog"
        st.rerun()


def main():
    if "page" not in st.session_state:
        if st.session_state.logged_in:
            st.session_state.page = "catalog"
        else:
            st.session_state.page = "login"

    if st.session_state.logged_in and st.session_state.page == "login":
        st.session_state.page = "catalog"

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
    elif st.session_state.page == "catalog":
        catalog_page()
    elif st.session_state.page == "planet_detail":
        if "selected_planet_id" in st.session_state:
            planet_detail_page(st.session_state.selected_planet_id)
        else:
            st.session_state.page = "catalog"
            st.rerun()
    elif st.session_state.page == "add_planet":
        if st.session_state.role == "admin":
            add_planet_page()
        else:
            st.session_state.page = "catalog"
            st.rerun()
    else:
        st.session_state.page = "login"
        st.rerun()


if __name__ == "__main__":
    main()