from decimal import Decimal
import pytest
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin
from wms_core.models import (
    Location, LocationType, Product, TrackingType,
    Lot, Quant, Picking, PickingState, Move, MoveState,
    StockRule, Package,
)
from wms_core.models.stock_rule import RuleAction, ProcureMethod, RuleAuto
from wms_core.utils.state_machine import transition, InvalidTransition
from wms_core.utils.hierarchy import build_full_path, get_all_children


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


def test_location_tablename():
    assert Location.__tablename__ == "stock_location"


def test_product_tablename_and_defaults(session):
    from wms_core.models import Product, TrackingType
    assert Product.__tablename__ == "product_product"
    p = Product(name="Widget", uom="unit")
    session.add(p)
    session.flush()
    assert p.tracking == TrackingType.none
    assert p.uom == "unit"
    assert p.can_be_sold is True
    assert p.can_be_purchased is True
    assert p.sale_price is None
    assert p.cost_price is None
    # no FK to location or warehouse
    assert not hasattr(p, "location_id")
    assert not hasattr(p, "warehouse_id")


def test_lot_tablename_fk_and_unique(session):
    from wms_core.models import Lot
    import sqlalchemy.exc
    assert Lot.__tablename__ == "stock_lot"
    product = Product(name="Part-A", uom="unit")
    session.add(product)
    session.flush()

    lot = Lot(name="LOT-001", product_id=product.id)
    session.add(lot)
    session.flush()
    assert lot.id is not None
    assert lot.product.name == "Part-A"   # relationship loads
    assert product.lots[0].name == "LOT-001"  # back_populates works

    # Duplicate (name, product_id) must raise
    session.add(Lot(name="LOT-001", product_id=product.id))
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        session.flush()
    session.rollback()


def test_warehouse_tablename_and_defaults(session):
    from wms_core.models import Warehouse
    assert Warehouse.__tablename__ == "stock_warehouse"
    src = Location(name="WH-Stock", location_type=LocationType.internal)
    session.add(src)
    session.flush()
    wh = Warehouse(name="Main Warehouse", lot_stock_id=src.id)
    session.add(wh)
    session.flush()
    assert wh.id is not None
    assert wh.reception_steps == "one_step"
    assert wh.delivery_steps == "one_step"
    assert wh.active is True
    assert wh.wh_input_stock_loc_id is None
    assert wh.wh_output_stock_loc_id is None


def test_no_circular_imports():
    from wms_core.models import (
        Warehouse, Location, Product, Lot, Quant,
        PickingType, Picking, Move, StockRule, Package,
    )
    assert Warehouse.__tablename__ == "stock_warehouse"


def test_picking_type_tablename_and_relationships(session):
    from wms_core.models import PickingType, OperationType
    assert PickingType.__tablename__ == "stock_picking_type"

    src = Location(name="Input", location_type=LocationType.internal)
    dest = Location(name="Stock", location_type=LocationType.internal)
    session.add_all([src, dest])
    session.flush()

    pt = PickingType(
        name="Receipts",
        operation_type=OperationType.incoming,
        default_location_src_id=src.id,
        default_location_dest_id=dest.id,
    )
    session.add(pt)
    session.flush()

    session.expire(pt)
    assert pt.warehouse_id is None          # nullable FK
    assert pt.count_picking_ready == 0
    assert pt.default_src_location.name == "Input"
    assert pt.default_dest_location.name == "Stock"
    assert pt.operation_type in (OperationType.incoming, "incoming")


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


def test_hierarchy_build_full_path(session):
    root = Location(name="WH", location_type=LocationType.view)
    child = Location(name="Stock", location_type=LocationType.internal)
    session.add_all([root, child])
    session.flush()
    child.parent_id = root.id
    session.flush()
    session.expire_all()
    child_r = session.get(Location, child.id)
    assert build_full_path(child_r) == "WH/Stock"


def test_hierarchy_get_all_children(session):
    root = Location(name="Zone", location_type=LocationType.view)
    c1 = Location(name="Aisle-1", location_type=LocationType.internal)
    c2 = Location(name="Aisle-2", location_type=LocationType.internal)
    gc1 = Location(name="Bin-01", location_type=LocationType.internal)
    session.add_all([root, c1, c2, gc1])
    session.flush()
    c1.parent_id = root.id
    c2.parent_id = root.id
    gc1.parent_id = c1.id
    session.flush()

    descendants = get_all_children(root.id, session)
    desc_ids = {d.id for d in descendants}
    assert c1.id in desc_ids
    assert c2.id in desc_ids
    assert gc1.id in desc_ids   # grandchild included
    assert root.id not in desc_ids


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


def test_quant_tablename_and_relationships(session):
    assert Quant.__tablename__ == "stock_quant"
    product = Product(name="Gadget", uom="unit")
    loc = Location(name="Shelf-Q", location_type=LocationType.internal)
    session.add_all([product, loc])
    session.flush()
    q = Quant.add_quantity(session, product.id, loc.id, Decimal("5"))
    session.flush()
    session.expire(q)
    assert q.product.name == "Gadget"
    assert q.location.name == "Shelf-Q"
    assert q.lot is None


def test_quant_add_quantity_idempotent(session):
    """Two add_quantity calls → single quant with summed qty."""
    product = Product(name="Sprocket", uom="unit")
    loc = Location(name="Bin-S", location_type=LocationType.internal)
    session.add_all([product, loc])
    session.flush()
    Quant.add_quantity(session, product.id, loc.id, Decimal("3"))
    Quant.add_quantity(session, product.id, loc.id, Decimal("7"))
    session.flush()
    quants = session.execute(
        __import__("sqlalchemy").select(Quant).where(
            Quant.product_id == product.id, Quant.location_id == loc.id
        )
    ).scalars().all()
    assert len(quants) == 1
    assert quants[0].quantity == Decimal("10")


def test_quant_get_available_zero_when_missing(session):
    product = Product(name="Ghost", uom="unit")
    loc = Location(name="Empty-Bin", location_type=LocationType.internal)
    session.add_all([product, loc])
    session.flush()
    assert Quant.get_available(session, product.id, loc.id) == Decimal("0")


def test_quant_get_available_minus_reserved(session):
    product = Product(name="Reserve-Part", uom="unit")
    loc = Location(name="Reserve-Bin", location_type=LocationType.internal)
    session.add_all([product, loc])
    session.flush()
    q = Quant.add_quantity(session, product.id, loc.id, Decimal("10"))
    session.flush()
    q.reserved_quantity = Decimal("3")
    session.flush()
    assert Quant.get_available(session, product.id, loc.id) == Decimal("7")


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

    picking.start()
    picking.validate()
    assert picking.state == PickingState.done


def test_picking_state_machine_invalid():
    picking = Picking(name="WH/IN/001")
    picking.state = PickingState.done
    with pytest.raises(InvalidTransition):
        picking.cancel()


def test_picking_start_method(session):
    product = Product(name="StartPart", uom="unit")
    src = Location(name="SrcStart", location_type=LocationType.internal)
    dest = Location(name="DestStart", location_type=LocationType.internal)
    session.add_all([product, src, dest])
    session.flush()

    picking = Picking(name="WH/START/001", location_src_id=src.id, location_dest_id=dest.id)
    session.add(picking)
    session.flush()

    picking.confirm()
    assert picking.state == PickingState.confirmed
    picking.start()
    assert picking.state == PickingState.in_progress


def test_picking_tablename():
    assert Picking.__tablename__ == "stock_picking"


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


def test_move_validate_updates_quants(session):
    """Move.validate(session) should decrement src and increment dest quants."""
    product = Product(name="ValidatePart", uom="unit")
    src = Location(name="SrcV", location_type=LocationType.internal)
    dest = Location(name="DestV", location_type=LocationType.internal)
    session.add_all([product, src, dest])
    session.flush()

    # Seed 10 units at src
    Quant.add_quantity(session, product.id, src.id, Decimal("10"))
    session.flush()

    move = Move(
        product_id=product.id,
        location_src_id=src.id,
        location_dest_id=dest.id,
        product_qty=Decimal("4"),
    )
    session.add(move)
    session.flush()

    move.validate(session)
    session.flush()

    assert move.state == MoveState.done
    assert move.qty_done == Decimal("4")
    assert Quant.get_available(session, product.id, src.id) == Decimal("6")
    assert Quant.get_available(session, product.id, dest.id) == Decimal("4")


def test_move_tablename():
    assert Move.__tablename__ == "stock_move"


def test_move_relationships(session):
    product = Product(name="RelPart", uom="unit")
    src = Location(name="SrcR", location_type=LocationType.internal)
    dest = Location(name="DestR", location_type=LocationType.internal)
    session.add_all([product, src, dest])
    session.flush()

    move = Move(
        product_id=product.id,
        location_src_id=src.id,
        location_dest_id=dest.id,
        product_qty=Decimal("1"),
    )
    session.add(move)
    session.flush()
    session.expire(move)

    assert move.product.name == "RelPart"
    assert move.src_location.name == "SrcR"
    assert move.dest_location.name == "DestR"
    assert move.lot is None


def test_stock_rule_tablename_and_defaults(session):
    src = Location(name="RuleSrc", location_type=LocationType.internal)
    dest = Location(name="RuleDest", location_type=LocationType.internal)
    session.add_all([src, dest])
    session.flush()

    rule = StockRule(
        name="Auto-replenish",
        action=RuleAction.pull,
        location_dest_id=dest.id,
    )
    session.add(rule)
    session.flush()

    assert StockRule.__tablename__ == "stock_rule"
    assert rule.action == RuleAction.pull
    assert rule.procure_method == ProcureMethod.make_to_stock
    assert rule.auto == RuleAuto.manual
    assert rule.delay == 0
    assert rule.warehouse_id is None


def test_package_tablename():
    assert Package.__tablename__ == "stock_quant_package"


def test_package_create(session):
    loc = Location(name="PkgBin", location_type=LocationType.internal)
    session.add(loc)
    session.flush()

    pkg = Package(name="PKG-001", location_id=loc.id)
    session.add(pkg)
    session.flush()
    assert pkg.id is not None
    assert pkg.name == "PKG-001"


def test_state_machine_can():
    from wms_core.utils.state_machine import StateMachine, PICKING_TRANSITIONS
    fsm = StateMachine(PICKING_TRANSITIONS)
    assert fsm.can("draft", "confirmed") is True
    assert fsm.can("draft", "done") is False
    assert fsm.can("done", "cancelled") is False


def test_no_circular_imports_full():
    from wms_core.models import (
        Warehouse, Location, Product, Lot, Quant,
        PickingType, Picking, Move, StockRule, Package,
    )
    assert StockRule.__tablename__ == "stock_rule"
    assert Package.__tablename__ == "stock_quant_package"
