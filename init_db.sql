CREATE DATABASE IF NOT EXISTS exoplanet_catalog
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE exoplanet_catalog;

CREATE TABLE IF NOT EXISTS stars (
    hostname VARCHAR(100) PRIMARY KEY, -- Имя звезды (уникальный идентификатор)
    st_spectype VARCHAR(50), -- Спектральный тип
    st_teff DOUBLE, -- Эффективная температура звезды [K]
    st_rad DOUBLE, -- Радиус звезды [солнечных радиусов]
    st_mass DOUBLE, -- Масса звезды [солнечных масс]
    st_met DOUBLE, -- Металличность звезды
    st_logg DOUBLE, -- Поверхностная гравитация звезды [log10(см/с²)]
    st_lum DOUBLE, -- Светимость звезды [log(солнечных)]
    st_age DOUBLE, -- Возраст звезды [млрд лет]
    ra DOUBLE, -- Прямое восхождение [градусы]
    `dec` DOUBLE, -- Склонение [градусы]
    sy_dist DOUBLE, -- Расстояние до системы [пк]
    st_dens DOUBLE, -- Плотность звезды [г/см³]
    st_vsin DOUBLE, -- Скорость вращения звезды [км/с]
    st_rotp DOUBLE, -- Период вращения звезды [дни]
    st_radv DOUBLE, -- Системная радиальная скорость [км/с]
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Уникальный идентификатор пользователя
    username VARCHAR(50) NOT NULL UNIQUE, -- Имя пользователя
    email VARCHAR(100) NOT NULL UNIQUE, -- Email пользователя
    password_hash VARCHAR(255) NOT NULL, -- пароль пользователя (не хэш)
    role ENUM('user','admin') NOT NULL DEFAULT 'user', -- Роль пользователя (user или admin)
    status ENUM('active','blocked') NOT NULL DEFAULT 'active', -- Статус аккаунта (active или blocked)
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS planets (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Уникальный идентификатор планеты
    pl_name VARCHAR(100) NOT NULL UNIQUE, -- Название планеты
    hostname VARCHAR(100) NOT NULL, -- Имя звезды-хозяина (ссылка на stars.hostname)
    pl_orbper DOUBLE, -- Орбитальный период [дни]
    pl_orbsmax DOUBLE, -- Большая полуось орбиты [а.е.]
    pl_orbeccen DOUBLE, -- Эксцентриситет орбиты
    pl_orbincl DOUBLE, -- Наклонение орбиты [градусы]
    pl_rade DOUBLE, -- Радиус планеты [радиусов Земли]
    pl_bmasse DOUBLE, -- Масса планеты или масса*sin(i) [масс Земли]
    pl_masse DOUBLE, -- Масса планеты [масс Земли]
    pl_dens DOUBLE, -- Плотность планеты [г/см³]
    pl_eqt DOUBLE, -- Равновесная температура [K]
    pl_insol DOUBLE, -- Поток излучения [относительно земного]
    pl_trandep DOUBLE, -- Глубина транзита [%]
    pl_trandur DOUBLE, -- Длительность транзита [часы]
    pl_imppar DOUBLE, -- То в какой части планета прошла по звезде
    discoverymethod VARCHAR(100), -- Метод обнаружения
    disc_year INT, -- Год открытия
    pl_controv_flag BOOLEAN DEFAULT FALSE, -- Флаг спорности данных
    sy_dist DOUBLE, -- Расстояние до системы [пк]
    is_deleted BOOLEAN DEFAULT FALSE, -- Флаг мягкого удаления (is_deleted)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hostname) REFERENCES stars(hostname) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    planet_id INT NOT NULL,
    user_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    is_illustrative BOOLEAN DEFAULT TRUE, -- Флаг: схематичное или реальное изображение
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (planet_id) REFERENCES planets(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

INSERT INTO users (username, email, password_hash, role, status)
VALUES ('admin', 'admin@example.com', 'admin', 'admin', 'active')
ON DUPLICATE KEY UPDATE username=username;