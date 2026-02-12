"""P2-401 ACL policy model

Revision ID: 20260212_p2_401
Revises: 20260212_p2_301
Create Date: 2026-02-12
"""

revision = "20260212_p2_401"
down_revision = "20260212_p2_301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Example intended SQL (not executed in scaffold):
    # CREATE TABLE acl_policies (
    #   resource_type VARCHAR(64) NOT NULL,
    #   resource_id VARCHAR(64) NOT NULL,
    #   principal_type VARCHAR(32) NOT NULL,
    #   principal_id VARCHAR(64) NOT NULL,
    #   actions_json JSONB NOT NULL,
    #   PRIMARY KEY (resource_type, resource_id, principal_type, principal_id)
    # );
    # CREATE INDEX ix_acl_policies_resource
    #   ON acl_policies(resource_type, resource_id);
    pass


def downgrade() -> None:
    # Reverse of upgrade in real DB-backed deployments.
    pass
