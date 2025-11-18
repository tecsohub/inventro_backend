"""add company_id to products table

Revision ID: 032e1fddb1f0
Revises: cb70ab024301
Create Date: 2025-09-29 03:02:15.468571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '032e1fddb1f0'
down_revision: Union[str, None] = 'cb70ab024301'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add company_id column to the old products table
    conn = op.get_bind()

    # Add company_id as nullable first
    op.add_column('products', sa.Column('company_id', sa.String(length=10), nullable=True))

    # Populate company_id based on manager_id relationship
    # For each product, find the manager's company_id and use it
    try:
        conn.execute(sa.text("""
            UPDATE products
            SET company_id = (
                SELECT m.company_id
                FROM managers m
                WHERE m.id = products.manager_id
            )
            WHERE company_id IS NULL
        """))
        print("Updated products with company_id based on manager relationships")
    except Exception as e:
        print(f"Warning during product migration: {e}")
        # If the update fails, set all products to the default company
        conn.execute(sa.text(
            "UPDATE products SET company_id = 'DEFAULT01' WHERE company_id IS NULL"
        ))
        print("Set default company_id for all products")

    # Create foreign key constraint
    try:
        op.create_foreign_key('fk_product_company', 'products', 'companies', ['company_id'], ['id'])
        print("Created foreign key constraint for products")
    except Exception as e:
        print(f"Foreign key constraint for products already exists or couldn't be created: {e}")


def downgrade() -> None:
    """Downgrade schema."""
    try:
        op.drop_constraint('fk_product_company', 'products', type_='foreignkey')
    except:
        pass  # FK might not exist if creation failed
    op.drop_column('products', 'company_id')
