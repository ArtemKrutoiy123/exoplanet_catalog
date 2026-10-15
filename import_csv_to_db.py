import pandas as pd
import mysql.connector
from config import DB_CONFIG


def import_csv_to_db(csv_file_path):
    if not os.path.exists(csv_file_path):
        print(f"Файл {csv_file_path} не найден")
        return

    try:
        df = pd.read_csv(csv_file_path, low_memory=False)
        print(f"Файл {csv_file_path} загружен, исходное число строк: {len(df)}")
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")
        return

    if 'pl_name' in df.columns:
        df['_non_null_count'] = df.notna().sum(axis=1)
        df_sorted = df.sort_values('_non_null_count', ascending=False)
        df_unique = df_sorted.drop_duplicates(subset=['pl_name'], keep='first')
        df = df_unique.drop(columns=['_non_null_count'])
        print(f"После удаления дубликатов планет осталось строк: {len(df)}")
    else:
        print("Колонка 'pl_name' не найдена, пропускаем дедупликацию")

    star_columns = [
        'hostname', 'st_spectype', 'st_teff', 'st_rad', 'st_mass',
        'st_met', 'st_logg', 'ra', 'dec', 'sy_dist'
    ]

    planet_columns = [
        'pl_name', 'hostname', 'pl_orbper', 'pl_orbsmax', 'pl_orbeccen',
        'pl_orbincl', 'pl_rade', 'pl_bmasse', 'pl_masse', 'pl_dens',
        'pl_eqt', 'pl_insol', 'pl_trandep', 'pl_trandur', 'pl_imppar',
        'discoverymethod', 'disc_year'
    ]

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    star_insert_query = """
        INSERT IGNORE INTO stars (hostname, st_spectype, st_teff, st_rad, st_mass,
                                  st_met, st_logg, ra, `dec`, sy_dist)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    star_count = 0
    for _, row in df.iterrows():
        values = []
        for col in star_columns:
            if col in df.columns and pd.notna(row[col]):
                values.append(row[col])
            else:
                values.append(None)

        if values[0] is None:
            continue

        try:
            cursor.execute(star_insert_query, values)
            star_count += cursor.rowcount
        except Exception as e:
            print(f"Ошибка вставки звезды {values[0]}: {e}")

    conn.commit()
    print(f"Вставлено (или уже существовало) звёзд: {star_count}")

    planet_insert_query = """
        INSERT IGNORE INTO planets (pl_name, hostname, pl_orbper, pl_orbsmax, pl_orbeccen,
                                    pl_orbincl, pl_rade, pl_bmasse, pl_masse, pl_dens,
                                    pl_eqt, pl_insol, pl_trandep, pl_trandur, pl_imppar,
                                    discoverymethod, disc_year, sy_dist)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    planet_count = 0
    for _, row in df.iterrows():
        values = []
        for col in planet_columns:
            if col in df.columns and pd.notna(row[col]):
                values.append(row[col])
            else:
                values.append(None)

        if 'sy_dist' in df.columns and pd.notna(row['sy_dist']):
            values.append(row['sy_dist'])
        else:
            values.append(None)

        if values[0] is None or values[1] is None:
            continue

        cursor.execute("SELECT 1 FROM stars WHERE hostname = %s", (values[1],))
        if not cursor.fetchone():
            continue

        try:
            cursor.execute(planet_insert_query, values)
            planet_count += cursor.rowcount
        except Exception as e:
            if "Duplicate entry" not in str(e):
                print(f"Ошибка вставки планеты {values[0]}: {e}")

    conn.commit()
    print(f"Вставлено (уникальных) планет: {planet_count}")

    cursor.close()
    conn.close()
    print("Импорт завершён.")


if __name__ == "__main__":
    import os
    import_csv_to_db("PS_2026.04.27_21.50.44.csv")