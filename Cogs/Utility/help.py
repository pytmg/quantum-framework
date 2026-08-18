import discord
from discord import ui
from discord.ext import commands
from Cogs.util import CommandInfo, CommandRegistry, Debugger, Paginator

class PageBtn(ui.Button):
    def __init__(self, categories: list[str], goal: int, View: "HelpView"):
        super().__init__()

        # Keep the view's state so the button knows what it is navigating.
        self.goal = goal
        self.paginator = View.paginator
        self.user = View.user
        self.category = View.category
        self.cmdreg = View.cmdreg
        self.prefix = View.prefix
        self.bot = View.bot
        self.page = self.paginator._page
        self.categories = categories

        # The paginator stores the available pages, so use its current
        # page to determine where this button should take the user.
        BOOK = self.paginator.pages

        # goal:
        # 0 = first page
        # 1 = previous page
        # 2 = next page
        # 3 = last page
        # 4 = refresh/current page
        self.targetpage = [0, self.page - 1, self.page + 1, len(BOOK) - 1, self.page][self.goal]

        if goal in [0, 1]:
            self.disabled = self.page == 0
            self.label = "⬅️" if goal == 0 else "◀️"
        elif goal in [2, 3]:
            self.disabled = self.page == len(BOOK) - 1
            self.label = "➡️" if goal == 3 else "▶️"
        elif goal == 4:
            self.disabled = False
            self.label = "🔁"
        else:
            raise ValueError("goal not in [0, 1, 2, 3, 4]")

    async def callback(self, interaction: discord.Interaction) -> None:
        # Help menus are tied to the user who opened them.
        # Prevent other users from controlling somebody else's menu.
        if interaction.user != self.user:
            await interaction.response.send_message("no", ephemeral=True)
            return

        paginator = self.paginator

        await interaction.response.edit_message(
            embed=BuildEmbed(paginator, self.targetpage, self.category, self.prefix),
            view=await HelpView(
                interaction.user,
                self.categories,
                self.bot,
                self.prefix,
                cmdreg=self.cmdreg,
                paginator=paginator,
                category=self.category
            ).populate()
        )

class CategorySelector(ui.Select):
    def __init__(self):
        super().__init__()
        self.set_up = False
        self.placeholder = "Please select a help category"

    async def update(self, View: "HelpView"):
        # Copy the current help menu state into the selector.
        self.paginator = View.paginator
        self.categories = View.categories
        self.user = View.user
        self.category = View.category
        self.cmdreg = View.cmdreg
        self.prefix = View.prefix
        self.bot = View.bot

        # Private categories (those beginning with "_") are only shown
        # to the bot owner.
        self.options = [
            discord.SelectOption(label=category)
            for category in self.categories
            if (not category.startswith("_") or await self.bot.is_owner(self.user))
        ]

        self.set_up = True
        self.placeholder = self.category or self.placeholder
        return self

    async def callback(self, interaction: discord.Interaction):
        # Only the user who opened the help menu can interact with it.
        if interaction.user != self.user:
            await interaction.response.send_message("no", ephemeral=True)
            return

        # Refresh the category data in case commands/categories changed
        # since the help menu was originally opened.
        allcats = await self.cmdreg.get_all_categories(with_command_info=True)
        categorynames = [key for key in list(allcats.keys())]

        # Reuse the existing paginator rather than creating a new one.
        # Changing the category replaces the paginator's data and resets
        # it back to the first page.
        paginator = self.paginator
        paginator.data = allcats[self.values[0]]
        paginator.page(0)

        prefix = self.prefix

        await interaction.response.edit_message(
            embed=BuildEmbed(paginator, 0, self.values[0], prefix),
            view=await HelpView(
                interaction.user,
                categorynames,
                self.bot,
                self.prefix,
                cmdreg=self.cmdreg,
                paginator=paginator,
                category=self.values[0]
            ).populate()
        )

class HelpView(ui.View):
    def __init__(
        self,
        user: discord.User | discord.Member,
        categories: list[str],
        bot: commands.Bot,
        prefix: str,
        *,
        cmdreg: CommandRegistry,
        paginator: Paginator,
        category: str = None
    ):
        super().__init__()

        # The view has no timeout because the help message is intended
        # to remain usable until the message itself is removed.
        self.timeout = None

        # Store everything required to rebuild the view after an interaction.
        self.user = user
        self.categories = categories
        self.bot = bot
        self.cmdreg = cmdreg
        self.paginator = paginator
        self.prefix = prefix
        self.category = category

    async def populate(self):
        # Only show pagination controls when there is actually more than
        # one page of commands to navigate.
        if len(self.paginator.pages) > 1:
            for i in range(4):
                self.add_item(PageBtn(self.categories, i, self))

        # The category selector is always available.
        self.add_item(
            await CategorySelector().update(self)
        )

        return self

def BuildEmbed(
    paginator: Paginator,
    page: int,
    categoryname: str,
    prefix: str
) -> discord.Embed:
    embed = discord.Embed()

    # No category means this is the initial help screen.
    if not categoryname:
        embed.title = ":question: Help"
        embed.description = (
            f"Use the dropdown below to browse commands by category.\n\n"
            f"Use `{prefix}help (command)` to get extra information about a command."
        )
        embed.color = 0x82ffb2
        return embed

    embed.title = f":question: Help : {categoryname}"
    embed.description = f"Commands in category {categoryname}"
    embed.color = 0x82ffb2

    # Paginator.page() returns only the commands belonging to the
    # requested page, keeping the embed from becoming too large.
    pageitems: list[CommandInfo] = paginator.page(page)

    for item in pageitems:
        embed.add_field(
            name=item.name,
            value=item.description
        )

    return embed

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cmdreg = CommandRegistry(bot)

    @commands.hybrid_command(name="help", description="Get help with Quantum")
    async def help(
        self,
        ctx: commands.Context | discord.Interaction,
        *,
        command: str = ""
    ):
        """
        Parameters
        ----------
        command: str
            Get information about a specific command
        """

        # Get every command category, including the command metadata
        # needed to build the help pages.
        allcats = await self.cmdreg.get_all_categories(with_command_info=True)
        categorynames = [key for key in list(allcats.keys())]

        # 15 commands per help page. Increase/decrease this if your bot's
        # command descriptions make the embeds too large or too sparse.
        paginator = Paginator([], 15)

        # Hybrid commands can be invoked through either a prefix or slash.
        prefix = "/" if ctx.interaction else self.bot.command_prefix

        # If a command was supplied, try to show information about that
        # command instead of opening the category browser.
        cmd = self.bot.get_command(command) or self.bot.tree.get_command(command)

        if cmd:
            # Convert the discord.py command into the normalized command
            # information used by Quantum's command registry.
            cmd = await self.cmdreg.inspect(cmd, only_subcommand_names=True)

            # Hidden commands are only exposed to the bot owner.
            if cmd.hidden and not await self.bot.is_owner(ctx.author):
                cmd = None

            if cmd:
                embed = discord.Embed(
                    title=":question: Help",
                    description=f"Information about command: {cmd.name}",
                    color=0x82ffb2
                )

                embed.add_field(
                    name="Name & Description",
                    value=f"`{cmd.full_name}`: {cmd.description}",
                    inline=False
                )

                embed.add_field(
                    name="Category",
                    value=cmd.category,
                    inline=False
                )

                embed.add_field(
                    name="Parameters",
                    value="\n".join(
                        f"{param['name']}: {param['type'].__name__} - {param['description']}"
                        for param in cmd.params
                    ) or "None"
                )

                if len(cmd.aliases) > 0:
                    embed.add_field(
                        name="Aliases",
                        value="*" + "*, *".join(cmd.aliases + [cmd.name]) + "*",
                        inline=False
                    )

                if len(cmd.subcommands) > 0:
                    embed.add_field(
                        name="Subcommands",
                        value="*" + "*, *".join(cmd.subcommands) + "*",
                        inline=False
                    )

                embed.add_field(
                    name="Server Command?",
                    value="Yes" if cmd.guild_only else "No",
                    inline=False
                )

                embed.add_field(
                    name="Permissions Required",
                    value=", ".join(cmd.permissions) if len(cmd.permissions) != 0 else "None",
                    inline=False
                )

                await ctx.reply(embed=embed)
                return

        # No specific command was requested (or the command was not found),
        # so show the category-based help browser instead.
        await ctx.reply(
            embed=BuildEmbed(paginator, 0, None, prefix),
            view=await HelpView(
                ctx.author,
                categorynames,
                self.bot,
                prefix,
                cmdreg=self.cmdreg,
                paginator=paginator
            ).populate()
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
