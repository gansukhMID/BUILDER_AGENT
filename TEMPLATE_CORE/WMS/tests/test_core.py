from decimal import Decimal
import pytest
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin
from wms_core.models import (
    Location, LocationType, Product, TrackingType,
    Lot, Quant, Picking, PickingState, Move, MoveState,
)
from wms_core.utils.state_machine import transition


def test_mixins_import():
    assert hasattr(TimestampMixin, "created_at")
    assert hasattr(TimestampMixin, "updated_at")
    assert hasattr(ActiveMixin, "active")
    assert hasattr(NameMixin, "name")
    assert hasattr(NameMixin, "code")


def test_mixins_via_model(session):
    loc = Location(name="TestBin", location_type=LocationType.internal)
    session.add(loc)
    session.flush()
    assert loc.created_at is not None
    assert loc.updated_at is not None
    assert loc.active is True
    assert loc.name == "TestBin"
    assert loc.code is None


def test_no_circular_imports():
    from wms_core.models import (
        Warehouse, Location, Product, Lot, Quant,
        PickingType, Picking, Move, StockRule, Package,
    )
    assert Warehouse.__tablename__ == "warehouse"


def test_location_complete_name(session):
    root = Location(name="WH", location_type=LocationType.view)
    stock = Location(name="Stock", location_type=LocationType.internal)
    shelf = Location(name="Shelf-A", location_type=LocationType.internal)

    session.add_all([root, stock, shelf])
    session.flush()

    stock.parent_id = root.id
    shelf.parent_id = stock.id
    session.flush()

    # Reload to populate relationship
    session.expire_all()
    shelf_reloaded = session.get(Location, shelf.id)
    assert shelf_reloaded.complete_name == "WH/Stock/Shelf-A"


def test_location_is_ancestor_of(session):
    parent = Location(name="Zone-A", location_type=LocationType.view)
    child = Location(name="Bin-01", location_type=LocationType.internal)

    session.add_all([parent, child])
    session.flush()

    child.parent_id = parent.id
    session.flush()
    session.expire_all()

    parent_r = session.get(Location, parent.id)
    child_r = session.get(Location, child.id)

    assert parent_r.is_ancestor_of(child_r) is True
    assert child_r.is_ancestor_of(parent_r) is False


def test_quant_add_and_get_available(session):
    product = Product(name="Widget", uom="unit", tracking=TrackingType.none)
    supplier_loc = Location(name="Supplier", location_type=LocationType.supplier)
    stock_loc = Location(name="Stock", location_type=LocationType.internal)

    session.add_all([product, supplier_loc, stock_loc])
    session.flush()

    # Receipt: add 10 units to stock
    Quant.add_quantity(session, product.id, stock_loc.id, Decimal("10"))
    session.flush()

    available = Quant.get_available(session, product.id, stock_loc.id)
    assert available == Decimal("10")


def test_quant_round_trip(session):
    product = Product(name="Box", uom="unit", tracking=TrackingType.none)
    stock_loc = Location(name="Stock-B", location_type=LocationType.internal)
    customer_loc = Location(name="Customer", location_type=LocationType.customer)

    session.add_all([product, stock_loc, customer_loc])
    session.flush()

    # Receipt: +5 into stock
    Quant.add_quantity(session, product.id, stock_loc.id, Decimal("5"))
    # Delivery: -5 out of stock
    Quant.add_quantity(session, product.id, stock_loc.id, Decimal("-5"))
    session.flush()

    available = Quant.get_available(session, product.id, stock_loc.id)
    assert available == Decimal("0")


def test_picking_state_machine_valid(session):
    product = Product(name="Part", uom="unit")
    src = Location(name="Src", location_type=LocationType.internal)
    dest = Location(name="Dest", location_type=LocationType.internal)
    session.add_all([product, src, dest])
    session.flush()

    picking = Picking(name="WH/OUT/001", location_src_id=src.id, location_dest_id=dest.id)
    session.add(picking)
    session.flush()

    assert picking.state == PickingState.draft
    picking.confirm()
    assert picking.state == PickingState.confirmed

    # Manually advance to in_progress before validate
    picking.state = PickingState(transition(picking.state.value, "in_progress"))
    picking.validate()
    assert picking.state == PickingState.done


def test_picking_state_machine_invalid():
    picking = Picking(name="WH/IN/001")
    picking.state = PickingState.done
    with pytest.raises(ValueError):
        picking.cancel()


def test_move_links_to_picking(session):
    product = Product(name="SKU-X", uom="each")
    src = Location(name="SrcM", location_type=LocationType.internal)
    dest = Location(name="DestM", location_type=LocationType.internal)
    session.add_all([product, src, dest])
    session.flush()

    picking = Picking(name="WH/MOVE/001")
    session.add(picking)
    session.flush()

    move = Move(
        picking_id=picking.id,
        product_id=product.id,
        location_src_id=src.id,
        location_dest_id=dest.id,
        product_qty=Decimal("3"),
    )
    session.add(move)
    session.flush()

    session.expire_all()
    picking_r = session.get(Picking, picking.id)
    assert len(picking_r.moves) == 1
    assert picking_r.moves[0].product_qty == Decimal("3")
