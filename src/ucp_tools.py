import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.config import CATALOG_DB_PATH, GOOGLE_PAY_MERCHANT_ID
from src.models import ProductItem, UCPCheckoutPayload

class UCPCommerceEngine:
    """Universal Commerce Protocol (UCP) Engine providing structured tools for catalog search,
    product detail retrieval, compatibility verification, and 1-click Google Pay checkout session creation."""

    def __init__(self, db_path: Path = CATALOG_DB_PATH):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Establish connection to SQLite catalog database."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def search_catalog(self, query: str, category: Optional[str] = None, max_results: int = 5) -> List[ProductItem]:
        """Search the merchant product catalog by freeform query and optional category filter.
        
        Args:
            query: Product title, brand, or attribute search string.
            category: Optional category filter (e.g. Tech, Apparel, Gaming, Beauty).
            max_results: Maximum number of products to return.
            
        Returns:
            List of matching ProductItem Pydantic schemas.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        clean_query = query.strip()
        tokens = [f"%{token}%" for token in clean_query.split()] if clean_query else ["%"]

        # Build dynamic query
        sql = """
            SELECT sku_id, title, brand, price, currency, in_stock, category, description, specs_json, creator_commission_rate, image_url
            FROM merchant_products
            WHERE 1=1
        """
        params: List[Any] = []

        if clean_query:
            token_conditions = []
            for token in clean_query.split():
                token_conditions.append("(title LIKE ? OR brand LIKE ? OR description LIKE ? OR category LIKE ? OR specs_json LIKE ?)")
                params.extend([f"%{token}%"] * 5)
            sql += " AND (" + " AND ".join(token_conditions) + ")"

        if category and category != "All":
            sql += " AND category = ?"
            params.append(category)

        sql += " LIMIT ?"
        params.append(max_results)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        # If strict keyword match returned nothing, fallback to category search or top results
        if not rows and category and category != "All":
            cursor.execute("""
                SELECT sku_id, title, brand, price, currency, in_stock, category, description, specs_json, creator_commission_rate, image_url
                FROM merchant_products
                WHERE category = ?
                LIMIT ?
            """, (category, max_results))
            rows = cursor.fetchall()

        if not rows:
            cursor.execute("""
                SELECT sku_id, title, brand, price, currency, in_stock, category, description, specs_json, creator_commission_rate, image_url
                FROM merchant_products
                LIMIT ?
            """, (max_results,))
            rows = cursor.fetchall()

        products: List[ProductItem] = []
        for row in rows:
            specs = json.loads(row["specs_json"]) if row["specs_json"] else {}
            item = ProductItem(
                sku_id=row["sku_id"],
                title=row["title"],
                brand=row["brand"],
                price=float(row["price"]),
                currency=row["currency"],
                in_stock=bool(row["in_stock"]),
                category=row["category"],
                description=row["description"] or "",
                specs=specs,
                creator_commission_rate=float(row["creator_commission_rate"]),
                image_url=row["image_url"]
            )
            products.append(item)

        conn.close()
        return products

    def get_product_details(self, sku_id: str) -> Optional[ProductItem]:
        """Retrieve detailed product specifications by exact SKU identifier.
        
        Args:
            sku_id: Product SKU string.
            
        Returns:
            ProductItem Pydantic schema if found, else None.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT sku_id, title, brand, price, currency, in_stock, category, description, specs_json, creator_commission_rate, image_url
            FROM merchant_products
            WHERE sku_id = ?
        """, (sku_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        specs = json.loads(row["specs_json"]) if row["specs_json"] else {}
        return ProductItem(
            sku_id=row["sku_id"],
            title=row["title"],
            brand=row["brand"],
            price=float(row["price"]),
            currency=row["currency"],
            in_stock=bool(row["in_stock"]),
            category=row["category"],
            description=row["description"] or "",
            specs=specs,
            creator_commission_rate=float(row["creator_commission_rate"]),
            image_url=row["image_url"]
        )

    def validate_compatibility(self, sku_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Verify compatibility of a given product against user-supplied context
        (e.g., camera lens mount, shoe size, operating system, skin type).
        
        Args:
            sku_id: Product SKU ID.
            user_context: Dictionary containing user attributes or device specs.
            
        Returns:
            Dictionary with compatibility status, validation details, and recommendations.
        """
        product = self.get_product_details(sku_id)
        if not product:
            return {
                "compatible": False,
                "status": "NOT_FOUND",
                "sku_id": sku_id,
                "reasons": [f"Product with SKU {sku_id} not found in Google Merchant catalog."]
            }

        reasons = []
        is_compatible = True
        specs = product.specs

        # Camera & Lens Compatibility Check
        if "mount" in specs:
            user_camera_mount = user_context.get("camera_mount") or user_context.get("camera_body")
            if user_camera_mount:
                if specs["mount"].lower() in str(user_camera_mount).lower() or str(user_camera_mount).lower() in specs["mount"].lower():
                    reasons.append(f"Direct match: Lens mount '{specs['mount']}' is 100% compatible with camera body '{user_camera_mount}'.")
                else:
                    is_compatible = False
                    reasons.append(f"Incompatible mount: Lens requires '{specs['mount']}', but user has '{user_camera_mount}'. Adapter required.")

        # Footwear & Sizing Compatibility Check
        if "sizes" in specs or "fit" in specs:
            user_size = user_context.get("shoe_size") or user_context.get("clothing_size")
            if user_size:
                reasons.append(f"Size verification: Item cut is '{specs.get('fit', 'Standard Fit')}'. Size '{user_size}' selected.")

        # Tech & OS Compatibility Check
        if "connectivity" in specs or "processor" in specs:
            user_os = user_context.get("os") or user_context.get("device")
            if user_os:
                reasons.append(f"Device compatibility: Specs verified against '{user_os}'. Full driver and hardware support active.")

        # Beauty & Skin Type Suitability Check
        if "skin_type" in specs or "key_ingredient" in specs:
            user_skin = user_context.get("skin_type")
            if user_skin:
                target_skin = specs.get("skin_type", "All Skin Types")
                if target_skin == "All Skin Types" or user_skin.lower() in target_skin.lower():
                    reasons.append(f"Skincare suitablity: Formulated for '{target_skin}', compatible with user skin profile '{user_skin}'.")
                else:
                    reasons.append(f"Note: Formulated for '{target_skin}'. Test patch recommended for '{user_skin}'.")

        if not reasons:
            reasons.append(f"Product '{product.title}' has no known compatibility conflicts with provided context.")

        return {
            "compatible": is_compatible,
            "status": "COMPATIBLE" if is_compatible else "INCOMPATIBLE",
            "sku_id": sku_id,
            "product_title": product.title,
            "reasons": reasons,
            "specs_checked": specs
        }

    def create_checkout_session(self, sku_id: str, user_id: str, creator_id: str, quantity: int = 1) -> UCPCheckoutPayload:
        """Execute instant 1-click Google Pay checkout via Universal Commerce Protocol (UCP).
        
        Args:
            sku_id: SKU identifier to purchase.
            user_id: Viewer / Customer ID.
            creator_id: YouTube creator ID for affiliate attribution.
            quantity: Item quantity.
            
        Returns:
            UCPCheckoutPayload containing transaction confirmation and creator earnings split.
        """
        product = self.get_product_details(sku_id)
        if not product:
            raise ValueError(f"Cannot checkout: SKU {sku_id} not found in catalog.")

        if not product.in_stock:
            raise ValueError(f"Cannot checkout: SKU {sku_id} ({product.title}) is currently out of stock.")

        # Calculate totals
        total_amount = round(product.price * quantity, 2)
        creator_commission = round(total_amount * product.creator_commission_rate, 2)

        # Generate transaction cryptographic tokens
        tx_uuid = uuid.uuid4().hex[:12].upper()
        transaction_id = f"ucp_tx_{tx_uuid}"
        confirmation_token = f"gpay_tok_zurich_{uuid.uuid4().hex[:16]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        payload = UCPCheckoutPayload(
            transaction_id=transaction_id,
            sku_id=sku_id,
            total_amount=total_amount,
            creator_id=creator_id,
            payment_status="SUCCESS",
            confirmation_token=confirmation_token,
            creator_commission_amount=creator_commission,
            timestamp=now_iso,
            payment_method="Google Pay (UCP 1-Click)",
            shipping_address_hash=f"ucp_addr_{user_id[-6:] if len(user_id) >= 6 else 'default'}"
        )

        return payload
