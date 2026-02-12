"""P2-201 template model and versioning

Revision ID: 20260212_p2_201
Revises: 20260212_p2_003
Create Date: 2026-02-12
"""

revision = "20260212_p2_201"
down_revision = "20260212_p2_003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Example intended SQL (not executed in scaffold):
    # CREATE TABLE templates (
    #   template_id VARCHAR(32) PRIMARY KEY,
    #   name VARCHAR(255) NOT NULL,
    #   description TEXT NULL,
    #   status VARCHAR(32) NOT NULL DEFAULT 'active',
    #   latest_version INTEGER NOT NULL DEFAULT 1,
    #   created_at TIMESTAMP NOT NULL,
    #   updated_at TIMESTAMP NOT NULL
    # );
    #
    # CREATE TABLE template_versions (
    #   template_id VARCHAR(32) NOT NULL,
    #   version INTEGER NOT NULL,
    #   spec_json JSONB NOT NULL,
    #   changelog TEXT NULL,
    #   created_at TIMESTAMP NOT NULL,
    #   PRIMARY KEY (template_id, version),
    #   FOREIGN KEY (template_id) REFERENCES templates(template_id)
    # );
    #
    # CREATE INDEX ix_template_versions_template_id_version
    #   ON template_versions(template_id, version DESC);
    pass


def downgrade() -> None:
    # Reverse of upgrade in real DB-backed deployments.
    pass
