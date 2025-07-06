import os
from datetime import datetime
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import logging

from utilities.utility import *
from utilities import config_loader as config
from utilities.embed_utils import apply_standard_footer, save_btrl, load_btrl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("primp").setLevel(logging.WARNING)
logging.getLogger("discord").setLevel(logging.WARNING)

load_dotenv()
intents = discord.Intents.all()
bot = commands.AutoShardedBot(command_prefix="/", intents=intents)
bot.start_time = datetime.now()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logger.error("DISCORD_TOKEN não encontrado no arquivo .env")
    exit(1)

presences = config.config["PRESENCES"]
language = config.load_current_language()

sync_done = False

@bot.event
async def setup_hook():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            extension = f'cogs.{filename[:-3]}'
            if extension not in bot.extensions:
                try:
                    await bot.load_extension(extension)
                    logger.info(f'Cog carregado: {extension}')
                except commands.ExtensionAlreadyLoaded:
                    continue
                except Exception as e:
                    logger.error(f'Erro ao carregar cog: {extension} - {e}')

@bot.event
async def on_ready():
    global sync_done
    if not sync_done:
        try:
            await bot.tree.sync()
            logger.info("Comandos sincronizados com sucesso.")
        except Exception as e:
            logger.warning(f"Falha ao sincronizar comandos: {e}")
        sync_done = True
    logger.info(f"Estou rodando em {language['language_name']}!")
    client_id = bot.user.id
    scopes = "bot+applications.commands"
    # Permissões: Send Messages, Embed Links, Read Message History, Use External Emojis, Attach Files, Add Reactions, View Channels
    permissions = 274878221440  # 0x4000000000 | 0x40000 | 0x800 | 0x400 | 0x2000 | 0x40 | 0x40000000 | 0x100000000000
    invite_link = f"https://discord.com/oauth2/authorize?client_id={client_id}&scope={scopes}&permissions={permissions}"
    logger.info(f"{bot.user} conectou ao Discord com {bot.shard_count} shards!\nLink de convite: {invite_link}")

@commands.guild_only()
@bot.hybrid_group()
async def top(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Comando inválido. Use /top ssg, /top rsg ou /top ranked.")

@top.command(name="rsg", description=language["comandos"]["top"]["rsg"])
async def top_rsg_command(ctx):
    try:
        await ctx.defer()
        results = await get_top_runs(tipo=config.config['RSG_1_16'])
        view = TopPaginationView(ctx, results, 'rsg')
        embed = view.get_embed()
        view.message = await ctx.send(embed=embed, view=view)
    except Exception as e:
        await ctx.send(f"Oops, não consegui encontrar os tops. {e}", ephemeral=True)

@top.command(name="ssg", description=language["comandos"]["top"]["ssg"])
async def top_ssg_command(ctx):
    try:
        await ctx.defer()
        results = await get_top_runs(tipo=config.config['SSG_1_16'])
        view = TopPaginationView(ctx, results, 'ssg')
        embed = view.get_embed()
        view.message = await ctx.send(embed=embed, view=view)
    except Exception as e:
        await ctx.send(f"Oops, não consegui encontrar os tops. {e}", ephemeral=True)

@top.command(name="ranked", description="Ranking brasileiro do MCSR Ranked")
async def top_ranked_command(ctx):
    try:
        await ctx.defer()
        url = config.config["RANKED"]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        users = data.get("data", {}).get("users", [])
        results = []
        for user in users:
            results.append({
                "nickname": user.get("nickname", "?"),
                "elo": user.get("eloRate", "?"),
                "rank": user.get("eloRank", "?"),
            })
        view = TopPaginationView(ctx, results, 'ranked')
        embed = view.get_embed()
        view.message = await ctx.send(embed=embed, view=view)
    except Exception as e:
        await ctx.send("Oops, não consegui encontrar o ranking ranked.", ephemeral=True)

@commands.guild_only()
@bot.hybrid_group(name="mcsr", description=language["comandos"]["mcsr"]["group"])
async def mcsr(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Comando inválido.")

@mcsr.command(name="config", description=language["comandos"]["mcsr"]["config"])
async def mcsr_config(ctx):
    embed = discord.Embed(title="Configuração Minecraft Speedrun", color=0x009739)
    embed.add_field(name="🇺🇸 Tutorial de configuração Geral:", value="Guia completo para configurar o Minecraft para speedrun.", inline=False)
    embed.add_field(name="🇺🇸 Tutorial de Configuração do Boat Eye", value="Aprenda a configurar o Boat Eye.", inline=False)
    embed.add_field(name="📁 ModCheck", value="Aplicativo para baixar mods permitidos.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Minecraft Speedrun Setup Guide 2025", emoji="🇺🇸", url="https://youtu.be/OEpZlv6cQsI?si=nE1dmyH1xn8fn0bo"))
    view.add_item(discord.ui.Button(label="Boat eye setup", emoji="🇺🇸", url="https://youtu.be/HcrrfsHrR_c?si=w3NluoWv-N1BCuZs"))
    view.add_item(discord.ui.Button(label="ModCheck", emoji="📁", url="https://github.com/tildejustin/modcheck/releases"))

    await ctx.send(embed=embed, view=view)

@mcsr.command(name="mapas", description=language["comandos"]["mcsr"]["mapas"])
async def mcsr_mapas(ctx):
    embed = discord.Embed(title="Mapas de Prática - Minecraft Speedrun", color=0x009739)
    embed.add_field(name="📁 Mapa de prática Geral (Baixe o .zip!)", value="Mapa completo para treinar várias situações do speedrun.", inline=False)
    embed.add_field(name="📁 Mapa de prática de Zero Cycle (Baixe o .zip!)", value="Mapa focado em treinar o Zero Cycle.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="MCSR PRACTICE MAP", emoji="📁", url="https://github.com/Dibedy/The-MCSR-Practice-Map/releases/tag/1.0.1"))
    view.add_item(discord.ui.Button(label="Zero Practice Map", emoji="📁", url="https://github.com/Mescht/Zero-Practice/releases/tag/v1.2.1"))

    await ctx.send(embed=embed, view=view)

@mcsr.command(name="overworld", description=language["comandos"]["mcsr"]["overworld"])
async def mcsr_overworld(ctx):
    embed = discord.Embed(title="Tutoriais Overworld - Minecraft Speedrun", color=0x009739)
    embed.add_field(name="🇧🇷 Como achar Tesouros sem o mapa! (e outras coisas)", value="Dicas para encontrar tesouros e outras estratégias.", inline=False)
    embed.add_field(name="🇺🇸 Tutorial de Mapless, achar tesouro sem ter o mapa", value="Tutorial em inglês sobre mapless.", inline=False)
    embed.add_field(name="🇺🇸 Tutorial de como fazer um monte de Portal", value="Guia para portais rápidos.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="PieChart explicado", emoji="🇧🇷", url="https://www.youtube.com/watch?v=CoVfWydyIYI"))
    view.add_item(discord.ui.Button(label="How to do Mapless", emoji="🇺🇸", url="https://youtu.be/KTjhUmvFeuA?si=Nce724JX3Axk6WCh"))
    view.add_item(discord.ui.Button(label="Portal Guide", emoji="🇺🇸", url="https://www.youtube.com/watch?v=WEfSS2JTR80"))

    await ctx.send(embed=embed, view=view)

@mcsr.command(name="bastions", description=language["comandos"]["mcsr"]["bastions"])
async def mcsr_bastions(ctx):
    embed = discord.Embed(title="Tutoriais Bastions - Minecraft Speedrun", color=0x009739)
    embed.add_field(name="🇺🇸 Playlist de Tutoriais de Bastion da MCSR Wiki", value="Vídeos para aprender todas as rotas e técnicas de Bastion.", inline=False)
    embed.add_field(name="🇺🇸 Playlist de Tutoriais de Bastion da MCSR Ranked", value="Tutoriais focados em Bastion para Ranked.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Bastion Playlist (Wiki)", emoji="🇺🇸", url="https://youtube.com/playlist?list=PL09eJKh_g69hcU7_y2uz3wB-jju4_4MdQ&si=9JhvjRWiBHAGxJb2"))
    view.add_item(discord.ui.Button(label="Bastion Playlist (Ranked)", emoji="🇺🇸", url="https://www.youtube.com/watch?v=OxZkC67rops&list=PLKMhRbg_I18-1gMJC1oXKF8loH2AC7mRI&index=4"))

    await ctx.send(embed=embed, view=view)

@mcsr.command(name="fortalezas", description=language["comandos"]["mcsr"]["fortalezas"])
async def mcsr_fortalezas(ctx):
    embed = discord.Embed(title="Tutoriais Fortalezas - Minecraft Speedrun", color=0x009739)
    embed.add_field(name="🇺🇸 Tutorial de como achar e jogar Fortalezas", value="Guia completo para encontrar e lidar com fortalezas.", inline=False)
    embed.add_field(name="🇺🇸 Mini Tutorial geral sobre Fortalezas", value="Dicas rápidas sobre fortalezas.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="How to Speedrun Fortress", emoji="🇺🇸", url="https://youtu.be/9LpyDBPC3u4?si=WLFeq2aWEz-K6BzK"))
    view.add_item(discord.ui.Button(label="The Fortress", emoji="🇺🇸", url="https://www.youtube.com/watch?v=Ts2cRIz-MOc"))

    await ctx.send(embed=embed, view=view)

@mcsr.command(name="stronghold", description=language["comandos"]["mcsr"]["stronghold"])
async def mcsr_stronghold(ctx):
    embed = discord.Embed(title="Tutoriais Stronghold - Minecraft Speedrun", color=0x009739)
    embed.add_field(name="🇺🇸 Tutorial de como achar a Portal room usando o Pie Chart", value="Aprenda a encontrar a sala do portal com Pie Chart.", inline=False)
    embed.add_field(name="🇺🇸 Mini tutorial de Stronghold do Doogile", value="Dicas rápidas do Doogile sobre stronghold.", inline=False)
    embed.add_field(name="🇺🇸 Mini tutorial de Stronghold da MCSR Wiki", value="Resumo da Wiki sobre stronghold.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Preemptive Navigation", emoji="🇺🇸", url="https://youtu.be/6rxUEOFVmJ8?si=6tyVbL6PZmh_tFQy"))
    view.add_item(discord.ui.Button(label="The Stronghold (Doogile)", emoji="🇺🇸", url="https://youtu.be/iI8bntMXJzE?si=-5pE7PVqcQ0Jow0O"))
    view.add_item(discord.ui.Button(label="The Stronghold (Wiki)", emoji="🇺🇸", url="https://www.youtube.com/watch?v=9dZWe7dNNMg"))

    await ctx.send(embed=embed, view=view)

@mcsr.command(name="end", description=language["comandos"]["mcsr"]["end"])
async def mcsr_end(ctx):
    embed = discord.Embed(title="Tutoriais End - Minecraft Speedrun", color=0x009739)
    embed.add_field(name="🇺🇸 Tutorial de One cycle, a maneira mais fácil de Matar o Dragão", value="Aprenda a matar o dragão com One Cycle.", inline=False)
    embed.add_field(name="🇺🇸 Tutorial de como fazer Zero Cycle", value="Guia para executar o Zero Cycle.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="How to One Cycle", emoji="🇺🇸", url="https://www.youtube.com/watch?v=JaVyuTyDxxs"))
    view.add_item(discord.ui.Button(label="How to Zero Cycle", emoji="🇺🇸", url="https://www.youtube.com/watch?v=PB5UQB13VHc"))

    await ctx.send(embed=embed, view=view)

@mcsr.command(name="outros", description=language["comandos"]["mcsr"]["outros"])
async def mcsr_outros(ctx):
    embed = discord.Embed(title="Tutoriais Diversos - Minecraft Speedrun", color=0x009739)
    embed.add_field(name="🇺🇸 Tutorial de como Lotear baús super rápido", value="Aprenda a lotear baús de forma eficiente.", inline=False)
    embed.add_field(name="🇧🇷 Vídeo geral explicando como speedrun de MC funciona da Wendy", value="Entenda o básico do speedrun de Minecraft.", inline=False)
    embed.add_field(name="🇧🇷 Tutorial ANTIGO do Spectro, bom pra ter uma base", value="Tutorial clássico do Spectro.", inline=False)
    embed.add_field(name="🇧🇷 Vídeo Explicando como usar o Pie Chart", value="Como usar o Pie Chart para speedrun.", inline=False)
    embed = apply_standard_footer(embed, bot.user)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="How to loot Chests This fast", emoji="🇺🇸", url="https://www.youtube.com/watch?v=ebd3q3HNnQA"))
    view.add_item(discord.ui.Button(label="Record Mundial Explicado", emoji="🇧🇷", url="https://youtu.be/ei6bD9thnl0?si=tw3ltMESjdN62A5V"))
    view.add_item(discord.ui.Button(label="Dicas de como zerar o mine", emoji="🇧🇷", url="https://www.youtube.com/watch?v=zLGADTmfnkg"))
    view.add_item(discord.ui.Button(label="PieChart explicado", emoji="🇧🇷", url="https://www.youtube.com/watch?v=CoVfWydyIYI"))

    await ctx.send(embed=embed, view=view)

@commands.guild_only()
@bot.hybrid_group(name="set", description=language["comandos"]["set"]["group"])
@commands.has_permissions(administrator=True)
async def set(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Use um subcomando, exemplo: /set btrl", ephemeral=True)

@set.command(name="btrl", description=language["comandos"]["set"]["btrl"]["desc"])
@app_commands.describe(
    titulo=language["comandos"]["set"]["btrl"]["titulo"],
    descricao=language["comandos"]["set"]["btrl"]["descricao"],
    thumbnail=language["comandos"]["set"]["btrl"]["thumbnail"],
    imagem=language["comandos"]["set"]["btrl"]["imagem"]
)
async def set_btrl(ctx, titulo: str, descricao: str, thumbnail: str = None, imagem: str = None):
    try:
        data = load_btrl()
        data["titulo"] = titulo
        data["descricao"] = descricao.replace('\\n', '\n')
        data["thumbnail"] = thumbnail
        data["imagem"] = imagem
        save_btrl(data)
        await ctx.send("Informações da BTRL atualizadas com sucesso!", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Erro ao atualizar informações da BTRL: {e}", ephemeral=True)

@set.command(name="youtube", description=language["comandos"]["set"]["youtube"]["desc"])
@app_commands.describe(link=language["comandos"]["set"]["youtube"]["link"])
async def set_youtube(ctx, link: str):
    try:
        if not is_valid_url(link):
            await ctx.send("O link informado não é válido. Envie um link começando com http:// ou https://", ephemeral=True)
            return
        data = load_links()
        data["youtube"] = link
        save_links(data)
        await ctx.send("Link do YouTube atualizado com sucesso!", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Erro ao atualizar link do YouTube: {e}", ephemeral=True)

@set.command(name="twitch", description=language["comandos"]["set"]["twitch"]["desc"])
@app_commands.describe(link=language["comandos"]["set"]["twitch"]["link"])
async def set_twitch(ctx, link: str):
    try:
        if not is_valid_url(link):
            await ctx.send("O link informado não é válido. Envie um link começando com http:// ou https://", ephemeral=True)
            return
        data = load_links()
        data["twitch"] = link
        save_links(data)
        await ctx.send("Link da Twitch atualizado com sucesso!", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Erro ao atualizar link da Twitch: {e}", ephemeral=True)

@set.command(name="tiktok", description=language["comandos"]["set"]["tiktok"]["desc"])
@app_commands.describe(link=language["comandos"]["set"]["tiktok"]["link"])
async def set_tiktok(ctx, link: str):
    try:
        if not is_valid_url(link):
            await ctx.send("O link informado não é válido. Envie um link começando com http:// ou https://", ephemeral=True)
            return
        data = load_links()
        data["tiktok"] = link
        save_links(data)
        await ctx.send("Link do TikTok atualizado com sucesso!", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Erro ao atualizar link do TikTok: {e}", ephemeral=True)

class HelpView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.message = None
        self.is_admin = ctx.author.guild_permissions.administrator if hasattr(ctx.author, 'guild_permissions') else False

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

    async def update_embed(self, category, interaction):
        try:
            await self.message.edit(embed=None)
        except Exception:
            return
        if category == "Comandos MCSR Brasil":
            embed = discord.Embed(title="Comandos MCSR Brasil", color=0xFFFFFF)
            embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
            embed.add_field(
                name="\u200b",
                value=f"👋 Olá {self.ctx.author.mention}, utilize os botões abaixo para ver meus comandos!",
                inline=False,
            )
        else:
            embed = discord.Embed(title=f"{category}", color=0xFFFFFF)
            embed.set_thumbnail(url=self.ctx.bot.user.avatar.url)
            if category == "MCSR - Comandos":
                embed.add_field(
                    name="> **Total de comandos nesta categoria:** `8`.\n",
                    value=f"</mcsr config:1387812113787129960> - {language['comandos']['mcsr']['config']}\n"
                    f"</mcsr mapas:1387812113787129960> - {language['comandos']['mcsr']['mapas']}\n"
                    f"</mcsr overworld:1387812113787129960> - {language['comandos']['mcsr']['overworld']}\n"
                    f"</mcsr bastions:1387812113787129960> - {language['comandos']['mcsr']['bastions']}\n"
                    f"</mcsr fortalezas:1387812113787129960> - {language['comandos']['mcsr']['fortalezas']}\n"
                    f"</mcsr stronghold:1387812113787129960> - {language['comandos']['mcsr']['stronghold']}\n"
                    f"</mcsr end:1387812113787129960> - {language['comandos']['mcsr']['end']}\n"
                    f"</mcsr outros:1387812113787129960> - {language['comandos']['mcsr']['outros']}\n",
                    inline=False,
                )
            elif category == "Tabela - Comandos":
                embed.add_field(
                    name="> **Total de comandos nesta categoria:** `3`.\n",
                    value=f"</top rsg:1387812113787129958> - {language['comandos']['top']['rsg']}\n"
                    f"</top ssg:1387812113787129958> - {language['comandos']['top']['ssg']}\n"
                    f"</top ranked:1387812113787129958> - {language['comandos']['top']['ranked']}\n",
                    inline=False,
                )
            elif category == "Redes Sociais - Comandos":
                embed.add_field(
                    name="> **Total de comandos nesta categoria:** `3`.\n",
                    value=f"</youtube:1387812114063818904> - {language['comandos']['youtube']}\n"
                    f"</twitch:1387812114063818903> - {language['comandos']['twitch']}\n"
                    f"</tiktok:1387812113787129966> - {language['comandos']['tiktok']}\n",
                    inline=False,
                )
            elif category == "Especiais - Comandos":
                embed.add_field(
                    name="> **Total de comandos nesta categoria:** `1`.\n",
                    value=f"</btrl:1387812113787129962> - {language['comandos']['youtube']}\n",
                    inline=False,
                )
            elif category == "Moderação - Comandos" and self.is_admin:
                embed.add_field(
                    name="> **Total de comandos nesta categoria:** `6`.\n",
                    value=f"</say:1387812113787129965> - {language['comandos']['say']}\n"
                    f"</embed:1387812113787129964> - {language['comandos']['embed']}\n"
                    f"</set btrl:1387816222640574587> - {language['comandos']['set']['btrl']['desc']}\n"
                    f"</set youtube:1387816222640574587> - {language['comandos']['set']['youtube']['desc']}\n"
                    f"</set tiktok:1387816222640574587> - {language['comandos']['set']['tiktok']['desc']}\n"
                    f"</set twitch:1387816222640574587> - {language['comandos']['set']['twitch']['desc']}\n",
                    inline=False,
                )
        embed = apply_standard_footer(embed, bot.user)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="MCSR",
        style=discord.ButtonStyle.success,
        custom_id="mcsr_button",
        emoji="🎉"
    )
    async def mcsr_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.update_embed("MCSR - Comandos", interaction)

    @discord.ui.button(
        label="Tabelas",
        style=discord.ButtonStyle.success,
        custom_id="tabelas_button",
        emoji="🎉",
    )
    async def tabelas_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.update_embed("Tabela - Comandos", interaction)

    @discord.ui.button(
        label="Redes",
        style=discord.ButtonStyle.primary,
        custom_id="socials_button",
        emoji="🎉",
    )
    async def socials_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.update_embed("Redes - Comandos", interaction)

    @discord.ui.button(
        label="Especiais",
        style=discord.ButtonStyle.primary,
        custom_id="especiais_button",
        emoji="🎉",
    )
    async def especiais_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.update_embed("Especiais - Comandos", interaction)

    @discord.ui.button(
        label="Moderação",
        style=discord.ButtonStyle.gray,
        custom_id="moderation_button",
        emoji="👮",
    )
    async def moderation_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.is_admin:
            await self.update_embed("Moderação - Comandos", interaction)
        else:
            await interaction.response.send_message("Aba de moderação disponível apenas para administradores.", ephemeral=True)

    @discord.ui.button(
        label="Voltar", style=discord.ButtonStyle.danger, custom_id="back_button"
    )
    async def back_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.update_embed("Comandos MCSR Brasil", interaction)


@commands.guild_only()
@bot.hybrid_command(name="ajuda", description=language["comandos"]["ajuda"])
async def ajuda(ctx):
    try:
        embed = discord.Embed(title="Comandos MCSR Brasil", color=0xFFFFFF)
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        embed.add_field(
            name="\u200b",
            value=f"👋 Olá {ctx.author.mention}, utilize os botões abaixo para ver meus comandos!",
            inline=False,
        )
        embed = apply_standard_footer(embed, bot.user)
        view = HelpView(ctx)
        view.message = await ctx.send(embed=embed, view=view)
    except Exception as e:
        await ctx.send(f"Erro ao exibir ajuda: {e}", ephemeral=True)

class TopPaginationView(discord.ui.View):
    def __init__(self, ctx, results, tipo):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.results = results
        self.tipo = tipo
        self.page = 0
        self.per_page = 5
        self.message = None
        self.max_page = (len(results) - 1) // self.per_page
        self.previous_button = discord.ui.Button(label="Anterior", style=discord.ButtonStyle.primary, disabled=True)
        self.page_button = discord.ui.Button(label=f"Página 1/{self.max_page+1}", style=discord.ButtonStyle.gray, disabled=True)
        self.next_button = discord.ui.Button(label="Próximo", style=discord.ButtonStyle.primary, disabled=(self.max_page == 0))
        self.previous_button.callback = self.previous
        self.next_button.callback = self.next
        self.add_item(self.previous_button)
        self.add_item(self.page_button)
        self.add_item(self.next_button)

    def get_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        embed = discord.Embed(
            title=f"Top {self.tipo.upper()} 1.16+ Brasil",
            color=0x006B3C
        )
        top_emotes = [
            '<:gold_ingot:1390146844344062055>',
            '<:iron_ingot:1390146833485140018>',
            '<:copper_ingot:1390146817173360700>'
        ]
        emote_gold_block = '<:gold_block:1390147037902803084>'
        emote_clock = '<:clock:1390146877009170483>'
        emote_seed = '<:seed:1390146860697784370>'

        if self.tipo in ('rsg', 'ssg'):
            nomes = []
            tempos = []
            bastions = []
            seeds = []
            datas = []
            verifs = []
            for idx, run in enumerate(self.results[start:end]):
                pos = start + idx
                place = top_emotes[pos] if pos < 3 else f"#{pos+1}"
                nome = run['nome']
                profile = run.get('profile')
                if profile and isinstance(profile, str) and profile.startswith('http'):
                    nome_md = f"[{nome}]({profile})"
                else:
                    nome_md = f"{nome}"
                nomes.append(f"**{place}** - {nome_md}")
                video = run.get('video')
                if video and isinstance(video, str) and video.strip() and video.strip().lower() != 'n/a' and video.strip().startswith('http'):
                    tempos.append(f"{emote_clock} [ `{run['tempo']}` ]({video.strip()})")
                else:
                    tempos.append(f"{emote_clock} `{run['tempo']}`")
                if self.tipo == 'rsg':
                    bastion = str(run.get('bastion', '')).strip()
                    bastions.append(f"{emote_gold_block} `{bastion}`")
                else:
                    seed = str(run.get('seed_name', '')).strip()
                    if not seed:
                        seed = 'N/A'
                    if seed.endswith('`'):
                        seed = seed[:-1]
                    seeds.append(f"{emote_seed} `{seed}`")
                data_str = str(run['data']).strip()
                if data_str.endswith('`'):
                    data_str = data_str[:-1]
                datas.append(f"📅 `{data_str}`")
                verifs.append(f"🔎 `{run['verificada']}`")
            embed.add_field(name="Jogador", value='\n'.join(nomes) or '-', inline=True)
            embed.add_field(name="Tempo", value='\n'.join(tempos) or '-', inline=True)
            if self.tipo == 'rsg':
                embed.add_field(name="Bastion", value='\n'.join(bastions) or '-', inline=True)
            else: 
                embed.add_field(name="Seed", value='\n'.join(seeds) or '-', inline=True)
        elif self.tipo == 'ranked':
            nomes = []
            elos = []
            ranks = []
            for idx, run in enumerate(self.results[start:end]):
                pos = start + idx
                place = top_emotes[pos] if pos < 3 else f"#{pos+1}"
                nomes.append(f"**{place}** - [{run['nickname']}](https://mcsrranked.com/stats/{run['nickname']})")
                elos.append(f"{run['elo']}")
                ranks.append(f"{run['rank']}")
            embed.add_field(name="Jogador", value='\n'.join(nomes) or '-', inline=True)
            embed.add_field(name="Elo", value='\n'.join(elos) or '-', inline=True)
            embed.add_field(name="Rank", value='\n'.join(ranks) or '-', inline=True)
        embed.set_footer(text=f"Página {self.page+1}/{self.max_page+1}")
        return apply_standard_footer(embed, self.ctx.bot.user)

    async def update_page(self, interaction):
        self.page_button.label = f"Página {self.page+1}/{self.max_page+1}"
        self.previous_button.disabled = self.page == 0
        self.next_button.disabled = self.page == self.max_page
        embed = self.get_embed()
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except (discord.errors.InteractionResponded, discord.errors.NotFound):
            try:
                await interaction.followup.send("Esta interação expirou ou não está mais disponível. Envie o comando novamente!", ephemeral=True)
            except Exception:
                pass

    async def previous(self, interaction: discord.Interaction):
        try:
            if self.page > 0:
                self.page -= 1
                await self.update_page(interaction)
            else:
                await interaction.response.defer()
        except (discord.errors.InteractionResponded, discord.errors.NotFound):
            try:
                await interaction.followup.send("Esta interação expirou ou não está mais disponível. Envie o comando novamente!", ephemeral=True)
            except Exception:
                pass

    async def next(self, interaction: discord.Interaction):
        try:
            if self.page < self.max_page:
                self.page += 1
                await self.update_page(interaction)
            else:
                await interaction.response.defer()
        except (discord.errors.InteractionResponded, discord.errors.NotFound):
            try:
                await interaction.followup.send("Esta interação expirou ou não está mais disponível. Envie o comando novamente!", ephemeral=True)
            except Exception:
                pass

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass

bot.run(TOKEN)
