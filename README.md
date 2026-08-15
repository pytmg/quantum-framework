# quantum-framework

This project is open-source boilerplate for helping people make Discord bots with a very developer-friendly architecture.

## Framework Features

* **Modular cog architecture** - organize bot features into independent extensions.
* **Hot-reloading** - load, unload, and reload cogs without restarting the bot.
* **Automatic cog discovery** - find and manage extensions from your project structure.
* **Centralized error handling** - handle errors globally while allowing individual cogs to handle their own errors.
* **Developer tooling** - built-in commands and utilities for managing and debugging the bot during development.
* **Debugging & reporting** - structured output for extension loading, reloading, failures, and other runtime events.
* **Command introspection** - inspect the bot's command structure and export command information for external tools.
* **Recovery tools** - keep core functionality available even when extensions fail to load.
* **discord.py-based** - built on top of `discord.py`, rather than replacing it.

## Philosophy

Quantum is designed around the idea that developing a Discord bot shouldn't require rebuilding the same infrastructure for every project.

The framework provides the architecture and developer tooling, while your bot's cogs provide the actual functionality.

Quantum Framework is tested against Quantum V2's feature set and edge-cases. Once proven stable, all architectural changes will be moved to this open-source repository.

## How to set up Quantum Framework for your bot

> [!IMPORTANT]
> The code in this repository uses syntax from Python 3.10+

### 1. Clone the repository

Clone the Quantum Framework repository into the directory where you want to build your bot.

```sh
git clone https://github.com/pytmg/quantum-framework my-bot
cd my-bot
```

### 2. Create a virtual environment

Quantum Framework should be run inside a Python virtual environment.

```sh
python -m venv .venv
```

Activate the virtual environment:

**Windows:**

```sh
.venv\Scripts\activate
```

**Linux/macOS:**

```sh
source .venv/bin/activate
```

Once activated, install the required dependencies:

```sh
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory of your bot.

```env
TOKEN=your_bot_token_here
```

Add any other environment variables required by your bot here as well.

> [!WARNING]
> **Do <ins>NOT</ins> commit your `.env` file to Git.**

A `.gitignore` should include at least:

```gitignore
.venv/
.env
__pycache__/
```

### 4. Configure your bot

Your bot's entry point is `__main__.py`.

Add your bot configuration there and place your bot's functionality inside the `Cogs/` directory.

A typical project structure will look like:

```text
my-bot/
- .venv/
- Cogs/
  - Fun/
  - Moderation/
  - Utility/
  - _core/
- .env
- .gitignore
- __main__.py
- requirements.txt
- report.py
```

### 5. Run the bot

With the virtual environment activated:

```sh
python .
```

The bot should start, load its extensions, and connect to Discord.

### Running on Linux

A simple shell script can be used to start the bot:

```sh
#!/bin/sh

. .venv/bin/activate
python .
```

Save this as `start.sh`, then make it executable:

```sh
chmod +x start.sh
```

Run it with:

```sh
./start.sh
```

This is useful for development or simple deployments. For production deployments, using a process manager such as `systemd`, Docker, or another service supervisor is recommended.

### Development workflow

Quantum Framework is designed to minimize the need to restart the bot during development.

When changing a cog, use Quantum's extension management tools to reload the affected cog instead of restarting the entire process.

This allows you to develop individual features while keeping the rest of the bot running.

For changes to the framework's core functionality that cannot be hot-reloaded, restart the bot normally, or by using `!dev restart`.

## Status

Quantum Framework is currently under active development, and most releases are stable.

The architecture is tested and extracted from Quantum V2 when changes are made.