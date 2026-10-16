"""Sprint 3: Google OAuth support — auth_provider, google_id, nullable password

Revision ID: 0003_sprint3_google_oauth
Revises: 0002_sprint2_profile_models
Create Date: 2026-10-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_sprint3_google_oauth"
down_revision = "0002_sprint2_profile_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users: add auth_provider and google_id, alter hashed_password nullable ─
    op.add_column(
        "users",
        sa.Column("auth_provider", sa.String(), server_default="local", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("google_id", sa.String(), nullable=True),
    )
    op.create_index(op.f("ix_users_google_id"), "users", ["google_id"], unique=True)
    op.alter_column("users", "hashed_password", nullable=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_google_id"), table_name="users")
    op.drop_column("users", "google_id")
    op.drop_column("users", "auth_provider")
    op.alter_column("users", "hashed_password", nullable=False)
