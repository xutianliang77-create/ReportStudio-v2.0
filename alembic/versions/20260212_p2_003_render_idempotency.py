"""P2-003 render idempotency columns + unique index

Revision ID: 20260212_p2_003
Revises: 20260212_p2_002
Create Date: 2026-02-12
"""

revision = "20260212_p2_003"
down_revision = "20260212_p2_002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Example intended SQL (not executed in scaffold):
    # ALTER TABLE render_jobs ADD COLUMN workspace_id VARCHAR(64) NOT NULL DEFAULT 'default-workspace';
    # ALTER TABLE render_jobs ADD COLUMN report_id VARCHAR(64) NOT NULL DEFAULT 'default-report';
    # ALTER TABLE render_jobs ADD COLUMN render_request_id VARCHAR(128) NULL;
    # CREATE UNIQUE INDEX uq_render_jobs_idempotency
    #   ON render_jobs(workspace_id, report_id, render_request_id)
    #   WHERE render_request_id IS NOT NULL;
    pass


def downgrade() -> None:
    # Reverse of upgrade in real DB-backed deployments.
    pass
