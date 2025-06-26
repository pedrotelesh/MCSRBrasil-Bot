import discord
from discord.ext import commands
from discord import app_commands
import logging

import utilities.config_loader as config

language = config.load_current_language()

logging.basicConfig(level=logging.INFO)

def is_valid_image_url(url: str) -> bool:
    image_extensions = (".jpg", ".jpeg", ".png", ".gif")
    if url.startswith("http://") or url.startswith("https://"):
        return url.lower().endswith(image_extensions)
    return False

class embed(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
	
    @commands.guild_only()
    @commands.hybrid_command(name="embed", description=language["comandos"]["embed"])
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        titulo="Título da embed",
        descricao="Descrição da embed que deseja enviar! (Permitido Markdown)",
        canal="Canal para enviar a mensagem",
        thumbnail="Imagem pequena da embed",
        imagem="Imagem grande da embed")
    async def embed(self, ctx, titulo: str, descricao: str, thumbnail: str = None, imagem: str = None, canal: discord.TextChannel = None):
        try:
            if thumbnail and not is_valid_image_url(thumbnail):
                await ctx.send("**O URL do thumbnail não é válido.**\nCertifique-se de que seja um link e termine com uma extensão de imagem válida (.jpg, .jpeg, .png, .gif).", ephemeral=True)
                return

            if imagem and not is_valid_image_url(imagem):
                await ctx.send("**O URL da imagem não é válido.**\nCertifique-se de que seja um link e termine com uma extensão de imagem válida (.jpg, .jpeg, .png, .gif).", ephemeral=True)
                return
            embed = discord.Embed(
                title=titulo,
                color=0xFFFFFF,
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            if imagem:
                embed.set_image(url=imagem)
            embed.description = descricao.replace('\\n', '\n')
            embed.set_footer(text=f"{config.embed_footer}", icon_url=self.bot.user.avatar.url)
            if canal:
                await canal.send(embed=embed)
                return await ctx.send(f"A embed foi enviada para o canal <#{canal.id}> com sucesso!", ephemeral=True)
            else:
                await ctx.channel.send(embed=embed)
                await ctx.send("Embed enviada com sucesso!", ephemeral=True)
        except Exception as e:
            logging.error(f"Erro ao enviar embed: {e}")
            await ctx.send("Oops, parece que ocorreu um erro!? :cry:")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(embed(bot))