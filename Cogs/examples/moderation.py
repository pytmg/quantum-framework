import discord
from discord.ext import commands
from Cogs.util import commands_extra, errorreport

class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Hybrid commands work as both prefix and slash commands.
    @commands.hybrid_command(name="ban", description="Ban a user.")
    @commands_extra.has_guild_permissions(ban_members=True) # Use this instead of commands.has_guild_permissions so permissions show in Help.
    async def ban_command(self, ctx: commands.Context, *, member: discord.Member) -> None:
        """
        Parameters
        ----------
            member: discord.Member
                The member you want to ban.
        """
        try:
            await ctx.guild.ban(member)
            await ctx.reply(f"Member {member.display_name} was successfully banned.")
        except discord.Forbidden:
            # The bot itself does not have permission to ban the member.
            await ctx.reply(f"I do not have the necessary permissions to ban users.", ephemeral=True) # ephemeral will show up for nobody except the person invoking the command

    async def handle_err(self, ctx: commands.Context, err: Exception) -> errorreport:
        if ctx.command.name == self.ban_command.name:
            # CheckFailure is raised when the permission check above fails for the user.
            if isinstance(err, commands.errors.CheckFailure): # This error can show up in slash commands
                await ctx.reply("You need to have the Ban Members permission to use this command.", ephemeral=True)
                return errorreport.handled
            # MissingRequiredArgument is raised when the user does not provide the required argument.
            if isinstance(err, commands.errors.MissingRequiredArgument): # This error cannot show up in slash commands
                if str(err).startswith("member"):
                    await ctx.reply("You need to provide a member to ban.")
                    return errorreport.handled
        return errorreport.globalhandler

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))