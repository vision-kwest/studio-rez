# Package standards

Studio Rez packages must be predictable, immutable, and easy to promote between stages.

## Naming

Package names use lowercase letters, numbers, and underscores only:

```python
name = "usd_tools"
```

Avoid hyphens in package names. Rez requirements still use a hyphen between package name and version, for example `usd-26.05`.

## Versions

Use numeric dotted versions such as:

- `1.0.0`
- `2.3.1`
- `26.05`
- `1.0.0-beta.1`

OpenUSD-style versions such as `26.05` are valid.

## Required fields

Every package must define:

```python
name = "my_package"
version = "1.0.0"


def commands():
    pass
```

## Commands

Use Rez's shell-agnostic rex API instead of shell-specific syntax:

```python
def commands():
    env.PATH.prepend("{root}/bin")
    env.PYTHONPATH.prepend("{root}/python")
```

## Immutability

Do not modify an installed package version in place. Build a new version or rebuild in `dev`, then promote a validated immutable directory to `test` and `prod`.
