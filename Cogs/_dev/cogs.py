import discord, traceback, os
from discord.ext import commands
from Cogs.util import Debugger

class cogsCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def reload(self, ctx, without: str = ""):
        # Reload every cog through CogHandler rather than manually reloading
        # each extension. CogHandler also detects newly added and removed cogs.
        _, reloaded, added, removed, errors = await self.bot.cog_handler.LoadAllCogs(
            self.bot,
            exceptions=without
        )

        embed = discord.Embed(
            title=":white_check_mark: Reload complete",
            color=0x82ffb2
        )

        # Only add sections for things that actually happened, keeping the
        # response compact when there are no changes.
        if reloaded:
            embed.add_field(
                name="Reloaded",
                value="`" + "`, `".join(reloaded) + "`",
                inline=False
            )

        if added:
            embed.add_field(
                name="Added",
                value="`" + "`, `".join(added) + "`",
                inline=False
            )

        if removed:
            embed.add_field(
                name="Removed",
                value="`" + "`, `".join(removed) + "`",
                inline=False
            )

        if errors:
            err_text = '\n'.join(
                [f"`{mod}`: {msg}" for mod, msg in errors]
            )
            embed.add_field(
                name="Errors",
                value=err_text or "None",
                inline=False
            )

        if not any([reloaded, added, removed, errors]):
            embed.description = "No cogs found."

        await ctx.reply(embed=embed)

        print("-!- COGS RELOADED -!-")

    @commands.group(name="cogs")
    @commands.is_owner()
    async def coggle(self, ctx: commands.Context):
        # Running `cogs` without a subcommand simply displays the available
        # subcommands instead of performing an action.
        if ctx.invoked_subcommand is None:
            CogCmd = self.bot.get_command("cogs")
            await ctx.reply(
                "*" + "*, *".join([Cmd.name for Cmd in CogCmd.commands]) + "*"
            )

    @coggle.group(
        name="reload",
        aliases=["r", "rl", "refresh", "rf"]
    )
    @commands.is_owner()
    async def reloadCogs(self, ctx, *, cogs: str = ""):
        # With no cog names supplied, use CogHandler to reconcile the entire
        # Cogs directory with the currently loaded extensions.
        if ctx.invoked_subcommand is None and cogs == "":
            await self.reload(ctx)

        # When specific extensions are supplied, reload only those extensions.
        if cogs:
            errs, succ = [], []

            for cog in cogs.split():
                try:
                    await self.bot.reload_extension(cog)
                    succ.append({"cog": cog, "err": None})
                except Exception as e:
                    errs.append({"cog": cog, "err": e})

            embed = discord.Embed(
                title=":white_check_mark: Reload complete",
                color=0x82ffb2
            )

            if succ:
                embed.add_field(
                    name="Successes",
                    value="`" + "`, `".join([cog["cog"] for cog in succ]) + "`",
                    inline=False
                )

            if errs:
                embed.add_field(
                    name="Failures",
                    value="`" + "`, `".join([cog["cog"] for cog in errs]) + "`",
                    inline=False
                )

            if not any([succ, errs]):
                embed.description = "No cogs reloaded..?"

            await ctx.reply(embed=embed)

    @reloadCogs.command(
        name="without",
        aliases=["wo", "rm", "remove"]
    )
    @commands.is_owner()
    async def reloadWithout(self, ctx, *, blocked: str = ""):
        # Reload everything through CogHandler while explicitly excluding
        # the extensions supplied by the user.
        await self.reload(ctx, blocked)

    @coggle.command(name="load", aliases=["l"])
    @commands.is_owner()
    async def loadCogs(self, ctx, *, cog: str):
        try:
            # Allow developers to provide either `foo.bar` or `Cogs.foo.bar`.
            # The actual extension is always loaded from the Cogs package.
            if cog.startswith("Cogs."):
                cog = cog.replace("Cogs.", "")

            await self.bot.load_extension(f'Cogs.{cog}')
            await ctx.reply(f"Loaded {cog}")
            print(f"--- COG : {cog} Loaded ---")

        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.reply(f"Cog {cog} was already loaded.")

        except Exception as e:
            # Keep the Discord response short and put the complete traceback
            # in the terminal where it is actually useful for debugging.
            tb_str = ''.join(
                traceback.format_exception(type(e), e, e.__traceback__)
            )
            await ctx.reply("somethin went wrong, check the termy")
            print(tb_str)

    @coggle.command(name="unload", aliases=["ul"])
    @commands.is_owner()
    async def unloadCogs(self, ctx, *, cog: str):
        try:
            # Unlike `load`, this accepts the full extension name because
            # discord.py needs the exact key used in bot.extensions.
            await self.bot.unload_extension(f'{cog}')
            await ctx.reply(f"Unloaded {cog}")
            print(f"--- COG : {cog} Unloaded ---")

        except commands.errors.ExtensionNotLoaded:
            await ctx.reply(f"Cog {cog} was never loaded.")

        except Exception as e:
            # As with loading, don't dump the traceback into Discord.
            tb_str = ''.join(
                traceback.format_exception(type(e), e, e.__traceback__)
            )
            await ctx.reply("somethin went wrong, check the termy")
            print(tb_str)

    @coggle.command(name="view", aliases=["v", "ls", "list"])
    @commands.is_owner()
    async def viewCogs(self, ctx):
        # bot.extensions contains the currently loaded extension names.
        # This gives developers a quick way to inspect the bot's extension state.
        loaded_cogs = '`\n- `'.join(self.bot.extensions.keys())

        await ctx.reply(
            f"Loaded cogs: ({len(self.bot.extensions)})\n- `{loaded_cogs}`"
            [:1500] + ("`..." if len(loaded_cogs) > 1500 else "")
        )

async def setup(bot):
    await bot.add_cog(cogsCommands(bot))