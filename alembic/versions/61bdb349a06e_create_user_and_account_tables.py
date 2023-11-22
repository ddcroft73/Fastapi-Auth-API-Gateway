"""create user and account tables

Revision ID: 61bdb349a06e
Revises: 
Create Date: 2023-09-14 18:55:54.491012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '61bdb349a06e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_uuid', postgresql.UUID( as_uuid=True), unique=True, nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True, default=False),
        sa.Column("phone_number", sa.String(), unique=False, nullable=True),
        sa.Column("is_verified", sa.Boolean(), default=False),
        sa.Column("cell_provider", sa.String(), unique=False, nullable=True),

        # New additions:
        # is_deleted   - important incase you need to revive the account, etc.
        # deleted_date - The date of the deletion, for record keeping. WIll also record this in the logs
        # user_notes   - May come in handy to keep tabs on certain users.
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_full_name"), "user", ["full_name"], unique=False)
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=True)  # Should be unique
    op.create_index(op.f("ix_phone_number"), "user", ["phone_number"], unique=False)

    op.create_table(
        "account",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        # delete the account associated with the user, when a user is deleted.
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete='CASCADE'), nullable=True),

        sa.Column("hashed_admin_PIN", sa.String(), nullable=True),
        sa.Column("creation_date", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        # change "subscription_type" to app_tier

        sa.Column("subscription_type", sa.String(), default='free', nullable=True),
        sa.Column("last_login_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bill_renew_date", sa.DateTime( timezone=True), nullable=True),
        sa.Column("auto_bill_renewal", sa.Boolean, default=False),

        sa.Column("cancellation_date", sa.DateTime( timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.String(), nullable=True),

        sa.Column("last_update_date",  sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column("preferred_contact_method", sa.String(), default='email', nullable=True),
        sa.Column("account_locked", sa.Boolean(), default=False),
        sa.Column("account_locked_reason", sa.String(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=True),
        # Values for 2FA
        sa.Column("use_2FA", sa.Boolean(), default=False),
        sa.Column("contact_method_2FA", sa.String(), nullable=True),
        sa.Column("cell_provider_2FA", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("account")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_full_name"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_index(op.f("ix_phone_number"), table_name="user")
    op.drop_table("user")

    