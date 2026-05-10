"""Initial schema — all ecommerce_core tables.

Revision ID: 0001
Revises:
Create Date: 2026-05-10
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. No-FK tables first
    op.create_table('product_category',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('parent_id', sa.Integer, sa.ForeignKey('product_category.id'), nullable=True),
        sa.Column('active', sa.Boolean, default=True),
    )
    op.create_table('product_attribute',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('active', sa.Boolean, default=True),
    )
    op.create_table('partner',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, nullable=True, unique=True),
        sa.Column('phone', sa.String, nullable=True),
        sa.Column('company_name', sa.String, nullable=True),
        sa.Column('is_company', sa.Boolean, default=False),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table('pricelist',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('currency', sa.String, default='USD'),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table('coupon',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('code', sa.String, nullable=False, unique=True),
        sa.Column('discount_type', sa.String, nullable=False),
        sa.Column('discount_value', sa.Numeric(10, 4), nullable=False),
        sa.Column('min_order_amount', sa.Numeric(12, 2), default=0),
        sa.Column('usage_limit', sa.Integer, nullable=True),
        sa.Column('used_count', sa.Integer, default=0),
        sa.Column('expiry_date', sa.Date, nullable=True),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table('shipping_method',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('carrier', sa.String, nullable=True),
        sa.Column('price', sa.Numeric(10, 2), default=0),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    # 2. FK to product_attribute
    op.create_table('product_attribute_value',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('attribute_id', sa.Integer, sa.ForeignKey('product_attribute.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('active', sa.Boolean, default=True),
    )
    # 3. FK to product_category
    op.create_table('product_template',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('product_category.id'), nullable=True),
        sa.Column('list_price', sa.Numeric(12, 4), default=0),
        sa.Column('image_url', sa.String, nullable=True),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    # 4. FK to partner
    op.create_table('address',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('partner_id', sa.Integer, sa.ForeignKey('partner.id'), nullable=False),
        sa.Column('address_type', sa.String, nullable=False),
        sa.Column('street', sa.String, nullable=True),
        sa.Column('street2', sa.String, nullable=True),
        sa.Column('city', sa.String, nullable=True),
        sa.Column('state', sa.String, nullable=True),
        sa.Column('country', sa.String, nullable=True),
        sa.Column('zip_code', sa.String, nullable=True),
        sa.Column('is_default', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    # 5. FK to pricelist
    op.create_table('pricelist_item',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('pricelist_id', sa.Integer, sa.ForeignKey('pricelist.id'), nullable=False),
        sa.Column('applied_on', sa.String, nullable=False, default='all'),
        sa.Column('product_variant_id', sa.Integer, nullable=True),
        sa.Column('product_template_id', sa.Integer, nullable=True),
        sa.Column('category_id', sa.Integer, nullable=True),
        sa.Column('compute_price', sa.String, nullable=False, default='fixed'),
        sa.Column('fixed_price', sa.Numeric(12, 4), nullable=True),
        sa.Column('price_discount', sa.Numeric(5, 2), nullable=True),
        sa.Column('min_quantity', sa.Numeric(10, 4), default=0),
        sa.Column('priority', sa.Integer, default=0),
    )
    # 6. FK to product_template
    op.create_table('product_variant',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('template_id', sa.Integer, sa.ForeignKey('product_template.id'), nullable=False),
        sa.Column('sku', sa.String, nullable=True, unique=True),
        sa.Column('barcode', sa.String, nullable=True),
        sa.Column('default_price', sa.Numeric(12, 4), default=0),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    # 7. Association table
    op.create_table('product_variant_attribute_line',
        sa.Column('variant_id', sa.Integer, sa.ForeignKey('product_variant.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('attribute_value_id', sa.Integer, sa.ForeignKey('product_attribute_value.id', ondelete='CASCADE'), primary_key=True),
    )
    # 8. Cart (FK to partner, pricelist, coupon, shipping_method)
    op.create_table('cart',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('partner_id', sa.Integer, sa.ForeignKey('partner.id'), nullable=True),
        sa.Column('session_token', sa.String, nullable=False, unique=True),
        sa.Column('pricelist_id', sa.Integer, sa.ForeignKey('pricelist.id'), nullable=True),
        sa.Column('coupon_id', sa.Integer, sa.ForeignKey('coupon.id'), nullable=True),
        sa.Column('shipping_method_id', sa.Integer, sa.ForeignKey('shipping_method.id'), nullable=True),
        sa.Column('status', sa.String, nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    # 9. CartLine
    op.create_table('cart_line',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('cart_id', sa.Integer, sa.ForeignKey('cart.id'), nullable=False),
        sa.Column('variant_id', sa.Integer, sa.ForeignKey('product_variant.id'), nullable=False),
        sa.Column('qty', sa.Numeric(10, 4), default=1),
        sa.UniqueConstraint('cart_id', 'variant_id', name='uq_cart_line_cart_variant'),
    )
    # 10. SaleOrder
    op.create_table('sale_order',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('partner_id', sa.Integer, sa.ForeignKey('partner.id'), nullable=False),
        sa.Column('billing_address_id', sa.Integer, sa.ForeignKey('address.id'), nullable=False),
        sa.Column('shipping_address_id', sa.Integer, sa.ForeignKey('address.id'), nullable=False),
        sa.Column('shipping_method_id', sa.Integer, sa.ForeignKey('shipping_method.id'), nullable=True),
        sa.Column('coupon_id', sa.Integer, sa.ForeignKey('coupon.id'), nullable=True),
        sa.Column('state', sa.String, nullable=False, default='draft'),
        sa.Column('tracking_number', sa.String, nullable=True),
        sa.Column('coupon_discount', sa.Numeric(12, 2), default=0),
        sa.Column('shipping_amount', sa.Numeric(12, 2), default=0),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    # 11. SaleOrderLine
    op.create_table('sale_order_line',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_id', sa.Integer, sa.ForeignKey('sale_order.id'), nullable=False),
        sa.Column('variant_id', sa.Integer, sa.ForeignKey('product_variant.id'), nullable=False),
        sa.Column('qty', sa.Numeric(10, 4), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 4), nullable=False),
        sa.Column('discount_amount', sa.Numeric(12, 2), default=0),
        sa.Column('tax_rate', sa.Numeric(5, 4), default=0),
    )
    # 12. PaymentTransaction
    op.create_table('payment_transaction',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('order_id', sa.Integer, sa.ForeignKey('sale_order.id'), nullable=False),
        sa.Column('provider', sa.String, nullable=False),
        sa.Column('provider_ref', sa.String, nullable=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String, default='USD'),
        sa.Column('state', sa.String, nullable=False, default='draft'),
        sa.Column('refunded_amount', sa.Numeric(12, 2), default=0),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('payment_transaction')
    op.drop_table('sale_order_line')
    op.drop_table('sale_order')
    op.drop_table('cart_line')
    op.drop_table('cart')
    op.drop_table('product_variant_attribute_line')
    op.drop_table('product_variant')
    op.drop_table('pricelist_item')
    op.drop_table('address')
    op.drop_table('product_template')
    op.drop_table('product_attribute_value')
    op.drop_table('shipping_method')
    op.drop_table('coupon')
    op.drop_table('pricelist')
    op.drop_table('partner')
    op.drop_table('product_attribute')
    op.drop_table('product_category')
