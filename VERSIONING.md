# Quantum Framework Versioning

Current: V0.9.0 - Initial QF release, and I'm sure I can name at least one feature that was added to QF since the initial commit.

## Version Numbers

Quantum Framework (QF) follows a `MAJOR.MINOR.PATCH` (`X.Y.Z`) versioning scheme, with a few QF-specific conventions.

### Patch Releases `(x.y.Z)`

Bug fixes, stability improvements, and minor corrections.

These releases shouldn't introduce any API changes. Existing APIs and their expected behaviour should remain as documented.

### Minor Releases `(x.Y.0)`

Significant improvements, new functionality, and API changes that maintain backwards compatibility.

If an API is replaced, the old API will remain functional, with deprecation warnings pointing developers towards the new API.

Deprecated APIs will remain available throughout the current major version.

### Major Releases `(X.0.0)`

Big fat updates.

Major releases will generally introduce a flagship feature, substantial architectural improvements, or even both.

Major releases also serve as cleanup points for the framework.

**APIs deprecated during the previous major version *will* be removed in the next stable major release.**

This is for the sole reason of preventing QF's codebase from getting too crowded with deprecated features/APIs.

Not every major release necessarily breaks existing code, but backwards compatibility between major releases is not guaranteed.

## Development Stages

- `-indev` - Internal development, in development- something. This will not be seen publicly on GitHub. Features are still in development, and are prone to instability, breaking or potentially keeping your bot from functioning.
- `-beta`/`-nodoc` - Public beta.
- No suffix - Stable release.

The difference between `-beta` and `-nodoc` isn't when in development they're released, they're both **Public Beta**.

The suffix simply indicates clearly whether documentation for that release is available.

- `-beta` - API documentation is available.
- `-nodoc` - API documentation is either incomplete, or outright nonexistent.

Both have the same stability expectations, if you know what spaghetti you're reading.

## Deprecation

Major betas may still contain APIs that are deprecated during the previous major version.

Usage of these APIs will result in continuous warnings, directing developers to the replacement API while also indicating that deprecated APIs will be removed in the stable release.

For example:

`[qf.feature.a.deprecated] THIS IS A DEPRECATED FEATURE OF QF, PLEASE USE THE NEW API AT qf.feature.b`

**Do not rely on deprecated APIs remaining available in the stable release.**

---

Next up: V1.0.0-nodoc (eta. sometime soon, after GTA6)