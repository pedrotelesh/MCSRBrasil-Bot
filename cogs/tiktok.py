import discord
from discord.ext import commands
from discord import app_commands
import logging

from utilities.utility import load_yt_tt_links
import utilities.config_loader as config

language = config.load_current_language()

logging.basicConfig(level=logging.INFO)

class TiktokCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.guild_only()
    @commands.hybrid_command(name="tiktok", description=language["comandos"]["tiktok"])
    async def tiktok(self, ctx):
        try:
            if hasattr(ctx, 'interaction') and ctx.interaction is not None:
                await ctx.defer()
            links = load_yt_tt_links()
            tiktok_link = links.get("tiktok")
            if not tiktok_link:
                await ctx.send("Nenhum link do TikTok foi configurado ainda! Use /set tiktok para definir.", ephemeral=True)
                return
            embed = discord.Embed(title="TikTok: Minecraft Speedrunning Brasil",
                description="Veja nossos melhores clipes e vídeos curtos no TikTok!",
                color=0x010101
            )
            embed.set_thumbnail(url="https://i.ibb.co/MxF30kjz/tiktok-6338432-1280.png")
            view = discord.ui.View()
            button = discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="Clique aqui!",
                url=tiktok_link,
                emoji="🔗",
            )
            view.add_item(button)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            logging.error(f"Erro no comando do TikTok: {e}")
            await ctx.send("Oops, parece que ocorreu um erro!? :cry:")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TiktokCog(bot))