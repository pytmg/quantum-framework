import os
from Cogs.util import Debugger
from discord.ext import commands
from typing import Any


class CogHandler:
    @staticmethod
    async def LoadAllCogs(
        bot: commands.Bot,
        folder: str = "Cogs",
        exceptions: list[str] | None = None,
        ignore_no_setup: bool = False,
        silent: bool = True,
        noload: bool = False
    ) -> tuple[dict[str, dict[str, Any]], list, list, list, list]:
        """
        Hot-reloader for extensions in a folder.

        Parameters:
            bot (commands.Bot): The bot to load all extensions into
            folder (str): Folder to load extensions from, defaults to Cogs
            exceptions (list[str]): A list of files/folders to ignore.
            ignore_no_setup (bool): Whether to ignore the NoEntryPoint error or not
            silent (bool): Prevents printing every cog's status when (re/un)loaded. (default: True)
            noload (bool): Prevents (re/un)loading extensions (default: False)

        Returns:
            dict[str, dict[str, Any]], list, list, list, list:
                Cog info used for the Reporter,
                list of reloaded extensions,
                list of new extensions,
                list of removed extensions,
                extensions that had an error
        """

        exceptions = exceptions or []
        exceptions.extend(["__pycache__"])  # Python cache directories are never extensions.

        # c   = information about every extension found/handled, used by the Reporter
        # rl  = extensions that were already loaded and successfully reloaded
        # n   = extensions that were newly loaded
        # d   = extensions that existed previously but are no longer present
        # err = extensions that failed to load, reload, or unload
        # w   = extensions that failed their first load attempt and should be tried again
        #       after the initial scan has finished.
        c, rl, n, d, err, w = {}, [], [], [], [], []

        # Keep a reference to the extensions that existed before scanning.
        # This is important because newly loaded extensions are added to bot.extensions
        # while we're walking the folder.
        existing = bot.extensions
        found_modules = set()

        for root, folders, files in os.walk(folder):
            if os.path.samefile(root, folder):
                continue  # Don't scan the root folder itself for extensions.

            # Remove explicitly ignored directories before os.walk enters them.
            for exception in exceptions:
                if exception in folders:
                    folders.remove(exception)

            # Folders beginning with "!" are treated as manually disabled.
            for dr in folders[:]:
                if dr.startswith("!"):
                    folders.remove(dr)

            for f in files:
                # Private/hidden Python files aren't treated as extensions.
                if (
                    f.endswith(".py")
                    and f not in exceptions
                    and not f.startswith("_")
                    and not f.startswith(".")
                ):
                    cogPath = os.path.join(root, f)
                    relPath = os.path.relpath(cogPath, folder)

                    # Convert the filesystem path into a Python module path.
                    modName = os.path.splitext(relPath)[0].replace(os.sep, ".")

                    # Add the folder name back so the result can be passed to
                    # discord.py's extension management methods.
                    extName = os.path.join(folder, modName).replace(os.sep, ".")
                    found_modules.add(extName)

                    try:
                        if extName in existing:
                            TYP = "reload"  # The extension is already loaded.
                            await bot.reload_extension(extName) if not noload else 0
                            rl.append(extName)
                        else:
                            try:
                                TYP = "load"  # The extension has never been loaded.
                                await bot.load_extension(extName) if not noload else 0
                                n.append(extName)
                            except:
                                # Some extensions may depend on another extension
                                # that hasn't been loaded yet. Save them for a second
                                # attempt after the entire directory has been scanned.
                                w.append(extName)
                                continue

                        if not silent:
                            Debugger.print(
                                f"[ext.loaded] Extension {extName} {TYP}ed successfully."
                            )

                        c[extName] = {
                            "type": TYP,
                            "success": True
                        }

                    except Exception as e:
                        err.append([extName, e])
                        c[extName] = {
                            "type": TYP,
                            "success": False,
                            "err": e
                        }

                        if not silent:
                            Debugger.print(
                                f"[ext.error] Extension {extName} could not be "
                                f"{TYP}ed | {e.__class__.__name__}: {e}"
                            )

        # Anything that was loaded before the scan but wasn't found this time
        # has either been deleted or explicitly excluded, so unload it.
        for ext in existing:
            if (ext not in found_modules) or (ext in exceptions):
                try:
                    await bot.unload_extension(ext)
                    d.append(ext)

                    c[ext] = {
                        "type": "remove",
                        "success": True
                    }

                    if not silent:
                        Debugger.print(
                            f"[ext.loaded] Extension {ext} removed successfully."
                        )

                except Exception as e:
                    err.append([ext, e])

                    c[ext] = {
                        "type": "remove",
                        "success": False,
                        "err": e
                    }

                    if not silent:
                        Debugger.print(
                            f"[ext.error] Extension {ext} could not be removed | "
                            f"{e.__class__.__name__}: {e}"
                        )

        # Retry extensions that failed during the first pass.
        # This allows dependencies to be loaded before the extensions that need them.
        for ext in w[:]:
            try:
                await bot.load_extension(ext) if not noload else 0
                n.append(ext)
                w.remove(ext)

                c[ext] = {
                    "type": "load",
                    "success": True
                }

                if not silent:
                    Debugger.print(
                        f"[ext.loaded] Extension {ext} loaded successfully."
                    )

            except Exception as e:
                w.remove(ext)
                err.append([ext, e])

                c[ext] = {
                    "type": "load",
                    "success": False,
                    "err": e
                }

                if not silent:
                    Debugger.print(
                        f"[ext.error] Extension {ext} could not be loaded | "
                        f"{e.__class__.__name__}: {e}"
                    )

        # A Python file without setup() isn't necessarily broken in this project.
        # When requested, hide discord.py's NoEntryPointError from the report.
        if ignore_no_setup:
            for er in err[:]:
                if isinstance(er[1], commands.errors.NoEntryPointError):
                    err.remove(er)

            for key, value in list(c.items()):
                if isinstance(value.get("err"), commands.errors.NoEntryPointError):
                    value.pop("err")

        return c, rl, n, d, err


async def setup(bot: commands.Bot):
    bot.cog_handler = CogHandler


async def teardown(bot: commands.Bot):
    bot.cog_handler = None