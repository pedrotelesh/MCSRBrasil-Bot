import discord
from discord.ext import commands
import json
import os
from utilities.embed_utils import apply_standard_footer

BTRL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'btrl.json')

def load_btrl():
    with open(BTRL_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

class BTRL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="btrl", description="Mostra as informações do evento Break The Record Live (BTRL)")
    async def btrl(self, ctx):
        data = load_btrl()
        embed = discord.Embed(title=data["titulo"], color=0x009739)
        embed.description = data["descricao"]
        if data.get("thumbnail"):
            embed.set_thumbnail(url=data["thumbnail"])
        if data.get("imagem"):
            embed.set_image(url=data["imagem"])
        bot_user = ctx.bot.user if hasattr(ctx, 'bot') else self.bot.user
        embed = apply_standard_footer(embed, bot_user=bot_user)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BTRL(bot))
