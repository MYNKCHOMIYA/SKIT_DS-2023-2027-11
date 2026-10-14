"""Sprint 2: Profile related models — education, experience, achievements

Revision ID: 0002_sprint2_profile_models
Revises: 0001_sprint1_initial
Create Date: 2026-10-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_sprint2_profile_models"
down_revision = "0001_sprint1_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── education ─────────────────────────────────────────────────────────────
    op.create_table(
        "education",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("faculty_id", sa.String(), nullable=False),
        sa.Column("degree", sa.String(), nullable=False),
        sa.Column("institution", sa.String(), nullable=False),
        sa.Column("field_of_study", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("grade", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── experience ────────────────────────────────────────────────────────────
    op.create_table(
        "experience",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("faculty_id", sa.String(), nullable=False),
        sa.Column("job_title", sa.String(), nullable=False),
        sa.Column("organization", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("employment_type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── achievements ──────────────────────────────────────────────────────────
    op.create_table(
        "achievements",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("faculty_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("achievement_date", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("achievements")
    op.drop_table("experience")
    op.drop_table("education")
