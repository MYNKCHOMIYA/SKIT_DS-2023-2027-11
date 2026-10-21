"""Sprint 2 & 3: Academic and Research modules
Publications, Projects, Patents, Certifications, Teaching, Student Guidance, Workshops, Activity Logs, Notifications

Revision ID: 0004_sprint2_academic_modules
Revises: 0003_sprint3_google_oauth
Create Date: 2026-10-21 20:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_sprint2_academic_modules"
down_revision = "0003_sprint3_google_oauth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── publications ──────────────────────────────────────────────────────────
    op.create_table(
        "publications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("faculty_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("publication_type", sa.String(), nullable=False),
        sa.Column("publisher", sa.String(), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=False),
        sa.Column("doi", sa.String(), nullable=True),
        sa.Column("citations", sa.Integer(), default=0),
        sa.Column("authors", sa.String(), nullable=True),
        sa.Column("journal", sa.String(), nullable=True),
        sa.Column("issn", sa.String(), nullable=True),
        sa.Column("indexed_in", sa.String(), nullable=True),
        sa.Column("pdf_url", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── projects ──────────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("faculty_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("funding_agency", sa.String(), nullable=True),
        sa.Column("budget", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("status", sa.String(), default="Ongoing", nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("team_members", sa.String(), nullable=True),
        sa.Column("project_documents_url", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── patents ───────────────────────────────────────────────────────────────
    op.create_table(
        "patents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("faculty_profile_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("patent_number", sa.String(), nullable=False),
        sa.Column("filing_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), default="FILED", nullable=False),
        sa.Column("inventors", sa.Text(), nullable=False),
        sa.Column("link_url", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_profile_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_patents_patent_number"), "patents", ["patent_number"], unique=True)
    op.create_index(op.f("ix_patents_id"), "patents", ["id"], unique=False)

    # ── certifications ────────────────────────────────────────────────────────
    op.create_table(
        "certifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("faculty_profile_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("organization", sa.String(), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("certificate_url", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_profile_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_certifications_id"), "certifications", ["id"], unique=False)

    # ── teaching ──────────────────────────────────────────────────────────────
    op.create_table(
        "teaching",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("faculty_profile_id", sa.String(), nullable=False),
        sa.Column("course_name", sa.String(), nullable=False),
        sa.Column("subject_code", sa.String(), nullable=False),
        sa.Column("semester", sa.String(), nullable=False),
        sa.Column("academic_year", sa.String(), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["faculty_profile_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teaching_id"), "teaching", ["id"], unique=False)

    # ── student_guidance ──────────────────────────────────────────────────────
    op.create_table(
        "student_guidance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("faculty_profile_id", sa.String(), nullable=False),
        sa.Column("student_name", sa.String(), nullable=False),
        sa.Column("project_title", sa.String(), nullable=False),
        sa.Column("degree", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), default="ONGOING", nullable=False),
        sa.ForeignKeyConstraint(["faculty_profile_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_guidance_id"), "student_guidance", ["id"], unique=False)

    # ── workshops ─────────────────────────────────────────────────────────────
    op.create_table(
        "workshops",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("faculty_profile_id", sa.String(), nullable=False),
        sa.Column("event_name", sa.String(), nullable=False),
        sa.Column("organizer", sa.String(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("certificate_url", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["faculty_profile_id"], ["faculty_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workshops_id"), "workshops", ["id"], unique=False)

    # ── activity_logs ─────────────────────────────────────────────────────────
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── notifications ─────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("is_read", sa.Boolean(), default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("activity_logs")
    op.drop_index(op.f("ix_workshops_id"), table_name="workshops")
    op.drop_table("workshops")
    op.drop_index(op.f("ix_student_guidance_id"), table_name="student_guidance")
    op.drop_table("student_guidance")
    op.drop_index(op.f("ix_teaching_id"), table_name="teaching")
    op.drop_table("teaching")
    op.drop_index(op.f("ix_certifications_id"), table_name="certifications")
    op.drop_table("certifications")
    op.drop_index(op.f("ix_patents_id"), table_name="patents")
    op.drop_index(op.f("ix_patents_patent_number"), table_name="patents")
    op.drop_table("patents")
    op.drop_table("projects")
    op.drop_table("publications")
