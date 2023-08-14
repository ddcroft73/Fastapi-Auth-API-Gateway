"""adding four new fields

Revision ID: ddab35a9a132
Revises: 802b42150f57
Create Date: 2023-08-14 11:36:44.271891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddab35a9a132'
down_revision: Union[str, None] = '802b42150f57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("phone_number", sa.String(), unique=False, nullable=True))
    op.add_column("user", sa.Column("is_verified", sa.Boolean(), default=False))
    op.add_column("user", sa.Column("failed_attempts", sa.Integer(), default=0))
    op.add_column("user", sa.Column("account_locked", sa.Boolean(), default=False))



def downgrade() -> None:
    op.drop_column("user", "phone_number")
    op.drop_column("user", "is_verified")
    op.drop_column("user", "failed_attempts")
    op.drop_column("user", "account_locked")

