"""P2-002 render progress columns

Revision ID: 20260212_p2_002
Revises:
Create Date: 2026-02-12
"""

# This migration is a placeholder for environments that wire Alembic + SQLAlchemy models.
# In this scaffold repository, runtime storage is in-memory.

revision = "20260212_p2_002"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Example intended SQL (not executed in scaffold):
    # ALTER TABLE render_jobs ADD COLUMN progress INTEGER NOT NULL DEFAULT 0;
    # ALTER TABLE render_jobs ADD COLUMN stage VARCHAR(32) NOT NULL DEFAULT 'queued';
    pass


def downgrade() -> None:
    # Reverse of upgrade in real DB-backed deployments.
    pass
