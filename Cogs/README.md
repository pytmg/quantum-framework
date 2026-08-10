# quantum-framework Cogs

All files in the root of `Cogs/` will be ignored by the [CogHandler](#coghandler) in `_core`. These files can be used for shared data, functions or debugging utilities.

Example structure:

```
Cogs/
- util.py
- _beta/
  - betafeature.py
- _core/
  - coghandler.py
- _tests/
  - testfeature1.py
- Moderation
  - moderationfeature.py
- Fun
  - funfeature1.py
  - funfeature2.py
```

## CogHandler

The CogHandler is in `_core`.

It handles the loading, reloading and unloading of extensions in `Cogs/`.

Ignores dotfiles.

## Special Directories

Directories that begin with `_` do not show up in Help for regular users. The only people that can see commands in these folders are the owners of your Discord bot.

These can be used for framework internals, developer tools, beta features, testing or other non-public features.

For example:
- `_core/` - Core framework functionality
- `_dev/` - Developer tooling
- `_tests/` - Testing features
- `_beta/` - Unfinished/In development features.

## Extensions

Python files inside `Cogs/` subdirectories are discovered by CogHandler and treated as extensions.

For example:

```
Cogs/
- Fun
  - funfeature.py
```

becomes the extension `Cogs.Fun.funfeature`.

See the `examples/` folder for examples of extensions that you can use or take inspiration from for your bot.