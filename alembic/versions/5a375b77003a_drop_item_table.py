"""drop item table

Revision ID: 5a375b77003a
Revises: c97ce60d6c85
Create Date: 2023-08-05 23:12:11.968331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a375b77003a'
down_revision = 'c97ce60d6c85'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(op.f("ix_item_title"), table_name="item")
    op.drop_index(op.f("ix_item_id"), table_name="item")
    op.drop_index(op.f("ix_item_description"), table_name="item")
    op.drop_table("item")

def downgrade() -> None:
    op.create_table(
        "item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_item_description"), "item", ["description"], unique=False)
    op.create_index(op.f("ix_item_id"), "item", ["id"], unique=False)
    op.create_index(op.f("ix_item_title"), "item", ["title"], unique=False)

