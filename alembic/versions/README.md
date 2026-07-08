# alembic/versions/

This directory contains all database migration scripts for LeadForge AI.

## File naming convention

Files are generated with the pattern:
```
YYYYMMDD_HHMM_<rev>_<slug>.py
```

For example:
```
20240115_1430_a3f9c2d1_create_leads_table.py
```

This ensures migrations sort chronologically in any file explorer.

## Workflow

```bash
# Generate a new migration after changing a model
alembic revision --autogenerate -m "describe_what_changed"

# Apply all pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# View current migration state
alembic current

# View full migration history
alembic history --verbose

# Preview SQL without applying (offline mode)
alembic upgrade head --sql
```

## Rules

1. **Always review** generated migration files before committing — autogenerate is not perfect.
2. **Never edit** applied migrations. Create a new one to correct a mistake.
3. **Every migration must have a `downgrade()`** function that completely reverses the `upgrade()`.
4. **Import new models** in `app/models/__init__.py` before running autogenerate, or Alembic won't see the table.
