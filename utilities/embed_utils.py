from datetime import datetime
import os
import json

def apply_standard_footer(embed, bot_user=None):
    ano = datetime.now().year
    footer_text = f"© Copyright {ano} MCSR Brasil"
    if bot_user and getattr(getattr(bot_user, 'avatar', None), 'url', None):
        embed.set_footer(text=footer_text, icon_url=bot_user.avatar.url)
    else:
        embed.set_footer(text=footer_text)
    return embed

BTRL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'btrl.json')

def save_btrl(data):
    with open(BTRL_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_btrl():
    with open(BTRL_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
