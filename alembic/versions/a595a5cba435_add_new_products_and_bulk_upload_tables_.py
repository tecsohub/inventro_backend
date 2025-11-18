"""add new products and bulk upload tables only

Revision ID: a595a5cba435
Revises: c7ab8dbfd9a3
Create Date: 2025-09-29 02:32:10.207812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a595a5cba435'
down_revision: Union[str, None] = 'c7ab8dbfd9a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new_products table
    op.create_table('new_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('product_type', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('serial_number', sa.String(), nullable=True),
        sa.Column('batch_number', sa.String(), nullable=True),
        sa.Column('lot_number', sa.String(), nullable=True),
        sa.Column('expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('condition', sa.String(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('payment_status', sa.String(), nullable=True),
        sa.Column('receiver', sa.String(), nullable=True),
        sa.Column('receiver_contact', sa.String(), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.UniqueConstraint('product_id')
    )
    op.create_index(op.f('ix_new_products_id'), 'new_products', ['id'], unique=False)
    op.create_index(op.f('ix_new_products_product_id'), 'new_products', ['product_id'], unique=True)

    # Add bulk_uploads table
    op.create_table('bulk_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('upload_status', sa.String(), nullable=True, default='processing'),
        sa.Column('total_records', sa.Integer(), nullable=True, default=0),
        sa.Column('successful_records', sa.Integer(), nullable=True, default=0),
        sa.Column('failed_records', sa.Integer(), nullable=True, default=0),
        sa.Column('skipped_records', sa.Integer(), nullable=True, default=0),
        sa.Column('updated_records', sa.Integer(), nullable=True, default=0),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('duplicate_action', sa.String(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['managers.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], )
    )
    op.create_index(op.f('ix_bulk_uploads_id'), 'bulk_uploads', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_bulk_uploads_id'), table_name='bulk_uploads')
    op.drop_table('bulk_uploads')
    op.drop_index(op.f('ix_new_products_product_id'), table_name='new_products')
    op.drop_index(op.f('ix_new_products_id'), table_name='new_products')
    op.drop_table('new_products')
