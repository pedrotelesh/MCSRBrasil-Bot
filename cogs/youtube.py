import discord
from discord.ext import commands
from discord import app_commands
import logging

from utilities.utility import load_yt_tt_links
import utilities.config_loader as config

language = config.load_current_language()

logging.basicConfig(level=logging.INFO)

class YoutubeCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
	
    @commands.guild_only()
    @commands.hybrid_command(name="youtube", description=language["comandos"]["youtube"])
    async def youtube(self, ctx):
        try:
            if hasattr(ctx, 'interaction') and ctx.interaction is not None:
                await ctx.defer()
            links = load_yt_tt_links()
            youtube_link = links.get("youtube")
            if not youtube_link:
                await ctx.send("Nenhum link do YouTube foi configurado ainda! Use /set youtube para definir.", ephemeral=True)
                return
            embed = discord.Embed(title="YouTube: Minecraft Speedrunning Brasil",
                description="Inscreva-se no nosso canal para vídeos, highlights e tutoriais!",
                color=0xFF0000
            )
            embed.set_thumbnail(url="https://i.ibb.co/SwVkd7Dj/1590430652red-youtube-logo-png-xl.png")
            view = discord.ui.View()
            button = discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="Clique aqui!",
                url=youtube_link,
                emoji="🔗",
            )
            view.add_item(button)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            logging.error(f"Erro no comando do YouTube: {e}")
            await ctx.send("Oops, parece que ocorreu um erro!? :cry:")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YoutubeCog(bot))