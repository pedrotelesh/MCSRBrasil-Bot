# 🇧🇷 MCSR Brasil Discord Bot

Um bot completo para a comunidade brasileira de Minecraft Speedrunning! Feito para facilitar divulgação, tutoriais, rankings, integração com APIs e administração de links de redes sociais.

![Minecraft Speedrun](https://img.shields.io/badge/Minecraft-Speedrun-green?style=flat-square)
![Discord](https://img.shields.io/badge/Discord-Bot-blueviolet?style=flat-square)

## ✨ Funcionalidades

- **Comandos de Ranking:**
  - `/top rsg`, `/top ssg`, `/top ranked` — Rankings brasileiros (speedrun.com e mcsrranked.com)
- **Divulgação de Redes Sociais:**
  - `/youtube`, `/twitch`, `/tiktok` — Embeds com links dinâmicos e botões
- **Tutoriais e Utilidades:**
  - `/mcsr` com subcomandos para mapas, estratégias, utilidades e links úteis
- **Administração Dinâmica:**
  - `/set` para editar links e informações de eventos (YouTube, Twitch, TikTok, BTRL)
- **Padronização Visual:**
  - Embeds modernas com footer automático e avatar do bot
- **Centralização de textos:**
  - Todas as descrições e textos em `lang/lang.pt-BR.json`

## 🚀 Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repo>
   cd teste
   ```
2. **Crie e configure o arquivo `.env`:**
   ```env
   DISCORD_TOKEN=seu_token_aqui
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure o arquivo `config.yml` e os arquivos de linguagem em `lang/` conforme necessário.**

5. **Inicie o bot:**
   ```bash
   python main.py
   ```

## 📋 Exemplo de Comandos

- `/top rsg` — Mostra o ranking brasileiro de Random Seed Glitchless
- `/mcsr mapas` — Links para mapas de prática
- `/set youtube <link>` — Atualiza o link do canal do YouTube

## 🛠️ Estrutura do Projeto

```
├── main.py
├── cogs/
│   ├── topruns.py
│   ├── twitch.py
│   ├── youtube.py
│   ├── tiktok.py
│   └── btrl.py
├── utilities/
│   ├── utility.py
│   ├── config_loader.py
│   └── embed_utils.py
├── lang/
│   └── lang.pt-BR.json
├── btrl.json
├── yt_tt_links.json
├── users.json
├── config.yml
└── requirements.txt
```

## 📦 Requisitos

- Python 3.9+
- discord.py >= 2.3.2
- python-dotenv
- aiohttp
- PyYAML
- ujson

## 🤝 Contribuição

Pull requests são bem-vindos! Sinta-se à vontade para abrir issues ou sugerir melhorias.

## 📝 Licença

Este projeto é open-source e está sob a licença MIT.

---

> Feito com ❤️ para a comunidade de Minecraft Speedrunning Brasil!
<BR>
> THE BEST.
