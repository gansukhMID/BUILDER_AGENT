from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecommerce_core.models.pricelist import Pricelist, PricelistItem, AppliedOn
    from ecommerce_core.models.product import ProductVariant

# Specificity rank: higher = matched first
_SPECIFICITY_RANK = {"variant": 3, "product": 2, "category": 1, "all": 0}


def _item_matches(item: "PricelistItem", variant: "ProductVariant", qty: Decimal) -> bool:
    """Return True if this pricelist item applies to the given variant and qty."""
    if qty < item.min_quantity:
        return False
    scope = item.applied_on.value if hasattr(item.applied_on, "value") else item.applied_on
    if scope == "all":
        return True
    if scope == "variant":
        return item.product_variant_id == variant.id
    if scope == "product":
        return item.product_template_id == variant.template_id
    if scope == "category":
        return item.category_id == variant.template.category_id
    return False


def _compute(item: "PricelistItem", variant: "ProductVariant") -> Decimal:
    """Apply item's compute_price rule and return unit price."""
    mode = item.compute_price.value if hasattr(item.compute_price, "value") else item.compute_price
    if mode == "fixed":
        return Decimal(str(item.fixed_price))
    if mode == "percentage":
        discount_pct = Decimal(str(item.price_discount or 0))
        base = Decimal(str(variant.template.list_price))
        return base * (1 - discount_pct / 100)
    if mode == "formula":
        raise NotImplementedError(
            "ComputePrice.formula is an extension point — subclass PricelistItem and override _compute()."
        )
    raise ValueError(f"Unknown compute_price mode: {mode}")


def evaluate_pricelist(
    pricelist: "Pricelist",
    variant: "ProductVariant",
    qty: Decimal,
) -> Decimal:
    """Evaluate pricelist rules and return effective unit price.

    Matching order: specificity desc → priority desc → min_quantity desc.
    Falls back to variant.default_price if no rule matches.
    """
    candidates = [item for item in pricelist.items if _item_matches(item, variant, qty)]
    if not candidates:
        return Decimal(str(variant.default_price))

    candidates.sort(
        key=lambda it: (
            _SPECIFICITY_RANK.get(
                it.applied_on.value if hasattr(it.applied_on, "value") else it.applied_on, 0
            ),
            it.priority,
            it.min_quantity,
        ),
        reverse=True,
    )
    return _compute(candidates[0], variant)
