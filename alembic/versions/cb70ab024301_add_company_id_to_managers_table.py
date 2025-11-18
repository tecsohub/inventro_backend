"""add company_id to managers table

Revision ID: cb70ab024301
Revises: a595a5cba435
Create Date: 2025-09-29 02:54:17.542615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb70ab024301'
down_revision: Union[str, None] = 'a595a5cba435'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The company_id column already exists from a previous migration attempt
    # We just need to populate it with data
    conn = op.get_bind()

    # Check if there are any managers without company_id
    result = conn.execute(sa.text("SELECT COUNT(*) FROM managers WHERE company_id IS NULL"))
    null_company_count = result.scalar()

    if null_company_count > 0:
        # Check if companies table has any records
        try:
            result = conn.execute(sa.text("SELECT COUNT(*) FROM companies"))
            company_count = result.scalar()

            if company_count == 0:
                # Create a default company for existing managers
                conn.execute(sa.text(
                    "INSERT INTO companies (id, name, size, created_at) VALUES "
                    "('DEFAULT01', 'Default Company', 1, datetime('now'))"
                ))
                print("Created default company for existing managers")

            # Update all existing managers to use the first available company
            conn.execute(sa.text(
                "UPDATE managers SET company_id = ("
                "  SELECT id FROM companies LIMIT 1"
                ") WHERE company_id IS NULL"
            ))

            print(f"Updated {null_company_count} managers with company_id")

        except Exception as e:
            print(f"Warning during migration: {e}")
            # If there's an error with companies table, create companies first
            try:
                conn.execute(sa.text(
                    "INSERT INTO companies (id, name, size, created_at) VALUES "
                    "('LEGACY01', 'Legacy Company', 1, datetime('now'))"
                ))
                conn.execute(sa.text(
                    "UPDATE managers SET company_id = 'LEGACY01' WHERE company_id IS NULL"
                ))
                print("Created legacy company and updated managers")
            except Exception as e2:
                print(f"Error creating legacy company: {e2}")
                # If all else fails, just set a default company_id
                conn.execute(sa.text(
                    "UPDATE managers SET company_id = 'DEFAULT01' WHERE company_id IS NULL"
                ))
                print("Set default company_id for managers")
    else:
        print("All managers already have company_id values")

    # Create foreign key constraint if it doesn't exist
    try:
        op.create_foreign_key('fk_manager_company', 'managers', 'companies', ['company_id'], ['id'])
        print("Created foreign key constraint")
    except Exception as e:
        print(f"Foreign key constraint already exists or couldn't be created: {e}")


def downgrade() -> None:
    """Downgrade schema."""
    try:
        op.drop_constraint('fk_manager_company', 'managers', type_='foreignkey')
    except:
        pass  # FK might not exist if creation failed
    op.drop_column('managers', 'company_id')
