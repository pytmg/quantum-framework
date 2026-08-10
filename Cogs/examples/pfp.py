import discord
from discord.ext import commands
from Cogs.util import errorreport


class ProfilePictureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="pfp", description="Get anyone's profile picture")
    async def pfp(self, ctx: commands.Context, member: discord.User = None):
        """
        Parameters
        ----------
        member: discord.User
            Optionally specify who's profile picture you want to see.
        """
        # Command parameters can be documented in the docstring above.
        # Quantum Framework uses these descriptions when displaying command help.

        Profile = member or ctx.author

        embed = discord.Embed(
            title="Profile Picture",
            description=f"{Profile.mention}'s profile picture",
            color=0x82ffb2
        )

        # Embeds can include a footer to show who requested the command.
        # This is useful for commands where the response may be visible to
        # multiple people.
        embed.set_footer(
            text=f"Requested by: {ctx.author.name}",
            icon_url=ctx.author.avatar.url
        )

        embed.set_image(url=Profile.avatar.url)

        await ctx.reply(embed=embed)

    async def handle_err(
        self,
        ctx: commands.Context,
        error: Exception
    ) -> errorreport:
        # Cogs can provide their own error handler by defining handle_err.
        # Return errorreport.handled or errorreport(True) when the error has been dealt with here.
        if ctx.command.name == self.pfp.name:
            # Check the specific command before handling its errors.
            if isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
                embed = discord.Embed(
                    title=":x: Member not found.",
                    description="I don't know who that member is.",
                    color=0xff0000
                )

                await ctx.reply(embed=embed)

                return errorreport.handled


async def setup(bot: commands.Bot):
    # Every cog needs a setup function so the CogHandler can load it.
    await bot.add_cog(ProfilePictureCog(bot))