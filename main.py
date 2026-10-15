from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import mysql.connector
from config import DB_CONFIG
import config
import database
from planet_classifier import PlanetClassifier
import datetime
import utils
import image_generator
import os

app = FastAPI(title="Exoplanet Catalog API")


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ImageCreateRequest(BaseModel):
    user_id: int
    description: str = ""


def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"DB connection error: {e}")
        return None


@app.post("/api/register")
def register(user: RegisterRequest):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (user.username, user.email))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем или email уже существует")
    
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role, status) VALUES (%s, %s, %s, 'user', 'active')",
        (user.username, user.email, user.password)
    )
    conn.commit()
    user_id = cursor.lastrowid
    
    cursor.close()
    conn.close()
    
    return {"success": True, "message": "Регистрация успешна", "user_id": user_id}


@app.post("/api/login")
def login(user: LoginRequest):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT id, username, role, status FROM users WHERE username = %s AND password_hash = %s",
        (user.username, user.password)
    )
    db_user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    
    if db_user['status'] != 'active':
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")
    
    return {
        "success": True,
        "user_id": db_user['id'],
        "username": db_user['username'],
        "role": db_user['role']
    }


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, username, email, role, status FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return user


@app.get("/api/planets")
def get_planets(
    page: int = Query(1, ge=1),
    per_page: int = Query(config.DEFAULT_PER_PAGE, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
):
    base_query = """
        SELECT 
            p.id, p.pl_name, p.hostname, p.pl_bmasse, p.pl_rade, 
            p.pl_eqt, p.sy_dist, p.discoverymethod, p.disc_year,
            p.created_at,
            p.pl_orbper, p.pl_orbsmax, p.pl_orbeccen, p.pl_orbincl,
            p.pl_masse, p.pl_dens, p.pl_insol,
            p.pl_trandep, p.pl_trandur, p.pl_imppar,
            s.st_spectype
        FROM planets p
        LEFT JOIN stars s ON p.hostname = s.hostname
        WHERE p.is_deleted = FALSE
    """
    
    count_query = "SELECT COUNT(*) as total FROM planets WHERE is_deleted = FALSE"
    params = []
    
    if search:
        base_query += " AND p.pl_name LIKE %s"
        count_query += " AND pl_name LIKE %s"
        params.append(f"%{search}%")
    
    if sort_by == "completeness":
        base_query += """
            ORDER BY (
                CASE WHEN p.pl_bmasse IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.pl_rade IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.pl_eqt IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.sy_dist IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.pl_orbper IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.pl_orbsmax IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.discoverymethod IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.disc_year IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.pl_masse IS NOT NULL THEN 1 ELSE 0 END +
                CASE WHEN p.pl_dens IS NOT NULL THEN 1 ELSE 0 END
            ) DESC, p.pl_name ASC
        """
    else:
        order_column = None
        if sort_by == "mass":
            order_column = "p.pl_bmasse"
        elif sort_by == "radius":
            order_column = "p.pl_rade"
        elif sort_by == "temp":
            order_column = "p.pl_eqt"
        elif sort_by == "distance":
            order_column = "p.sy_dist"
        
        if order_column:
            if sort_order == "desc":
                base_query += f" ORDER BY {order_column} DESC, p.pl_name ASC"
            else:
                base_query += f" ORDER BY {order_column} ASC, p.pl_name ASC"
        else:
            base_query += " ORDER BY p.pl_name ASC"
    
    offset = (page - 1) * per_page
    base_query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    count_result = database.fetch_one(count_query, params[:-2] if search else [])
    total = count_result['total'] if count_result else 0
    
    planets = database.fetch_all(base_query, params)
    
    for planet in planets:
        image_count = database.fetch_one(
            "SELECT COUNT(*) as cnt FROM images WHERE planet_id = %s",
            (planet['id'],)
        )
        planet['has_image'] = image_count['cnt'] > 0 if image_count else False
        
        planet['pl_bmasse'] = utils.round_value(planet['pl_bmasse'])
        planet['pl_rade'] = utils.round_value(planet['pl_rade'])
        planet['pl_eqt'] = utils.round_value(planet['pl_eqt'])
        planet['sy_dist'] = utils.round_value(planet['sy_dist'])
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "planets": planets,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


@app.get("/api/planets/{planet_id}")
def get_planet_detail(planet_id: int):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            p.id, p.pl_name, p.hostname,
            p.pl_orbper, p.pl_orbsmax, p.pl_orbeccen, p.pl_orbincl,
            p.pl_rade, p.pl_bmasse, p.pl_masse, p.pl_dens, p.pl_eqt, p.pl_insol,
            p.pl_trandep, p.pl_trandur, p.pl_imppar,
            p.discoverymethod, p.disc_year, p.pl_controv_flag, p.sy_dist,
            p.is_deleted, p.created_at, p.updated_at,
            s.st_spectype, s.st_teff, s.st_rad, s.st_mass,
            s.st_met, s.st_logg, s.st_lum, s.st_age,
            s.ra, s.dec, s.st_dens, s.st_vsin, s.st_rotp, s.st_radv
        FROM planets p
        LEFT JOIN stars s ON p.hostname = s.hostname
        WHERE p.id = %s AND p.is_deleted = 0
    """, (planet_id,))
    planet = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not planet:
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    star_info = {}
    star_fields = ["st_spectype", "st_teff", "st_rad", "st_mass", 
                  "st_met", "st_logg", "st_lum", "st_age",
                  "ra", "dec", "st_dens", "st_vsin", "st_rotp", "st_radv"]
    for field in star_fields:
        star_info[field] = planet.pop(field, None)
    
    return {**planet, "star_info": star_info}


@app.get("/api/planets/{planet_id}/generate-prompt")
def generate_prompt(planet_id: int):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, s.st_spectype, s.st_teff, s.st_rad, s.st_mass, s.st_met, s.st_logg
        FROM planets p
        LEFT JOIN stars s ON p.hostname = s.hostname
        WHERE p.id = %s AND p.is_deleted = 0
    """, (planet_id,))
    row = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    planet_row = {k: row[k] for k in row if not k.startswith("st_")}
    star_row = {k: row[k] for k in row if k.startswith("st_")}
    
    prompts = PlanetClassifier.generate_prompts(planet_row, star_row)
    
    return {
        "success": True,
        "prompt_ru": prompts["ru"],
        "prompt_en": prompts["en"],
        "planet_type": PlanetClassifier.classify(planet_row.get("pl_bmasse"), planet_row.get("pl_rade"))["type_ru"],
        "message": "Промпт сгенерирован"
    }


@app.post("/api/planets/{planet_id}/generate-image")
def generate_image(planet_id: int, user_id: int = Query(...)):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, s.st_spectype, s.st_teff, s.st_rad, s.st_mass, s.st_met, s.st_logg
        FROM planets p
        LEFT JOIN stars s ON p.hostname = s.hostname
        WHERE p.id = %s AND p.is_deleted = 0
    """, (planet_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    planet_row = {k: row[k] for k in row if not k.startswith("st_")}
    star_row = {k: row[k] for k in row if k.startswith("st_")}
    
    prompts = PlanetClassifier.generate_prompts(planet_row, star_row)
    prompt_en = prompts["en"]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"planet_{planet_id}_{timestamp}.png"
    
    try:
        filepath = image_generator.generate_image(prompt_en, filename)
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"Ошибка генерации: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации изображения: {str(e)}")
    
    cursor.execute(
        "INSERT INTO images (planet_id, user_id, file_path, is_illustrative) VALUES (%s, %s, %s, %s)",
        (planet_id, user_id, filepath, False)
    )
    conn.commit()
    image_id = cursor.lastrowid
    
    cursor.close()
    conn.close()
    
    return {
        "success": True,
        "message": "Изображение успешно сгенерировано",
        "image_id": image_id,
        "image_path": filepath,
        "prompt_used": prompt_en
    }


@app.post("/api/planets/{planet_id}/regenerate-image")
def regenerate_image(planet_id: int, user_id: int = Query(...)):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM planets WHERE id = %s AND is_deleted = 0", (planet_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    cursor.execute("SELECT id, file_path FROM images WHERE planet_id = %s AND is_illustrative = 0", (planet_id,))
    old_image = cursor.fetchone()
    
    if old_image:
        old_path = old_image.get("file_path")
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
                print(f"Удалён старый файл: {old_path}")
            except Exception as e:
                print(f"Не удалось удалить старый файл: {e}")
        
        cursor.execute("DELETE FROM images WHERE id = %s", (old_image["id"],))
        print(f"Удалена запись изображения id={old_image['id']}")
    
    cursor.execute("""
        SELECT p.*, s.st_spectype, s.st_teff, s.st_rad, s.st_mass, s.st_met, s.st_logg
        FROM planets p
        LEFT JOIN stars s ON p.hostname = s.hostname
        WHERE p.id = %s AND p.is_deleted = 0
    """, (planet_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    planet_row = {k: row[k] for k in row if not k.startswith("st_")}
    star_row = {k: row[k] for k in row if k.startswith("st_")}
    
    prompts = PlanetClassifier.generate_prompts(planet_row, star_row)
    prompt_en = prompts["en"]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"planet_{planet_id}_{timestamp}.png"
    
    try:
        filepath = image_generator.generate_image(prompt_en, filename)
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"Ошибка генерации: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации изображения: {str(e)}")
    
    cursor.execute(
        "INSERT INTO images (planet_id, user_id, file_path, is_illustrative) VALUES (%s, %s, %s, %s)",
        (planet_id, user_id, filepath, False)
    )
    conn.commit()
    image_id = cursor.lastrowid
    
    cursor.close()
    conn.close()
    
    return {
        "success": True,
        "message": "Изображение перегенерировано",
        "image_id": image_id,
        "image_path": filepath,
        "prompt_used": prompt_en
    }


@app.get("/api/planets/{planet_id}/images")
def get_planet_images(planet_id: int):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT i.id, i.file_path, i.created_at, i.is_illustrative, u.username
        FROM images i
        JOIN users u ON i.user_id = u.id
        WHERE i.planet_id = %s
        ORDER BY i.created_at DESC
    """, (planet_id,))
    images = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for img in images:
        if img['created_at']:
            img['created_at'] = img['created_at'].isoformat()
    
    return {"images": images}


@app.post("/api/planets/{planet_id}/images")
def create_image(planet_id: int, req: ImageCreateRequest):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM planets WHERE id = %s AND is_deleted = 0", (planet_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    cursor.execute("SELECT id FROM users WHERE id = %s AND status = 'active'", (req.user_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь не активен")
    
    file_path = f"generated/planet_{planet_id}_user_{req.user_id}_{datetime.datetime.now().timestamp()}.png"
    
    cursor.execute(
        "INSERT INTO images (planet_id, user_id, file_path, is_illustrative) VALUES (%s, %s, %s, %s)",
        (planet_id, req.user_id, file_path, True)
    )
    conn.commit()
    image_id = cursor.lastrowid
    
    cursor.close()
    conn.close()
    
    return {"success": True, "message": "Изображение создано (заглушка)", "image_id": image_id}


def check_admin(user_id: int):
    conn = get_db()
    if not conn:
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT role FROM users WHERE id = %s AND status = 'active'", (user_id,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user and user['role'] == 'admin':
        return True
    return False


class PlanetCreateRequest(BaseModel):
    pl_name: str
    hostname: str
    pl_orbper: Optional[float] = None
    pl_orbsmax: Optional[float] = None
    pl_orbeccen: Optional[float] = None
    pl_orbincl: Optional[float] = None
    pl_rade: Optional[float] = None
    pl_bmasse: Optional[float] = None
    pl_masse: Optional[float] = None
    pl_dens: Optional[float] = None
    pl_eqt: Optional[float] = None
    pl_insol: Optional[float] = None
    pl_trandep: Optional[float] = None
    pl_trandur: Optional[float] = None
    pl_imppar: Optional[float] = None
    discoverymethod: Optional[str] = None
    disc_year: Optional[int] = None
    sy_dist: Optional[float] = None
    pl_controv_flag: Optional[bool] = None


class StarCreateRequest(BaseModel):
    hostname: str
    st_spectype: Optional[str] = None
    st_teff: Optional[float] = None
    st_rad: Optional[float] = None
    st_mass: Optional[float] = None
    st_met: Optional[float] = None
    st_logg: Optional[float] = None
    ra: Optional[float] = None
    dec: Optional[float] = None
    sy_dist: Optional[float] = None


@app.post("/api/admin/planets")
def admin_create_planet(request: PlanetCreateRequest, user_id: int = Query(...)):
    if not check_admin(user_id):
        raise HTTPException(status_code=403, detail="Только для администраторов")
    
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id FROM planets WHERE pl_name = %s", (request.pl_name,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Планета с таким названием уже существует")
    
    cursor.execute("SELECT hostname FROM stars WHERE hostname = %s", (request.hostname,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO stars (hostname) VALUES (%s)", (request.hostname,))
    
    cursor.execute("""
        INSERT INTO planets (
            pl_name, hostname, pl_orbper, pl_orbsmax, pl_orbeccen, pl_orbincl,
            pl_rade, pl_bmasse, pl_masse, pl_dens, pl_eqt, pl_insol,
            pl_trandep, pl_trandur, pl_imppar, discoverymethod, disc_year,
            sy_dist, pl_controv_flag
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        request.pl_name, request.hostname,
        request.pl_orbper, request.pl_orbsmax, request.pl_orbeccen, request.pl_orbincl,
        request.pl_rade, request.pl_bmasse, request.pl_masse, request.pl_dens,
        request.pl_eqt, request.pl_insol,
        request.pl_trandep, request.pl_trandur, request.pl_imppar,
        request.discoverymethod, request.disc_year,
        request.sy_dist, request.pl_controv_flag
    ))
    
    conn.commit()
    planet_id = cursor.lastrowid
    
    cursor.close()
    conn.close()
    
    return {"success": True, "message": "Планета создана", "planet_id": planet_id}


@app.put("/api/admin/planets/{planet_id}")
def admin_update_planet(planet_id: int, request: PlanetCreateRequest, user_id: int = Query(...)):
    if not check_admin(user_id):
        raise HTTPException(status_code=403, detail="Только для администраторов")
    
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM planets WHERE id = %s", (planet_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    cursor.execute("""
        UPDATE planets SET
            pl_name = %s, hostname = %s, pl_orbper = %s, pl_orbsmax = %s,
            pl_orbeccen = %s, pl_orbincl = %s, pl_rade = %s, pl_bmasse = %s,
            pl_masse = %s, pl_dens = %s, pl_eqt = %s, pl_insol = %s,
            pl_trandep = %s, pl_trandur = %s, pl_imppar = %s,
            discoverymethod = %s, disc_year = %s, sy_dist = %s,
            pl_controv_flag = %s, updated_at = NOW()
        WHERE id = %s
    """, (
        request.pl_name, request.hostname,
        request.pl_orbper, request.pl_orbsmax, request.pl_orbeccen, request.pl_orbincl,
        request.pl_rade, request.pl_bmasse, request.pl_masse, request.pl_dens,
        request.pl_eqt, request.pl_insol,
        request.pl_trandep, request.pl_trandur, request.pl_imppar,
        request.discoverymethod, request.disc_year,
        request.sy_dist, request.pl_controv_flag,
        planet_id
    ))
    
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return {"success": True, "message": "Планета обновлена"}


@app.delete("/api/admin/planets/{planet_id}")
def admin_delete_planet(planet_id: int, user_id: int = Query(...)):
    if not check_admin(user_id):
        raise HTTPException(status_code=403, detail="Только для администраторов")
    
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM planets WHERE id = %s", (planet_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Планета не найдена")
    
    cursor.execute("UPDATE planets SET is_deleted = TRUE, updated_at = NOW() WHERE id = %s", (planet_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return {"success": True, "message": "Планета удалена"}


@app.get("/api/admin/planets")
def admin_get_all_planets(
    user_id: int = Query(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
):
    if not check_admin(user_id):
        raise HTTPException(status_code=403, detail="Только для администраторов")
    
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Ошибка БД")
    
    cursor = conn.cursor(dictionary=True)
    
    base_query = """
        SELECT id, pl_name, hostname, pl_bmasse, pl_rade, 
               pl_eqt, sy_dist, discoverymethod, disc_year, is_deleted, created_at
        FROM planets
    """
    count_query = "SELECT COUNT(*) as total FROM planets"
    params = []
    
    order_map = {
        "date": "created_at",
        "name": "pl_name",
        "mass": "pl_bmasse",
        "radius": "pl_rade",
        "temp": "pl_eqt",
        "distance": "sy_dist"
    }
    order_column = order_map.get(sort_by, "created_at")
    
    if sort_order == "asc":
        order_dir = "ASC"
    else:
        order_dir = "DESC"
    
    base_query += f" ORDER BY {order_column} {order_dir}"
    
    offset = (page - 1) * per_page
    base_query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    cursor.execute(count_query)
    total = cursor.fetchone()['total']
    
    cursor.execute(base_query, params)
    planets = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for p in planets:
        p['pl_bmasse'] = utils.round_value(p['pl_bmasse'])
        p['pl_rade'] = utils.round_value(p['pl_rade'])
        p['pl_eqt'] = utils.round_value(p['pl_eqt'])
        p['sy_dist'] = utils.round_value(p['sy_dist'])
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "planets": planets,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)