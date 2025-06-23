"""alphanumeric_company_id

Revision ID: c7ab8dbfd9a3
Revises: 4037fde38c13
Create Date: 2025-06-24 01:55:47.072533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7ab8dbfd9a3'
down_revision: Union[str, None] = '4037fde38c13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraints
    op.drop_constraint('managers_company_id_fkey', 'managers', type_='foreignkey')
    op.drop_constraint('products_company_id_fkey', 'products', type_='foreignkey')

    # Alter columns
    op.alter_column('companies', 'id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=10),
               existing_nullable=False)
    op.alter_column('managers', 'company_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=10),
               existing_nullable=False)
    op.alter_column('products', 'company_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=10),
               existing_nullable=False)

    # Re-create foreign key constraints
    op.create_foreign_key(
        'managers_company_id_fkey', 'managers', 'companies', ['company_id'], ['id']
    )
    op.create_foreign_key(
        'products_company_id_fkey', 'products', 'companies', ['company_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraints
    op.drop_constraint('managers_company_id_fkey', 'managers', type_='foreignkey')
    op.drop_constraint('products_company_id_fkey', 'products', type_='foreignkey')

    # Alter columns back to INTEGER
    op.alter_column('products', 'company_id',
               existing_type=sa.String(length=10),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('managers', 'company_id',
               existing_type=sa.String(length=10),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('companies', 'id',
               existing_type=sa.String(length=10),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # Re-create foreign key constraints
    op.create_foreign_key(
        'managers_company_id_fkey', 'managers', 'companies', ['company_id'], ['id']
    )
    op.create_foreign_key(
        'products_company_id_fkey', 'products', 'companies', ['company_id'], ['id']
    )
