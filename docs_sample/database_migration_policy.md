# PostgreSQL Database Migration & Zero-Downtime Policy

## Zero-Downtime Rules
1. **Never drop columns in a single release**: Follow the Expand-Contract pattern over 2 separate deployments.
2. **Nullable New Columns**: New columns added to existing production tables MUST be nullable or have a non-locking DEFAULT value.
3. **Index Creation**: Always use `CREATE INDEX CONCURRENTLY` for adding indexes on large tables in production.

## Alembic Migration Guidelines
- Migration scripts must be committed under `backend/alembic/versions/`.
- Test both `upgrade()` and `downgrade()` functions locally before pushing PR.
- Lock timeout should be set to `2s` prior to executing DDL operations to prevent blocking incoming user transactions.
