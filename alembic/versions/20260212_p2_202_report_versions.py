"""P2-202 report version snapshot model

Revision ID: 20260212_p2_202
Revises: 20260212_p2_201
Create Date: 2026-02-12
"""

revision = "20260212_p2_202"
down_revision = "20260212_p2_201"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Example intended SQL (not executed in scaffold):
    # CREATE TABLE report_versions (
    #   version_id VARCHAR(32) PRIMARY KEY,
    #   report_id VARCHAR(32) NOT NULL,
    #   version_no INTEGER NOT NULL,
    #   spec_json JSONB NOT NULL,
    #   created_at TIMESTAMP NOT NULL
    # );
    # CREATE UNIQUE INDEX uq_report_versions_report_id_version_no
    #   ON report_versions(report_id, version_no);
    # CREATE UNIQUE INDEX uq_report_versions_version_id
    #   ON report_versions(version_id);
    pass


def downgrade() -> None:
    # Reverse of upgrade in real DB-backed deployments.
    pass
