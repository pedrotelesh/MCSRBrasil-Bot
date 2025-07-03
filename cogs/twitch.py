import discord
from discord.ext import commands
from discord import app_commands
import logging

from utilities.utility import load_links
import utilities.config_loader as config

language = config.load_current_language()

logging.basicConfig(level=logging.INFO)

class TwitchCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
	
    @commands.guild_only()
    @commands.hybrid_command(name="twitch", description=language["comandos"]["twitch"])
    async def twitch(self, ctx):
        try:
            if hasattr(ctx, 'interaction') and ctx.interaction is not None:
                await ctx.defer()
            links = load_links()
            twitch_link = links.get("twitch")
            if not twitch_link:
                await ctx.send("Nenhum link da Twitch foi configurado ainda! Use /set twitch para definir.", ephemeral=True)
                return
            embed = discord.Embed(title="Twitch: Minecraft Speedrunning Brasil",
                description="Aqui fazemos todas as lives dos nossos torneios!",
                color=0x9146FF
            )
            embed.set_thumbnail(url="https://i.ibb.co/9kdyVpsk/twitch-PNG48.png")
            view = discord.ui.View()
            button = discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="Clique aqui!",
                url=twitch_link,
                emoji="🔗",
            )
            view.add_item(button)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            logging.error(f"Erro no comando da Twitch: {e}")
            await ctx.send("Oops, parece que ocorreu um erro!? :cry:")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TwitchCog(bot))