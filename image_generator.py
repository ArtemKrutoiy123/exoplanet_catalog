import os
import requests
import random

GENERATED_DIR = "generated_images"
os.makedirs(GENERATED_DIR, exist_ok=True)


def generate_image(prompt, filename):
    print(f"Генерация изображения...")
    print(f"Промпт: {prompt}")
    
    seed = random.randint(0, 999999)
    
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
    params = {
        "width": 768,
        "height": 768,
        "seed": seed,
        "nologo": "true",
        "model": "flux",
        "enhance": "true"
    }
    
    response = requests.get(url, params=params, timeout=180)
    
    if response.status_code != 200:
        raise Exception(f"Ошибка API: статус {response.status_code}")
    
    filepath = os.path.join(GENERATED_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    print(f"Изображение сохранено: {filepath} (seed: {seed})")
    return filepath