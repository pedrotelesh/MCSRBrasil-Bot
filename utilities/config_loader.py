import yaml
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("primp").setLevel(logging.WARNING)

try:
    with open('config.yml', 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    logging.error("Arquivo config.yml não encontrado.")
    config = {}
except yaml.YAMLError as e:
    logging.error(f"Erro ao carregar config.yml: {e}")
    config = {}

valid_language_codes = []
lang_directory = "lang"

current_language_code = config.get('LANGUAGE', 'pt-BR')

for filename in os.listdir(lang_directory):
    if filename.startswith("lang.") and filename.endswith(".json") and os.path.isfile(
            os.path.join(lang_directory, filename)):
        language_code = filename.split(".")[1]
        valid_language_codes.append(language_code)

def load_current_language():
    lang_file_path = os.path.join(
        lang_directory, f"lang.{current_language_code}.json")
    try:
        with open(lang_file_path, encoding="utf-8") as lang_file:
            current_language = json.load(lang_file)
        return current_language
    except FileNotFoundError:
        logging.error(f"Arquivo de linguagem {lang_file_path} não encontrado.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao carregar arquivo de linguagem {lang_file_path}: {e}")
        return {}