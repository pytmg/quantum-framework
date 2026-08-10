import discord, os, asyncio, sys, traceback, shutil, requests
from dotenv import load_dotenv as env
from typing import Optional, Literal
from discord.ext import commands
from Cogs.util import Debugger, errorreport
from report import Reporter


env()

# Global exception handler for errors that escape the normal command/event handling.
def handle_exception(exc_type, exc_value, exc_traceback):
    if exc_type is KeyboardInterrupt:
        return
    print("Uncaught exception", exc_type, exc_value)
    traceback.print_tb(exc_traceback)


sys.excepthook = handle_exception

token = os.getenv("token")

intents = discord.Intents.all()

# The entrypoint intentionally has very few commands.
# Most functionality is provided by extensions loaded through CogHandler.
bot = commands.Bot(
    command_prefix="!",
    help_command=None,
    intents=intents
)

# Temporary files are cleared on startup so a previous run cannot leave stale data.
try:
    shutil.rmtree("temp")
except:
    pass

os.makedirs("temp")


@bot.event
async def on_ready():
    print(f"[login.report] Logged in as {bot.user.name}")

    activity = discord.CustomActivity(
        name="Based on Quantum Framework by pytmg",
        type=discord.ActivityType.custom
    )

    status = discord.Status.online

    await bot.change_presence(
        activity=activity,
        status=status
    )

    print(f"[login.report.debug] Debugger Active?: {Debugger.IsEnabled()}")


@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None
) -> None:
    """
    Manually synchronise application commands.

    ~  Sync commands already registered to the current guild.
    *  Copy global commands to the current guild and sync them.
    ^  Clear commands from the current guild and sync.
    """

    try:
        if not guilds:
            if spec == "~":
                synced = await bot.tree.sync(guild=ctx.guild)

            elif spec == "*":
                bot.tree.copy_global_to(guild=ctx.guild)
                synced = await bot.tree.sync(guild=ctx.guild)

            elif spec == "^":
                bot.tree.clear_commands(guild=ctx.guild)
                synced = await bot.tree.sync(guild=ctx.guild)

            else:
                synced = await bot.tree.sync()

            await ctx.reply(
                f"Synced {len(synced):,} commands "
                f"{'globally' if spec is None else 'to the current guild.'}"
            )

            return

    except Exception as e:
        print(f"{e.__class__.__name__}: {e}")


@bot.command()
@commands.is_owner()
async def loadrequirements(ctx: commands.Context):
    """
    Manually restore the minimum extensions required for developer tooling.

    This command exists specifically for the situation where CogHandler itself
    failed during startup, leaving the bot with only the commands defined here.
    """

    coghandler = "Cogs._core.coghandler"

    # CogHandler normally loads itself during startup. If that failed, try loading
    # it manually so the rest of the extension system can become available again.
    if coghandler not in bot.extensions:
        msg = await ctx.reply("how does the HANDLER fail to load?")

        try:
            await bot.load_extension(coghandler)
        except Exception as e:
            await msg.edit(
                content=f"An error occured.\n{e.__class__.__name__}: {e}"
            )

    cogCog = "Cogs._dev.cogs"

    # _dev.cogs contains the developer-only cog management commands.
    # It should not normally already be loaded when this recovery command is used.
    if cogCog in bot.extensions and coghandler in bot.extensions:
        raise commands.CommandNotFound("you suck")

    Msg = await ctx.reply(f"Reloading {cogCog}")

    try:
        await bot.load_extension(cogCog)
    except Exception as e:
        await Msg.edit(
            content=f"An error occured.\n{e.__class__.__name__}: {e}"
        )
    else:
        await Msg.edit(content=f"{cogCog} reloaded.")


@bot.command()
async def recovercoghandler(ctx: commands.Context):
    """
    Recover CogHandler directly from the Quantum Framework repository.

    This is the last-resort recovery command. It downloads a known copy of
    CogHandler, loads it under a temporary module name to test it, then replaces
    the local copy only after the temporary extension successfully exposes
    bot.cog_handler.
    """

    # If CogHandler is already available, require explicit confirmation before
    # replacing it. This prevents accidental recovery over a working handler.
    if getattr(bot, "cog_handler", None):
        msg = await ctx.reply(
            "CogHandler exists. Are you sure you want to recover it? "
            "Type `YES` to confirm."
        )

        def check(c):
            return c.author == ctx.author

        event = await bot.wait_for("message", check=check)

        if event.content != "YES":
            await msg.edit(content="CogHandler exists.")
            return

        await msg.delete()

    # Download the replacement rather than importing/replacing the currently
    # loaded CogHandler directly.
    r = requests.get(
        "https://raw.githubusercontent.com/pytmg/quantum-framework/"
        "refs/heads/main/Cogs/_core/coghandler.py"
    )
    r.raise_for_status()

    temp_path = os.path.join(
        os.path.dirname(__file__),
        "Cogs",
        "_core",
        "coghandler_temp.py"
    )

    with open(temp_path, "w") as f:
        f.write(r.text)

    try:
        # Loading under a temporary module name lets us test the downloaded
        # handler without replacing the currently installed file first.
        await bot.load_extension("Cogs._core.coghandler_temp")

        coghandler = getattr(bot, "cog_handler", None)

        if coghandler:
            msg = await ctx.reply("CogHandler might be working.")

            # Remove the temporary extension before replacing the actual module.
            await bot.unload_extension("Cogs._core.coghandler_temp")

            original_path = os.path.join(
                os.path.dirname(__file__),
                "Cogs",
                "_core",
                "coghandler.py"
            )

            os.remove(original_path)
            os.rename(temp_path, original_path)

            # Load the recovered handler under its real extension name.
            await bot.load_extension("Cogs._core.coghandler")

            await msg.edit(
                content="CogHandler shows up. Do you want to try running CogHandler?\n"
                        "Type `YES` to confirm."
            )

            def check(c):
                return c.author == ctx.author

            event = await bot.wait_for("message", check=check)

            if event.content == "YES":
                try:
                    CogReport, _, l, _, _ = await bot.cog_handler.LoadAllCogs(
                        bot,
                        "Cogs",
                        ignore_no_setup=True,
                        silent=True
                    )

                    await event.reply(f"Loaded {len(l)} cogs.")

                except Exception as e:
                    await event.reply(
                        f"CogHandler is broken.\n"
                        f"{e.__class__.__name__}: {e}"
                    )

                return

        else:
            await ctx.reply("CogHandler is broken.")

    except Exception as e:
        await ctx.reply(f"{e.__class__.__name__}: {e}")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    # Handle unknown commands ourselves because the default help command is disabled.
    if isinstance(error, commands.CommandNotFound):
        Embed = discord.Embed()
        Embed.title = ":x: Command not found"
        Embed.description = (
            f"The command `{ctx.message.content[len(bot.command_prefix):].split()[0]}` "
            "was not found."
        )
        Embed.color = 0xff0000
        await ctx.reply(embed=Embed)
        return

    # Commands marked as guild-only cannot be used from DMs.
    if isinstance(error, commands.NoPrivateMessage):
        embed = discord.Embed(
            title=":x: DMs",
            description="You cannot use server-required commands in DMs.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

    # Cogs can provide their own error handler for command-specific errors.
    # This keeps command-specific behaviour inside the cog instead of putting
    # every possible error case into the global handler.
    if ctx.command.cog:
        if getattr(ctx.command.cog, "handle_err", None):
            Debugger.print(
                f"Passing error handling to cog {ctx.command.cog_name}"
            )

            returned = await ctx.command.cog.handle_err(ctx, error)

            if isinstance(returned, errorreport):
                Debugger.print(
                    f"{ctx.command.cog_name} returned a "
                    f"{'success' if returned.success else 'failure'}"
                )

                if returned.success:
                    return

            else:
                Debugger.print(
                    f"{ctx.command.cog_name} returned an unknown report."
                )

    # Don't dump command exceptions unless debugging is enabled.
    if not Debugger.IsEnabled():
        return

    print("\x1b[31m")
    print("Exception in command:", ctx.command)
    traceback.print_exception(
        type(error),
        error,
        error.__traceback__
    )
    print("\x1b[0m")


def handle_async_exception(loop, context):
    """
    Handle exceptions raised by asyncio tasks that aren't propagated normally.
    """

    msg = context.get("exception", context["message"])
    print(f"Uncaught async exception: {msg}")

    if "exception" in context:
        traceback.print_exception(
            type(context["exception"]),
            context["exception"],
            context["exception"].__traceback__
        )


async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(handle_async_exception)

    # CogHandler and the extensions it loads may need to know where the
    # entrypoint is, for example when restarting the bot.
    bot.entry = __file__

    try:
        # CogHandler is optional for startup. If it fails, the bot still starts
        # with the minimal bootstrap commands above so the handler can be repaired.
        await bot.load_extension("Cogs._core.coghandler")

        CogReport, _, _, _, _ = await bot.cog_handler.LoadAllCogs(
            bot,
            "Cogs",
            ignore_no_setup=True,
            silent=True
        )

        Debugger.print(
            Reporter.SReport(
                CogReport,
                beautify=True,
                leftcolumn="Cog"
            )
        )

    except Exception as e:
        # Do not prevent the bot from starting if the extension system is broken.
        # loadrequirements and recovercoghandler are intentionally kept available
        # for exactly this situation.
        print(
            f"!!WARNING!! CogHandler failed to load. "
            f"Use {bot.command_prefix}loadrequirements to reload CogHandler "
            f"when it's fixed!\n"
            f"Or use {bot.command_prefix}recovercoghandler to restore a "
            f"functional CogHandler.\n\n"
            f"{e.__class__.__name__}: {e}"
        )

    try:
        await bot.start(token)

    except KeyboardInterrupt:
        await bot.close()
        sys.exit(0)

    except Exception as e:
        sys.excepthook(
            type(e),
            e,
            e.__traceback__
        )


asyncio.run(main())