from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecommerce_core.models.pricelist import Pricelist
    from ecommerce_core.models.product import ProductVariant


def evaluate_pricelist(
    pricelist: "Pricelist",
    variant: "ProductVariant",
    qty: Decimal,
) -> Decimal:
    """Evaluate pricelist rules and return effective unit price for variant at qty.

    Implemented in task #31. Raises NotImplementedError until then.
    """
    raise NotImplementedError(
        "evaluate_pricelist is implemented in task #31 (Pricing Models & Engine)."
    )
