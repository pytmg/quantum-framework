import discord
from typing import Any
from discord.ext import commands
from dataclasses import dataclass, field

class Paginator:
    def __init__(self, data: list[Any], items_per_page: int):
        self.data = data
        self.items_per_page = items_per_page
        self._page = 0

    @property
    def pages(self):
        return [self.data[i:i+self.items_per_page] for i in range(0, len(self.data), self.items_per_page)] if len(self.data) != 0 else []

    @property
    def page_count(self):
        return len(self.pages)

    def page(self, page: int = None):
        if page is not None:
            self._page = page
        if len(self.pages) == 0:
            return None
        if page >= len(self.pages):
            return self.pages[-1]
        if page < 0:
            return self.pages[0]
        return self.pages[self._page]

class classproperty(property):
    def __get__(self, obj, objtype=None):
        return self.fget(objtype)
        
class errorreport: # used in cogs' error handlers, see examples/
    """
    A class for Quantum Framework's error handling, expected when a cog has its own error handler.
    """
    def __init__(self, success: bool = False):
        self.success = success

    @classproperty
    def handled(self) -> "errorreport":
        """
        The error was handled.
        """
        return errorreport(success=True)

    @classproperty
    def unhandled(self) -> "errorreport":
        """
        The error was not handled.
        """
        return errorreport(success=False)

class commands_extra: # Functions for Help to know what permissions are required for the user to run the command.
    @staticmethod
    def has_permissions(**permissions):
        def decorator(func):
            async def predicate(ctx: commands.Context = None):
                if not ctx:
                    return permissions
                return all(
                    getattr(ctx.author.guild_permissions, perm) == value
                    for perm, value in permissions.items()
                )
            return commands.check(predicate)(func)

        return decorator
    
    @staticmethod
    def has_guild_permissions(**permissions):
        return commands_extra.has_permissions(**permissions)
    
class Debugger:
    @staticmethod
    def IsEnabled() -> bool:
        try:
            with open("Cogs/debugging", "r") as f:
                data = f.read()
                if data == "":
                    with open("Cogs/debugging", "w") as f:
                        f.write("0\n\n!!!DO NOT OVERWRITE THIS FILE!!!")
                    return False
                lines = data.splitlines()
                try:
                    return len(lines) > 0 and int(lines[0]) == 1
                except ValueError:
                    print("-!- DEBUG FILE MALFORMED -!- attempting fix -!-")
                    try:
                        with open("Cogs/debugging", "w") as f:
                            f.write("0\n\n!!!DO NOT OVERWRITE THIS FILE!!!")
                        print("--- DEBUG FILE FIXED ---")
                    except Exception as e:
                        print(f"!!! CANNOT FIX DEBUG FILE !!! {e.__class__.__name__} : {e} !!!")
                    return False
        except FileNotFoundError:
            with open("Cogs/debugging", "w") as f:
                f.write("0\n\n!!!DO NOT OVERWRITE THIS FILE!!!")
            return False
        
    @staticmethod
    def print(*text):
        """
        Print text to the terminal if debugging is enabled.

        Parameters:
            *text (str): The text to print to the terminal.
        """
        if Debugger.IsEnabled():
            print(*text)
        return

@dataclass
class CommandInfo:
    name: str
    full_name: str
    description: str
    category: str
    prefix: str
    permissions: list[str]

    cog: str | None = None
    module: str | None = None

    guild_only: bool = False
    hidden: bool = False
    aliases: list[str] = field(default_factory=list)
    params: list[dict] = field(default_factory=list)
    subcommands: list["CommandInfo"] = field(default_factory=list)

    def __repr__(self):
        return self.name

# Type aliases, unused outside of utils.py
GroupTypes = commands.Group | commands.HybridGroup | discord.app_commands.Group
CommandTypes = commands.Command | commands.HybridCommand | discord.app_commands.Command
SlashTypes = discord.app_commands.Command | discord.app_commands.Group
HybridTypes = commands.HybridCommand | commands.HybridGroup
PrefixTypes = commands.Command | commands.Group
AllCommandTypes = GroupTypes | CommandTypes

class CommandRegistry:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_commands(self) -> list[CommandInfo]:
        return [
            await self.inspect(command) for command in self.bot.commands
        ]

    @staticmethod
    def get_category(command: AllCommandTypes) -> str:
        Ext = command.module
        if Ext.startswith("__main__"): # Commands in __main__, such as !sync or !loadcoghandler
            return "_dev"
        return Ext.split(".")[-2] # example: Cogs.Fun.extension -> Fun

    async def get_all_categories(self, *, with_command_info: bool = False) -> list[str] | dict[str, list[CommandInfo]]:
        Categories = {} if with_command_info else []
        ALLCMDS = list(self.bot.commands)
        names = [cmd.name for cmd in ALLCMDS]
        ALLCMDS.extend([cmd for cmd in self.bot.tree.get_commands(type=(discord.AppCommandType.chat_input)) if cmd.name not in names])
        for cmd in ALLCMDS:
            cat = self.get_category(cmd)
            if cat not in Categories:
                if with_command_info:
                    Categories[cat] = []
                else:
                    Categories.append(cat)
            if with_command_info:
                Categories[cat].append(await self.inspect(cmd, only_subcommand_names=True)) # Subcommands will not be needed, as we really only need the names and desc
        return Categories

    @staticmethod
    def get_subcommand_names(command: GroupTypes) -> list[str]:
        if not isinstance(command, GroupTypes):
            return []
        return [cmd.name for cmd in command.commands]

    async def get_subcommands(self, command: GroupTypes) -> list[str]:
        if not isinstance(command, GroupTypes):
            return []
        return [await self.inspect(cmd) for cmd in command.commands]

    @staticmethod
    def get_params(command: AllCommandTypes) -> list[dict]:
        params = []
        if isinstance(command, discord.app_commands.Group): return params
        for param in command.clean_params.values():
            params.append({
                "name": param.name,
                "type": param.converter,
                "description": param.description or "No description provided"
            })
        return params

    async def inspect(self, command: AllCommandTypes, *, only_subcommand_names: bool = True) -> CommandInfo:
        if not isinstance(command, discord.app_commands.Group):
            perms = [await check() for check in command.checks if "commands_extra" in str(check)]
        else:
            perms = []
        outputdict = {}
        for dit in perms:
            for key, item in dit.items():
                if key in outputdict:
                    raise ValueError
                outputdict[key] = item
        permissions = [key for key, item in outputdict.items() if item]
        return CommandInfo(
            name=command.name,
            description=command.description or "No description provided.",
            full_name=(command.full_parent_name + " " + command.name) if getattr(command, "full_parent_name", None) else command.name,
            prefix=self.bot.command_prefix if isinstance(command, PrefixTypes) else "/",
            aliases=getattr(command, "aliases", []),
            subcommands=self.get_subcommand_names(command) if only_subcommand_names else self.get_subcommands(command),
            category=self.get_category(command),
            params=self.get_params(command),
            permissions=[perm.replace("_", " ").title() for perm in permissions],

            cog=getattr(command, "cog_name", None),
            module=command.module,

            guild_only=command.guild_only if isinstance(command, (SlashTypes)) else ("guild_only" in str(command.checks)),
            hidden=self.get_category(command).startswith("_") or ("is_owner" in str(getattr(command, "checks", [])))
        )
