import pytest
import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.ucp_tools import UCPCommerceEngine
from src.models import ProductItem, UCPCheckoutPayload

@pytest.fixture
def ucp_engine():
    return UCPCommerceEngine()

def test_search_catalog(ucp_engine):
    """Test searching the catalog returns valid ProductItem objects."""
    results = ucp_engine.search_catalog(query="Sony camera", category="Tech")
    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(p, ProductItem) for p in results)
    assert any("Sony" in p.brand for p in results)

def test_get_product_details(ucp_engine):
    """Test retrieving product details by exact SKU ID."""
    sku = "SKU-SONY-2470GM2"
    product = ucp_engine.get_product_details(sku)
    assert product is not None
    assert product.sku_id == sku
    assert product.brand == "Sony"
    assert product.price == 2298.00
    assert product.in_stock is True
    assert "mount" in product.specs

def test_validate_compatibility_success(ucp_engine):
    """Test compatibility check returns COMPATIBLE when mounts match."""
    sku = "SKU-SONY-2470GM2"
    context = {"camera_mount": "Sony E-mount"}
    result = ucp_engine.validate_compatibility(sku, context)
    assert result["compatible"] is True
    assert result["status"] == "COMPATIBLE"
    assert result["sku_id"] == sku

def test_validate_compatibility_failure(ucp_engine):
    """Test compatibility check returns INCOMPATIBLE when mounts mismatch."""
    sku = "SKU-SONY-2470GM2"
    context = {"camera_mount": "Canon RF-mount"}
    result = ucp_engine.validate_compatibility(sku, context)
    assert result["compatible"] is False
    assert result["status"] == "INCOMPATIBLE"

def test_create_checkout_session(ucp_engine):
    """Test 1-click Google Pay checkout session creation via UCP."""
    sku = "SKU-RODE-VMPPLUS"
    user_id = "usr_yt_test_101"
    creator_id = "creator_test_88"

    payload = ucp_engine.create_checkout_session(sku_id=sku, user_id=user_id, creator_id=creator_id, quantity=1)
    assert isinstance(payload, UCPCheckoutPayload)
    assert payload.sku_id == sku
    assert payload.creator_id == creator_id
    assert payload.payment_status == "SUCCESS"
    assert payload.total_amount == 299.00
    assert payload.creator_commission_amount == round(299.00 * 0.12, 2)
    assert payload.transaction_id.startswith("ucp_tx_")
    assert payload.confirmation_token.startswith("gpay_tok_zurich_")
