"""Initial schema — all WMS core tables.

Revision ID: 0001
Revises:
Create Date: 2026-05-08
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. warehouse (no FK deps yet)
    op.create_table(
        "warehouse",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column("short_name", sa.String, nullable=False),
        sa.Column("lot_stock_id", sa.Integer, nullable=True),  # FK added below
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 2. product
    op.create_table(
        "product",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column(
            "tracking",
            sa.Enum("none", "lot", "serial", name="tracking_type"),
            server_default="none",
        ),
        sa.Column("uom", sa.String, nullable=False, server_default="unit"),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 3. location (self-referential)
    op.create_table(
        "stock_location",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column(
            "location_type",
            sa.Enum(
                "internal", "view", "customer", "supplier",
                "transit", "inventory", "production",
                name="location_type",
            ),
            server_default="internal",
        ),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=True),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Back-fill the deferred FK on warehouse
    op.create_foreign_key(
        "fk_warehouse_lot_stock", "warehouse", "stock_location", ["lot_stock_id"], ["id"]
    )

    # 4. lot
    op.create_table(
        "lot",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("product.id"), nullable=False),
        sa.Column("ref", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 5. picking_type
    op.create_table(
        "picking_type",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column(
            "operation_type",
            sa.Enum("incoming", "outgoing", "internal", name="operation_type"),
            nullable=False,
        ),
        sa.Column("warehouse_id", sa.Integer, sa.ForeignKey("warehouse.id"), nullable=True),
        sa.Column(
            "default_location_src_id",
            sa.Integer,
            sa.ForeignKey("stock_location.id"),
            nullable=True,
        ),
        sa.Column(
            "default_location_dest_id",
            sa.Integer,
            sa.ForeignKey("stock_location.id"),
            nullable=True,
        ),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 6. quant
    op.create_table(
        "quant",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("product.id"), nullable=False),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=False),
        sa.Column("lot_id", sa.Integer, sa.ForeignKey("lot.id"), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 6), server_default="0"),
        sa.Column("reserved_quantity", sa.Numeric(18, 6), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("product_id", "location_id", "lot_id", name="uq_quant_key"),
    )

    # 7. picking
    op.create_table(
        "picking",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column(
            "state",
            sa.Enum(
                "draft", "confirmed", "in_progress", "done", "cancelled",
                name="picking_state",
            ),
            server_default="draft",
        ),
        sa.Column(
            "picking_type_id",
            sa.Integer,
            sa.ForeignKey("picking_type.id"),
            nullable=True,
        ),
        sa.Column(
            "location_src_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=True
        ),
        sa.Column(
            "location_dest_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=True
        ),
        sa.Column("scheduled_date", sa.DateTime, nullable=True),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 8. move
    op.create_table(
        "move",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("picking_id", sa.Integer, sa.ForeignKey("picking.id"), nullable=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("product.id"), nullable=False),
        sa.Column("lot_id", sa.Integer, sa.ForeignKey("lot.id"), nullable=True),
        sa.Column(
            "location_src_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=False
        ),
        sa.Column(
            "location_dest_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=False
        ),
        sa.Column("product_qty", sa.Numeric(18, 6), server_default="0"),
        sa.Column("qty_done", sa.Numeric(18, 6), server_default="0"),
        sa.Column(
            "state",
            sa.Enum(
                "draft", "confirmed", "assigned", "done", "cancelled",
                name="move_state",
            ),
            server_default="draft",
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 9. stock_rule
    op.create_table(
        "stock_rule",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column(
            "action",
            sa.Enum("pull", "push", "pull_push", name="rule_action"),
            nullable=False,
        ),
        sa.Column(
            "location_src_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=True
        ),
        sa.Column(
            "location_dest_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=False
        ),
        sa.Column(
            "picking_type_id",
            sa.Integer,
            sa.ForeignKey("picking_type.id"),
            nullable=True,
        ),
        sa.Column("delay", sa.Integer, server_default="0"),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 10. package
    op.create_table(
        "package",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column(
            "location_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("package")
    op.drop_table("stock_rule")
    op.drop_table("move")
    op.drop_table("picking")
    op.drop_table("quant")
    op.drop_table("picking_type")
    op.drop_table("lot")
    op.drop_constraint("fk_warehouse_lot_stock", "warehouse", type_="foreignkey")
    op.drop_table("stock_location")
    op.drop_table("product")
    op.drop_table("warehouse")
