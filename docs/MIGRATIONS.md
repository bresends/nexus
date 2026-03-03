# Database Migrations

Migrations are managed with [Alembic](https://alembic.sqlalchemy.org/) and require the `DATABASE_URL` environment variable to be set.

## Common Commands

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Create a new migration from model changes
uv run alembic revision --autogenerate -m "description of change"

# Create an empty migration (for manual SQL)
uv run alembic revision -m "description of change"

# Rollback the last migration
uv run alembic downgrade -1

# Show current migration state
uv run alembic current

# Show migration history
uv run alembic history
```

## NixOS

On NixOS, Python must come from nixpkgs — `uv` cannot download its own CPython binary because it's dynamically linked against glibc. The devShell in `flake.nix` provides `pkgs.python312` and sets `UV_PYTHON_PREFERENCE=only-system` to enforce this.

If you see errors about dynamically linked executables, make sure you're inside the devShell (`nix develop`) and that no stale uv-managed Python remains:

```bash
rm -rf ~/.local/share/uv/python
nix develop
```
