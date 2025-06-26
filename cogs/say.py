import discord
from discord.ext import commands
from discord import app_commands
import logging

import utilities.config_loader as config

language = config.load_current_language()

logging.basicConfig(level=logging.INFO)

class say(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
	
    @commands.guild_only()
    @commands.hybrid_command(name="say", description=language["comandos"]["say"])
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        mensagem="Escreva a mensagem que você quer enviar!",
        canal="Canal para enviar a mensagem.")
    async def say(self, ctx, mensagem: str, canal: discord.TextChannel = None):
        try:
            if canal:
                await canal.send(mensagem)
                return await ctx.send(f"A mensagem foi enviada para o canal <#{canal.id}> com sucesso!", ephemeral=True)
            else:
                await ctx.channel.send(mensagem)
                await ctx.send("Mensagem enviada com sucesso!", ephemeral=True)
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem: {e}")
            await ctx.send("Oops, parece que ocorreu um erro!? :cry:")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(say(bot))