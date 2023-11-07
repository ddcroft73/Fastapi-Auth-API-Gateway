"""Add login logout fields

Revision ID: 72a971be7b93
Revises: 61bdb349a06e
Create Date: 2023-11-06 17:17:26.211403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72a971be7b93'
down_revision: Union[str, None] = '61bdb349a06e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('is_loggedin', sa.Boolean(), nullable=True))
    op.add_column('account', sa.Column('last_logout_date', sa.DateTime(timezone=True), nullable=True))



def downgrade() -> None:
    pass