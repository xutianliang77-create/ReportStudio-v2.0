"""P2-301 preview session model

Revision ID: 20260212_p2_301
Revises: 20260212_p2_202
Create Date: 2026-02-12
"""

revision = "20260212_p2_301"
down_revision = "20260212_p2_202"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Example intended SQL (not executed in scaffold):
    # CREATE TABLE preview_sessions (
    #   preview_session_id VARCHAR(32) PRIMARY KEY,
    #   report_id VARCHAR(32) NOT NULL,
    #   base_spec_version VARCHAR(32) NULL,
    #   working_spec_json JSONB NOT NULL,
    #   patch_history_json JSONB NOT NULL DEFAULT '[]',
    #   status VARCHAR(32) NOT NULL DEFAULT 'active',
    #   updated_at TIMESTAMP NOT NULL
    # );
    # CREATE INDEX ix_preview_sessions_report_id_updated_at
    #   ON preview_sessions(report_id, updated_at DESC);
    pass


def downgrade() -> None:
    # Reverse of upgrade in real DB-backed deployments.
    pass
