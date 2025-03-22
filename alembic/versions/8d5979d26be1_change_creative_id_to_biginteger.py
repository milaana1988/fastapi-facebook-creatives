"""Change creative_id to BigInteger

Revision ID: 8d5979d26be1
Revises: 
Create Date: 2025-03-21 18:18:10.958819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d5979d26be1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the index that depends on creative_id
    op.drop_index('ix_creatives_creative_id', table_name='creatives')

    # Alter creative_id from Integer to BigInteger
    op.alter_column(
        'creatives',
        'creative_id',
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=True
    )

    # Re-create the index on creative_id
    op.create_index('ix_creatives_creative_id', 'creatives',
                    ['creative_id'], unique=True)


def downgrade() -> None:
    # Drop the index on creative_id
    op.drop_index('ix_creatives_creative_id', table_name='creatives')

    # Revert creative_id from BigInteger back to Integer
    op.alter_column(
        'creatives',
        'creative_id',
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=True
    )

    # Re-create the index on creative_id
    op.create_index('ix_creatives_creative_id', 'creatives',
                    ['creative_id'], unique=True)
