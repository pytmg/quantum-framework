import discord, random
from discord.ext import commands


class CoinFlipCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Basic command example.
    # Hybrid commands can be used with both a prefix and a slash command.
    @commands.hybrid_command(name="coin", description="Flip a coin.")
    async def coin(self, ctx: commands.Context | discord.Interaction):
        await ctx.reply(random.choice(["Tails!", "Heads!"]))


async def setup(bot: commands.Bot):
    # This function is required for the CogHandler to load the cog.
    await bot.add_cog(CoinFlipCog(bot))