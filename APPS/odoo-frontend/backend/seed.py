"""Seed script — populate demo data for Odoo Frontend.

Run from the backend directory:
    python seed.py

Idempotent: skips if any User rows already exist.
"""
from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Add backend dir to sys.path so local modules resolve
sys.path.insert(0, os.path.dirname(__file__))

from db import engine, SessionLocal
from auth_utils import hash_password

# Import all models so their tables are known to SQLAlchemy metadata
from models.concrete import (  # noqa: F401
    User,
    UserProfile,
    Membership,
    ActivityEvent,
)
import wms_core.models  # noqa: F401
import ecommerce_core.models  # noqa: F401

from wms_core.models.warehouse import Warehouse
from wms_core.models.location import Location, LocationType
from wms_core.models.product import Product, TrackingType
from wms_core.models.picking_type import PickingType, OperationType
from wms_core.models.picking import Picking, PickingState
from wms_core.models.move import Move, MoveState

from ecommerce_core.models.product import ProductTemplate, ProductVariant
from ecommerce_core.models.partner import Partner, Address, AddressType
from ecommerce_core.models.order import SaleOrder, SaleOrderLine, OrderState
from ecommerce_core.models.coupon import Coupon, DiscountType

from user_core.enums import MembershipTier


def seed():
    db = SessionLocal()
    try:
        # ------------------------------------------------------------------ #
        # Idempotency guard
        # ------------------------------------------------------------------ #
        if db.query(User).count() > 0:
            print("Database already seeded, skipping.")
            return

        now = datetime.now(timezone.utc)

        # ------------------------------------------------------------------ #
        # 1. WMS — Warehouse & Locations
        # ------------------------------------------------------------------ #
        # Create parent view location first (warehouse needs lot_stock_id later)
        parent_loc = Location(name="WH", location_type=LocationType.view)
        db.add(parent_loc)
        db.flush()  # get id

        stock_loc = Location(name="Stock", location_type=LocationType.internal, parent_id=parent_loc.id)
        input_loc = Location(name="Input", location_type=LocationType.internal, parent_id=parent_loc.id)
        output_loc = Location(name="Output", location_type=LocationType.internal, parent_id=parent_loc.id)
        db.add_all([stock_loc, input_loc, output_loc])
        db.flush()

        warehouse = Warehouse(
            name="Main Warehouse",
            lot_stock_id=stock_loc.id,
            wh_input_stock_loc_id=input_loc.id,
            wh_output_stock_loc_id=output_loc.id,
            reception_steps="one_step",
            delivery_steps="one_step",
        )
        db.add(warehouse)
        db.flush()

        # ------------------------------------------------------------------ #
        # 2. WMS — Products
        # ------------------------------------------------------------------ #
        wms_products = [
            Product(name="Widget A", tracking=TrackingType.none, uom="unit", sale_price=10.0, cost_price=5.0),
            Product(name="Widget B", tracking=TrackingType.none, uom="unit", sale_price=20.0, cost_price=8.0),
            Product(name="Gadget (Lot)", tracking=TrackingType.lot, uom="unit", sale_price=50.0, cost_price=25.0),
            Product(name="Sensor (Serial)", tracking=TrackingType.serial, uom="unit", sale_price=100.0, cost_price=60.0),
            Product(name="Cable", tracking=TrackingType.none, uom="m", sale_price=5.0, cost_price=2.0),
        ]
        db.add_all(wms_products)
        db.flush()

        # ------------------------------------------------------------------ #
        # 3. WMS — Picking Types
        # ------------------------------------------------------------------ #
        receipt_type = PickingType(
            name="Receipts",
            operation_type=OperationType.incoming,
            warehouse_id=warehouse.id,
            default_location_src_id=input_loc.id,
            default_location_dest_id=stock_loc.id,
            sequence_prefix="WH/IN/",
        )
        delivery_type = PickingType(
            name="Delivery Orders",
            operation_type=OperationType.outgoing,
            warehouse_id=warehouse.id,
            default_location_src_id=stock_loc.id,
            default_location_dest_id=output_loc.id,
            sequence_prefix="WH/OUT/",
        )
        internal_type = PickingType(
            name="Internal Transfers",
            operation_type=OperationType.internal,
            warehouse_id=warehouse.id,
            default_location_src_id=stock_loc.id,
            default_location_dest_id=stock_loc.id,
            sequence_prefix="WH/INT/",
        )
        db.add_all([receipt_type, delivery_type, internal_type])
        db.flush()

        # ------------------------------------------------------------------ #
        # 4. WMS — Pickings & Moves
        # ------------------------------------------------------------------ #
        picking_draft = Picking(
            name="WH/IN/00001",
            state=PickingState.draft,
            picking_type_id=receipt_type.id,
            location_src_id=input_loc.id,
            location_dest_id=stock_loc.id,
            scheduled_date=now + timedelta(days=1),
        )
        db.add(picking_draft)
        db.flush()

        move1 = Move(
            picking_id=picking_draft.id,
            product_id=wms_products[0].id,
            location_src_id=input_loc.id,
            location_dest_id=stock_loc.id,
            product_qty=Decimal("10"),
            state=MoveState.draft,
        )
        move2 = Move(
            picking_id=picking_draft.id,
            product_id=wms_products[1].id,
            location_src_id=input_loc.id,
            location_dest_id=stock_loc.id,
            product_qty=Decimal("5"),
            state=MoveState.draft,
        )
        db.add_all([move1, move2])

        picking_done = Picking(
            name="WH/OUT/00001",
            state=PickingState.done,
            picking_type_id=delivery_type.id,
            location_src_id=stock_loc.id,
            location_dest_id=output_loc.id,
            scheduled_date=now - timedelta(days=1),
        )
        db.add(picking_done)
        db.flush()

        move3 = Move(
            picking_id=picking_done.id,
            product_id=wms_products[0].id,
            location_src_id=stock_loc.id,
            location_dest_id=output_loc.id,
            product_qty=Decimal("3"),
            qty_done=Decimal("3"),
            state=MoveState.done,
        )
        db.add(move3)
        db.flush()

        # ------------------------------------------------------------------ #
        # 5. Users
        # ------------------------------------------------------------------ #
        admin = User(
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            is_active=True,
            is_verified=True,
            is_superuser=True,
            last_login_at=now,
        )
        alice = User(
            email="alice@example.com",
            password_hash=hash_password("password"),
            is_active=True,
            is_verified=True,
            is_superuser=False,
            last_login_at=now - timedelta(days=2),
        )
        bob = User(
            email="bob@example.com",
            password_hash=hash_password("password"),
            is_active=True,
            is_verified=False,
            is_superuser=False,
            last_login_at=None,
        )
        db.add_all([admin, alice, bob])
        db.flush()

        # ------------------------------------------------------------------ #
        # 6. UserProfiles
        # ------------------------------------------------------------------ #
        admin_profile = UserProfile(
            user_id=admin.id,
            display_name="Administrator",
            bio="System administrator account.",
            phone="+1-555-0100",
            timezone="America/New_York",
            locale="en",
        )
        alice_profile = UserProfile(
            user_id=alice.id,
            display_name="Alice Smith",
            bio="Pro tier customer.",
            phone="+1-555-0101",
            timezone="UTC",
            locale="en",
        )
        bob_profile = UserProfile(
            user_id=bob.id,
            display_name="Bob Jones",
            bio="Free tier user.",
            phone=None,
            timezone="UTC",
            locale="en",
        )
        db.add_all([admin_profile, alice_profile, bob_profile])
        db.flush()

        # ------------------------------------------------------------------ #
        # 7. Memberships
        # ------------------------------------------------------------------ #
        admin_membership = Membership(
            user_id=admin.id,
            tier=MembershipTier.vip,
            started_at=now - timedelta(days=365),
            expires_at=now + timedelta(days=365),
        )
        alice_membership = Membership(
            user_id=alice.id,
            tier=MembershipTier.pro,
            started_at=now - timedelta(days=30),
            expires_at=now + timedelta(days=335),
        )
        bob_membership = Membership(
            user_id=bob.id,
            tier=MembershipTier.free,
            started_at=now - timedelta(days=7),
            expires_at=None,  # non-expiring free tier
        )
        db.add_all([admin_membership, alice_membership, bob_membership])
        db.flush()

        # ------------------------------------------------------------------ #
        # 8. Ecommerce — Product Templates & Variants
        # ------------------------------------------------------------------ #
        ec_templates = [
            ProductTemplate(name="Laptop Pro", list_price=Decimal("999.99"), description="High-end laptop"),
            ProductTemplate(name="Wireless Mouse", list_price=Decimal("29.99"), description="Ergonomic mouse"),
            ProductTemplate(name="USB-C Hub", list_price=Decimal("49.99"), description="7-port USB-C hub"),
            ProductTemplate(name="Monitor 27\"", list_price=Decimal("349.99"), description="4K monitor"),
            ProductTemplate(name="Mechanical Keyboard", list_price=Decimal("89.99"), description="RGB keyboard"),
        ]
        db.add_all(ec_templates)
        db.flush()

        # Add variants for first two templates
        variants = [
            ProductVariant(template_id=ec_templates[0].id, sku="LAPTOP-001", default_price=Decimal("999.99")),
            ProductVariant(template_id=ec_templates[0].id, sku="LAPTOP-002", default_price=Decimal("1199.99")),
            ProductVariant(template_id=ec_templates[1].id, sku="MOUSE-001", default_price=Decimal("29.99")),
            ProductVariant(template_id=ec_templates[2].id, sku="HUB-001", default_price=Decimal("49.99")),
            ProductVariant(template_id=ec_templates[3].id, sku="MON-001", default_price=Decimal("349.99")),
        ]
        db.add_all(variants)
        db.flush()

        # ------------------------------------------------------------------ #
        # 9. Ecommerce — Partner & Addresses
        # ------------------------------------------------------------------ #
        partner = Partner(
            name="Acme Corp",
            email="orders@acme.com",
            phone="+1-555-9000",
            company_name="Acme Corporation",
            is_company=True,
        )
        db.add(partner)
        db.flush()

        billing_addr = Address(
            partner_id=partner.id,
            address_type=AddressType.billing,
            street="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            zip_code="62701",
            is_default=True,
        )
        shipping_addr = Address(
            partner_id=partner.id,
            address_type=AddressType.shipping,
            street="456 Warehouse Blvd",
            city="Springfield",
            state="IL",
            country="US",
            zip_code="62702",
            is_default=True,
        )
        db.add_all([billing_addr, shipping_addr])
        db.flush()

        # ------------------------------------------------------------------ #
        # 10. Ecommerce — Sale Orders with Lines
        # ------------------------------------------------------------------ #
        order1 = SaleOrder(
            partner_id=partner.id,
            billing_address_id=billing_addr.id,
            shipping_address_id=shipping_addr.id,
            state=OrderState.confirmed,
            coupon_discount=Decimal("0"),
            shipping_amount=Decimal("10.00"),
        )
        db.add(order1)
        db.flush()

        line1a = SaleOrderLine(
            order_id=order1.id,
            variant_id=variants[0].id,
            qty=Decimal("1"),
            unit_price=Decimal("999.99"),
            discount_amount=Decimal("0"),
            tax_rate=Decimal("0.08"),
        )
        line1b = SaleOrderLine(
            order_id=order1.id,
            variant_id=variants[2].id,
            qty=Decimal("2"),
            unit_price=Decimal("29.99"),
            discount_amount=Decimal("0"),
            tax_rate=Decimal("0.08"),
        )
        db.add_all([line1a, line1b])

        order2 = SaleOrder(
            partner_id=partner.id,
            billing_address_id=billing_addr.id,
            shipping_address_id=shipping_addr.id,
            state=OrderState.draft,
            coupon_discount=Decimal("0"),
            shipping_amount=Decimal("5.00"),
        )
        db.add(order2)
        db.flush()

        line2a = SaleOrderLine(
            order_id=order2.id,
            variant_id=variants[3].id,
            qty=Decimal("1"),
            unit_price=Decimal("49.99"),
            discount_amount=Decimal("5.00"),
            tax_rate=Decimal("0.08"),
        )
        line2b = SaleOrderLine(
            order_id=order2.id,
            variant_id=variants[4].id,
            qty=Decimal("1"),
            unit_price=Decimal("349.99"),
            discount_amount=Decimal("0"),
            tax_rate=Decimal("0.08"),
        )
        db.add_all([line2a, line2b])
        db.flush()

        # ------------------------------------------------------------------ #
        # 11. Ecommerce — Coupons
        # ------------------------------------------------------------------ #
        coupons = [
            Coupon(
                code="SAVE10",
                discount_type=DiscountType.percentage,
                discount_value=Decimal("10"),
                min_order_amount=Decimal("50.00"),
                usage_limit=100,
                used_count=5,
            ),
            Coupon(
                code="FLAT20",
                discount_type=DiscountType.fixed,
                discount_value=Decimal("20.00"),
                min_order_amount=Decimal("100.00"),
                usage_limit=50,
                used_count=10,
            ),
            Coupon(
                code="FREESHIP",
                discount_type=DiscountType.fixed,
                discount_value=Decimal("10.00"),
                min_order_amount=Decimal("0"),
                usage_limit=None,  # unlimited
                used_count=0,
            ),
        ]
        db.add_all(coupons)
        db.flush()

        # ------------------------------------------------------------------ #
        # 12. ActivityEvents for admin
        # ------------------------------------------------------------------ #
        event_types = [
            "user.login",
            "order.viewed",
            "product.searched",
            "profile.updated",
            "report.exported",
        ]
        for i, event_type in enumerate(event_types):
            event = ActivityEvent(
                user_id=admin.id,
                event_type=event_type,
                ip_address="127.0.0.1",
                user_agent="Mozilla/5.0",
                metadata_={"detail": f"seed event {i+1}"},
            )
            db.add(event)

        db.commit()
        print("Seed complete!")
        print(f"  Users:         {db.query(User).count()}")
        print(f"  Warehouses:    {db.query(Warehouse).count()}")
        print(f"  Locations:     {db.query(Location).count()}")
        print(f"  WMS Products:  {db.query(Product).count()}")
        print(f"  EC Templates:  {db.query(ProductTemplate).count()}")
        print(f"  Sale Orders:   {db.query(SaleOrder).count()}")
        print(f"  Coupons:       {db.query(Coupon).count()}")
        print(f"  Activity:      {db.query(ActivityEvent).count()}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
