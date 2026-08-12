import discord, datetime
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # hybrid_command allows this to be used as both a prefix and slash command.
    @commands.hybrid_command(name="ping", description="Check the bot's latency.")
    async def pingpong(self, ctx: discord.Interaction | commands.Context):
        latency = round(self.bot.latency * 1000)
        starttime = datetime.datetime.now()

        # ctx.interaction is present when the command was invoked as a slash command.
        if ctx.interaction:
            # Slash commands need to be acknowledged before sending a followup.
            await ctx.interaction.response.defer()

            endtime = datetime.datetime.now()
            bot_latency = (endtime - starttime).total_seconds() * 1000

            string = ":ping_pong: **Pong!**"
            string += f"\n**Discord Latency:** `{latency}ms`"
            string += f"\n**Bot Latency:** `{round(bot_latency)}ms`"

            await ctx.interaction.followup.send(string)

        # Without an interaction, the command was invoked as a prefix command.
        else:
            message = await ctx.reply(":ping_pong: **Pong!**\n[Please Wait...]")

            endtime = datetime.datetime.now()
            bot_latency = (endtime - starttime).total_seconds() * 1000

            string = ":ping_pong: **Pong!**"
            string += f"\n**Discord Latency:** `{latency}ms`"
            string += f"\n**Bot Latency:** `{round(bot_latency)}ms`"

            await message.edit(content=string)


# This is the entry point Quantum uses when loading the cog.
async def setup(bot: commands.Bot):
    await bot.add_cog(PingCog(bot))
