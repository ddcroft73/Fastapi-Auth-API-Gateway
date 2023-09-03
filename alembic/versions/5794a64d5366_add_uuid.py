"""add uuid

Revision ID: 5794a64d5366
Revises: ddab35a9a132
Create Date: 2023-09-02 18:31:13.298808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5794a64d5366'
down_revision: Union[str, None] = 'ddab35a9a132'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is because I have to delete all current data to add the Unique Identifier.
    # if there is no data in the DB comment out. This is for Development use. THis DB was
    # built overtime with trial and error as to the tables and fields. it has been... stressful but educational
   op.execute('TRUNCATE "user"')
   op.add_column('user',
                 sa.Column('user_uuid',
                           postgresql.UUID(as_uuid=True),
                           nullable=True)
                 )
   
def downgrade() -> None:
    op.drop_column('user', 'user_uuid')
