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
    # 1. stock_warehouse (location FKs deferred — added after stock_location is created)
    op.create_table(
        "stock_warehouse",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column("lot_stock_id", sa.Integer, nullable=True),
        sa.Column("wh_input_stock_loc_id", sa.Integer, nullable=True),
        sa.Column("wh_output_stock_loc_id", sa.Integer, nullable=True),
        sa.Column("reception_steps", sa.String, nullable=False, server_default="one_step"),
        sa.Column("delivery_steps", sa.String, nullable=False, server_default="one_step"),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 2. product_product
    op.create_table(
        "product_product",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column(
            "tracking",
            sa.Enum("none", "lot", "serial", name="tracking_type"),
            server_default="none",
        ),
        sa.Column("uom", sa.String, nullable=False, server_default="unit"),
        sa.Column("can_be_sold", sa.Boolean, server_default=sa.true()),
        sa.Column("can_be_purchased", sa.Boolean, server_default=sa.true()),
        sa.Column("sale_price", sa.Float, nullable=True),
        sa.Column("cost_price", sa.Float, nullable=True),
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

    # Back-fill deferred FKs on stock_warehouse → stock_location
    op.create_foreign_key(
        "fk_warehouse_lot_stock", "stock_warehouse", "stock_location", ["lot_stock_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_warehouse_input_loc", "stock_warehouse", "stock_location", ["wh_input_stock_loc_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_warehouse_output_loc", "stock_warehouse", "stock_location", ["wh_output_stock_loc_id"], ["id"]
    )

    # 4. stock_lot
    op.create_table(
        "stock_lot",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("product_product.id"), nullable=False),
        sa.Column("ref", sa.String, nullable=True),
        sa.Column("expiration_date", sa.DateTime, nullable=True),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("name", "product_id", name="uq_lot_name_product"),
    )

    # 5. stock_picking_type
    op.create_table(
        "stock_picking_type",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=True),
        sa.Column(
            "operation_type",
            sa.Enum("incoming", "outgoing", "internal", name="operation_type"),
            nullable=False,
        ),
        sa.Column("warehouse_id", sa.Integer, sa.ForeignKey("stock_warehouse.id"), nullable=True),
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
        sa.Column("sequence_prefix", sa.String, nullable=True),
        sa.Column("count_picking_ready", sa.Integer, server_default="0"),
        sa.Column("active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 6. quant
    op.create_table(
        "stock_quant",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("product_product.id"), nullable=False),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("stock_location.id"), nullable=False),
        sa.Column("lot_id", sa.Integer, sa.ForeignKey("stock_lot.id"), nullable=True),
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
            sa.ForeignKey("stock_picking_type.id"),
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
        sa.Column("product_id", sa.Integer, sa.ForeignKey("product_product.id"), nullable=False),
        sa.Column("lot_id", sa.Integer, sa.ForeignKey("stock_lot.id"), nullable=True),
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
            sa.ForeignKey("stock_picking_type.id"),
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
    op.drop_table("stock_quant")
    op.drop_table("stock_picking_type")
    op.drop_table("stock_lot")
    op.drop_constraint("fk_warehouse_output_loc", "stock_warehouse", type_="foreignkey")
    op.drop_constraint("fk_warehouse_input_loc", "stock_warehouse", type_="foreignkey")
    op.drop_constraint("fk_warehouse_lot_stock", "stock_warehouse", type_="foreignkey")
    op.drop_table("stock_location")
    op.drop_table("product_product")
    op.drop_table("stock_warehouse")
