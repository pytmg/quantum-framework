import subprocess, sys
from pathlib import Path
from discord.ext import commands
from Cogs.util import errorreport

class DeveloperCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command groups let you organize related commands under one command.
    # The owner check applies to the group, so all developer commands are
    # restricted to the bot owner by default.
    @commands.group(name="dev", description="Developer Tooling")
    @commands.is_owner()
    async def dev(self, ctx: commands.Context):
        if ctx.invoked_subcommand:
            return

        # If no subcommand was provided, show the commands available
        # under the developer command group.
        await ctx.reply(", ".join([cmd.name for cmd in self.dev.commands]))

    @dev.command(name="restart", description="Restart the bot.")
    async def restart(self, ctx: commands.Context):
        await ctx.reply(f"Restarting {self.bot.user.name}.. please wait.")

        # Run the bot's entrypoint again using the same Python interpreter.
        # bot.entry is set by the main bot file and points to the entrypoint
        # that should be executed when restarting.
        subprocess.run(
            [sys.executable, self.bot.entry],
            shell=True,
            cwd=Path(self.bot.entry).parent
        )
        self.bot.close()
        sys.exit(0)

    async def handle_err(self, ctx: commands.Context, err: Exception) -> errorreport:
        if isinstance(err, commands.errors.NotOwner):
            return errorreport.handled
        return errorreport.globalhandler

async def setup(bot: commands.Bot):
    # This function is required for the CogHandler to load the cog.
    await bot.add_cog(DeveloperCog(bot))