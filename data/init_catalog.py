import sqlite3
import json
import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from src.config import CATALOG_DB_PATH, TRANSCRIPTS_JSON_PATH

PRODUCTS_DATA = [
    # Electronics & Camera Gear (Tech)
    {
        "sku_id": "SKU-SONY-A7IV",
        "title": "Sony Alpha 7 IV Full-Frame Mirrorless Camera",
        "brand": "Sony",
        "price": 2498.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "33MP full-frame Exmor R CMOS sensor camera with 4K 60p video and advanced autofocus.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400",
        "specs": {"mount": "Sony E-mount", "sensor": "33MP Full-Frame", "resolution": "4K 60p", "weight": "658g", "stabilization": "5-axis IBIS"}
    },
    {
        "sku_id": "SKU-SONY-2470GM2",
        "title": "Sony FE 24-70mm f/2.8 GM II Lens",
        "brand": "Sony",
        "price": 2298.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Lightweight standard zoom lens with f/2.8 constant aperture and XD Linear Motors.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1617005082133-548c4dd27f35?w=400",
        "specs": {"mount": "Sony E-mount", "focal_length": "24-70mm", "max_aperture": "f/2.8", "filter_size": "82mm", "weight": "695g"}
    },
    {
        "sku_id": "SKU-SONY-70200GM2",
        "title": "Sony FE 70-200mm f/2.8 GM OSS II Lens",
        "brand": "Sony",
        "price": 2798.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Flagship telephoto zoom lens providing breathtaking sharpness and creamy bokeh.",
        "creator_commission_rate": 0.09,
        "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400",
        "specs": {"mount": "Sony E-mount", "focal_length": "70-200mm", "max_aperture": "f/2.8", "filter_size": "77mm", "weight": "1045g"}
    },
    {
        "sku_id": "SKU-RODE-VMPPLUS",
        "title": "Rode VideoMic Pro+ On-Camera Shotgun Microphone",
        "brand": "Rode",
        "price": 299.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Best-in-class broadcast camera mic with automatic power functionality and rechargeable battery.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
        "specs": {"polar_pattern": "Supercardioid", "frequency_range": "20Hz-20kHz", "output": "3.5mm TRS", "battery": "LB-1 Li-Ion"}
    },
    {
        "sku_id": "SKU-PEAK-TRIPOD-CF",
        "title": "Peak Design Travel Tripod (Carbon Fiber)",
        "brand": "Peak Design",
        "price": 649.95,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Ultra-compact carbon fiber travel tripod that packs down to the diameter of a water bottle.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1519638399535-1b036603ac77?w=400",
        "specs": {"material": "Carbon Fiber", "max_height": "152.4 cm", "weight": "1.27 kg", "weight_capacity": "9.1 kg"}
    },
    {
        "sku_id": "SKU-APP-MBP16M3",
        "title": "Apple MacBook Pro 16-inch (M3 Max, 36GB RAM, 1TB SSD)",
        "brand": "Apple",
        "price": 3499.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Pro laptop powered by M3 Max chip with Liquid Retina XDR display and 22-hour battery life.",
        "creator_commission_rate": 0.05,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
        "specs": {"processor": "Apple M3 Max", "ram": "36GB Unified", "storage": "1TB SSD", "screen": "16.2 inch XDR", "color": "Space Black"}
    },
    {
        "sku_id": "SKU-SONY-WHXM5",
        "title": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones",
        "brand": "Sony",
        "price": 398.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Industry-leading noise cancellation with 8 microphones and Auto NC Optimizer.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400",
        "specs": {"battery_life": "30 hrs", "bluetooth": "5.2", "weight": "250g", "codecs": "LDAC, AAC, SBC"}
    },
    {
        "sku_id": "SKU-APP-APMAX",
        "title": "Apple AirPods Max Wireless Over-Ear Headphones",
        "brand": "Apple",
        "price": 549.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "High-fidelity audio with Active Noise Cancellation, Transparency mode, and Personalized Spatial Audio.",
        "creator_commission_rate": 0.05,
        "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400",
        "specs": {"chip": "Apple H1 (each ear cup)", "battery_life": "20 hrs", "weight": "384.8g", "color": "Space Gray"}
    },
    {
        "sku_id": "SKU-DJI-MINI4PRO",
        "title": "DJI Mini 4 Pro Fly More Combo Drone",
        "brand": "DJI",
        "price": 1099.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Under 249g mini drone with 4K/60fps HDR video, omnidirectional obstacle sensing, and 34-min flight time.",
        "creator_commission_rate": 0.07,
        "image_url": "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=400",
        "specs": {"weight": "< 249g", "camera": "4K/60fps HDR", "transmission": "DJI O4 20km", "flight_time": "34 mins"}
    },
    {
        "sku_id": "SKU-ELG-STREAMDECK",
        "title": "Elgato Stream Deck MK.2 Control Surface",
        "brand": "Elgato",
        "price": 149.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "15 customizable LCD keys for instant control of streaming tools, apps, and video production.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1563089145-599997674d42?w=400",
        "specs": {"keys": "15 LCD keys", "interface": "USB 2.0", "dimensions": "118 x 84 x 25 mm", "weight": "145g"}
    },
    {
        "sku_id": "SKU-SHURE-SM7B",
        "title": "Shure SM7B Cardioid Dynamic Vocal Microphone",
        "brand": "Shure",
        "price": 399.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Legendary studio microphone revered for speech, podcasting, and broadcast vocal warmth.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
        "specs": {"polar_pattern": "Cardioid", "frequency_range": "50Hz-20kHz", "connector": "XLR", "weight": "765g"}
    },
    {
        "sku_id": "SKU-KEY-Q1PRO",
        "title": "Keychron Q1 Pro QMK/VIA Wireless Mechanical Keyboard",
        "brand": "Keychron",
        "price": 199.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Full aluminum 75% layout wireless custom mechanical keyboard with hot-swappable switches.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400",
        "specs": {"layout": "75%", "connectivity": "Bluetooth 5.1 / Type-C", "switches": "KPro Banana / Red", "body": "CNC Aluminum"}
    },
    {
        "sku_id": "SKU-LOGI-MXM3S",
        "title": "Logitech MX Master 3S Performance Wireless Mouse",
        "brand": "Logitech",
        "price": 99.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "Ergonomic precision wireless mouse with 8K DPI sensor and ultra-quiet click switches.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400",
        "specs": {"sensor": "8000 DPI Darkfield", "connectivity": "Bluetooth / Logi Bolt", "clicks": "Quiet Clicks 90% reduction", "weight": "141g"}
    },
    {
        "sku_id": "SKU-LG-34OLED",
        "title": "LG UltraGear 34GS95QE 34\" Curved OLED Gaming Monitor",
        "brand": "LG",
        "price": 1299.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "34-inch 240Hz 0.03ms WQHD Curved OLED display with 800R curvature for immersive gaming.",
        "creator_commission_rate": 0.06,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400",
        "specs": {"screen_size": "34 inch", "panel": "OLED 800R", "refresh_rate": "240Hz", "response_time": "0.03ms", "resolution": "3440x1440"}
    },
    {
        "sku_id": "SKU-ANK-POWER20K",
        "title": "Anker Prime 20,000mAh Power Bank (200W Output)",
        "brand": "Anker",
        "price": 129.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Tech",
        "description": "High-capacity smart power bank capable of fast charging two laptops simultaneously at up to 100W each.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1609592424009-dd27909c2a6a?w=400",
        "specs": {"capacity": "20,000mAh", "max_output": "200W", "ports": "2x USB-C, 1x USB-A", "display": "Smart Digital Screen"}
    },

    # Apparel & Accessories (Fashion)
    {
        "sku_id": "SKU-ACNE-TRENCH-BRN",
        "title": "Acne Studios Double-Breasted Wool Blend Trench Coat",
        "brand": "Acne Studios",
        "price": 1150.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Iconic autumn camel trench coat crafted from heavy Italian wool blend with tailored shoulder silhouette.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=400",
        "specs": {"material": "80% Wool, 20% Polyamide", "fit": "Oversized Tailored", "color": "Camel Brown", "sizes": "XS, S, M, L"}
    },
    {
        "sku_id": "SKU-DRM-1460BOOTS",
        "title": "Dr. Martens 1460 Pascal Smooth Leather Boots",
        "brand": "Dr. Martens",
        "price": 170.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Classic 8-eye boot constructed with soft Pascal leather and signature yellow welt stitching.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "specs": {"upper": "100% Virginia Leather", "sole": "AirWair Cushion Sole", "construction": "Goodyear Welted", "color": "Black"}
    },
    {
        "sku_id": "SKU-REF-CASHMERE-BLK",
        "title": "Reformation Clara Oversized Cashmere Crewneck Sweater",
        "brand": "Reformation",
        "price": 278.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Luxuriously plush 100% recycled cashmere sweater with relaxed drop-shoulder cut.",
        "creator_commission_rate": 0.14,
        "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=400",
        "specs": {"material": "100% Recycled Cashmere", "fit": "Relaxed Oversized", "color": "Black", "care": "Dry Clean / Hand Wash"}
    },
    {
        "sku_id": "SKU-TOT-SCARF-BEIGE",
        "title": "Toteme Signature Wool Jacquard Monogram Scarf",
        "brand": "Toteme",
        "price": 340.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Essential winter wool scarf featuring Toteme's geometric jacquard monogram pattern.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=400",
        "specs": {"material": "100% Responsible Wool", "dimensions": "180 x 50 cm", "color": "Beige / Cream", "made_in": "Italy"}
    },
    {
        "sku_id": "SKU-LEVI-501DENIM",
        "title": "Levi's 501 Original Fit Unisex Raw Denim Jeans",
        "brand": "Levi's",
        "price": 98.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "The archetypal straight leg jean with button fly and rigid cotton construction.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400",
        "specs": {"material": "100% Non-Stretch Cotton", "fit": "Straight Leg", "rise": "Mid Rise", "fly": "Button Fly"}
    },
    {
        "sku_id": "SKU-CARH-HOODIE-GRN",
        "title": "Carhartt WIP Heavyweight Hooded Vista Sweatshirt",
        "brand": "Carhartt WIP",
        "price": 188.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Pigment-dyed heavyweight cotton fleece hoodie with balloon fit cut and brushed soft interior.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400",
        "specs": {"material": "100% Cotton Fleece (456 gsm)", "fit": "Balloon Cut", "color": "Vista Olive Green"}
    },
    {
        "sku_id": "SKU-RAY-WAYFARER",
        "title": "Ray-Ban Original Wayfarer Classic Sunglasses",
        "brand": "Ray-Ban",
        "price": 171.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Timeless acetate frame sunglasses equipped with G-15 green crystal lenses.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400",
        "specs": {"frame": "Black Acetate", "lens": "G-15 Green Glass", "uv_protection": "100% UV400", "size": "50-22"}
    },
    {
        "sku_id": "SKU-ARC-BETAAR",
        "title": "Arc'teryx Beta AR Waterproof Gore-Tex Pro Jacket",
        "brand": "Arc'teryx",
        "price": 600.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Versatile all-round mountain hardshell crafted from durable Gore-Tex Pro Most Rugged technology.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=400",
        "specs": {"membrane": "Gore-Tex Pro 3L", "hood": "DropHood storm protection", "weight": "461g", "fit": "Regular Fit"}
    },
    {
        "sku_id": "SKU-SAL-XT6GTX",
        "title": "Salomon XT-6 GTX Gore-Tex Trail Sneakers",
        "brand": "Salomon",
        "price": 220.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Iconic outdoor silhouette upgraded with ePE Gore-Tex waterproof membrane and Quicklace system.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400",
        "specs": {"membrane": "Gore-Tex Waterproof", "lacing": "Quicklace", "outsole": "Mud Contagrip", "weight": "357g"}
    },
    {
        "sku_id": "SKU-STUSSY-SWEATPANTS",
        "title": "Stüssy Heavyweight Stock Logo Fleece Sweatpants",
        "brand": "Stüssy",
        "price": 120.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Relaxed fit fleece pants with elastic cuffs and embroidered signature Stüssy logo.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=400",
        "specs": {"material": "100% Heavyweight Cotton Fleece", "fit": "Relaxed Straight", "color": "Ash Grey"}
    },
    {
        "sku_id": "SKU-FJL-KANKEN",
        "title": "Fjällräven Kånken Classic Everyday Backpack",
        "brand": "Fjällräven",
        "price": 90.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Durable, water-resistant Vinylon F backpack created in Sweden in 1978.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
        "specs": {"volume": "16 Liters", "material": "Vinylon F", "dimensions": "38 x 27 x 13 cm", "weight": "300g"}
    },
    {
        "sku_id": "SKU-BIRK-BOSTON-TAUPE",
        "title": "Birkenstock Boston Soft Footbed Suede Clogs",
        "brand": "Birkenstock",
        "price": 160.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Classic slip-on clog crafted from velvety soft suede with anatomically shaped cork-latex footbed.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=400",
        "specs": {"upper": "Velour Suede Leather", "footbed": "Soft Cork Footbed", "color": "Taupe", "sole": "EVA"}
    },
    {
        "sku_id": "SKU-PAT-SWEATER14",
        "title": "Patagonia Better Sweater 1/4-Zip Fleece",
        "brand": "Patagonia",
        "price": 139.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Fair Trade Certified pullover made from 100% recycled polyester fleece dyed with low-impact process.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=400",
        "specs": {"material": "100% Recycled Polyester Fleece", "weight": "505g", "certification": "Fair Trade Certified"}
    },
    {
        "sku_id": "SKU-COS-BLAZER-BLK",
        "title": "COS Oversized Double-Breasted Tailored Wool Blazer",
        "brand": "COS",
        "price": 275.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Modern capsule wardrobe blazer tailored from premium wool blend with structured shoulders.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400",
        "specs": {"material": "96% Wool, 4% Elastane", "fit": "Oversized Boxy", "color": "Black"}
    },
    {
        "sku_id": "SKU-APC-BAG-GRACE",
        "title": "A.P.C. Grace Small Smooth Leather Shoulder Bag",
        "brand": "A.P.C.",
        "price": 695.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Apparel",
        "description": "Structured Parisian leather bag featuring gold metallic clasp and adjustable shoulder strap.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400",
        "specs": {"material": "100% Cowhide Leather", "dimensions": "21.5 x 17 x 5 cm", "color": "Black / Gold Hardware"}
    },

    # Gaming & Entertainment (Gaming)
    {
        "sku_id": "SKU-ASUS-ROGALLYX",
        "title": "ASUS ROG Ally X Handheld Gaming PC (1TB SSD, 24GB RAM)",
        "brand": "ASUS",
        "price": 799.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Windows 11 handheld gaming console powered by AMD Ryzen Z1 Extreme with 80Wh battery capacity.",
        "creator_commission_rate": 0.06,
        "image_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=400",
        "specs": {"processor": "AMD Ryzen Z1 Extreme", "ram": "24GB LPDDR5X", "storage": "1TB M.2 NVMe", "battery": "80Wh", "display": "7\" 120Hz FHD"}
    },
    {
        "sku_id": "SKU-SONY-PS5PRO",
        "title": "Sony PlayStation 5 Pro Console (Digital Edition)",
        "brand": "Sony",
        "price": 699.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Advanced gaming console featuring PlayStation Spectral Super Resolution (PSSR) AI upscaling and 2TB SSD.",
        "creator_commission_rate": 0.05,
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400",
        "specs": {"gpu": "Advanced Ray Tracing GPU", "storage": "2TB Custom SSD", "upscaling": "PSSR AI Upscaling", "wifi": "Wi-Fi 7"}
    },
    {
        "sku_id": "SKU-MSFT-XBOXCTRL",
        "title": "Xbox Wireless Controller (Velocity Green Edition)",
        "brand": "Microsoft",
        "price": 64.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Textured grip wireless controller with Share button, hybrid D-pad, and cross-device Bluetooth compatibility.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=400",
        "specs": {"connectivity": "Xbox Wireless & Bluetooth", "battery": "AA (Up to 40 hrs)", "color": "Velocity Green"}
    },
    {
        "sku_id": "SKU-SECRETLAB-EVO",
        "title": "Secretlab TITAN Evo Ergonomic Gaming Chair",
        "brand": "Secretlab",
        "price": 549.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Ergonomic gaming chair with L-ADAPT 4-way lumbar support system and SoftWeave Plus fabric.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=400",
        "specs": {"upholstery": "SoftWeave Plus Fabric", "lumbar": "L-ADAPT 4-Way System", "armrests": "4D Full-Metal", "size": "Regular / Large"}
    },
    {
        "sku_id": "SKU-STEEL-NOVAPRO",
        "title": "SteelSeries Arctis Nova Pro Wireless Gaming Headset",
        "brand": "SteelSeries",
        "price": 349.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Premium multi-system wireless headset with active noise cancellation and hot-swappable dual battery system.",
        "creator_commission_rate": 0.08,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400",
        "specs": {"drivers": "40mm High Fidelity", "anc": "4-Mic Hybrid ANC", "wireless": "2.4GHz + Bluetooth", "battery": "Hot-swappable dual pack"}
    },
    {
        "sku_id": "SKU-RAZER-DA-V3",
        "title": "Razer DeathAdder V3 Pro Wireless Ergonomic Mouse",
        "brand": "Razer",
        "price": 149.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Ultra-lightweight 63g esports wireless gaming mouse with Focus Pro 30K Optical Sensor.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=400",
        "specs": {"weight": "63g ultra-light", "sensor": "Focus Pro 30K DPI", "battery_life": "90 hrs", "polling": "Up to 4000Hz HyperPolling"}
    },
    {
        "sku_id": "SKU-META-QUEST3",
        "title": "Meta Quest 3 512GB Breakthrough Mixed Reality Headset",
        "brand": "Meta",
        "price": 649.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Mixed reality VR headset powered by Snapdragon XR2 Gen 2 with high-resolution color Passthrough.",
        "creator_commission_rate": 0.05,
        "image_url": "https://images.unsplash.com/photo-1622979135225-d2ba269bc1bd?w=400",
        "specs": {"chip": "Snapdragon XR2 Gen 2", "display": "4K+ Infinite Display (2064x2208 per eye)", "passthrough": "Full-color passthrough", "storage": "512GB"}
    },
    {
        "sku_id": "SKU-ELG-KEYLIGHT",
        "title": "Elgato Key Light Air Professional Desktop LED Panel",
        "brand": "Elgato",
        "price": 129.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Wi-Fi enabled 1400 lumen studio LED panel controllable via app, Mac, PC, and Stream Deck.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1563089145-599997674d42?w=400",
        "specs": {"brightness": "1400 Lumens", "color_temp": "2900 - 7000 K", "power": "25W", "control": "Wi-Fi App / Stream Deck"}
    },
    {
        "sku_id": "SKU-SAMSUNG-G9OLED",
        "title": "Samsung Odyssey OLED G9 49\" Dual QHD Curved Monitor",
        "brand": "Samsung",
        "price": 1799.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Massive 49-inch 32:9 super-ultrawide OLED monitor with 240Hz refresh rate and Neo Quantum Processor Pro.",
        "creator_commission_rate": 0.05,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400",
        "specs": {"resolution": "5120 x 1440 (Dual QHD)", "refresh_rate": "240Hz", "response_time": "0.03ms", "curvature": "1800R"}
    },
    {
        "sku_id": "SKU-NANO-LINES10",
        "title": "Nanoleaf Lines RGB LED Smart Wall Light Expansion Kit",
        "brand": "Nanoleaf",
        "price": 199.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Gaming",
        "description": "Modular backlit smart ambient light bars with 16M+ colors and screen-mirror synchronization.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400",
        "specs": {"bars": "9 Smart LED Light Lines", "connectivity": "Wi-Fi (2.4 GHz)", "features": "Rhythm Music Visualizer, Screen Mirror"}
    },

    # Beauty & Personal Care (Beauty)
    {
        "sku_id": "SKU-COSRX-SNAIL96",
        "title": "COSRX Advanced Snail 96 Mucin Power Essence (100ml)",
        "brand": "COSRX",
        "price": 25.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Hydrating K-beauty essence containing 96.3% snail secretion filtrate to soothe and plump skin.",
        "creator_commission_rate": 0.15,
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400",
        "specs": {"volume": "100ml / 3.38 fl.oz", "key_ingredient": "96.3% Snail Secretion Filtrate", "skin_type": "All Skin Types", "cruelty_free": True}
    },
    {
        "sku_id": "SKU-BOJ-RELIEFSUN",
        "title": "Beauty of Joseon Relief Sun SPF50+ PA++++ Rice + Probiotics",
        "brand": "Beauty of Joseon",
        "price": 18.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Organic K-beauty chemical sunscreen enriched with 30% rice extract and grain fermented extracts.",
        "creator_commission_rate": 0.15,
        "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400",
        "specs": {"spf": "SPF50+ PA++++", "volume": "50ml", "finish": "Dewy Non-Sticky", "key_ingredient": "30% Rice Extract"}
    },
    {
        "sku_id": "SKU-LANEIGE-LIPMASK",
        "title": "Laneige Lip Sleeping Mask (Berry Flavor 20g)",
        "brand": "Laneige",
        "price": 24.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Overnight lip treatment infused with Berry Mix Complex and Vitamin C for intense hydration.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400",
        "specs": {"weight": "20g / 0.70 oz", "flavor": "Berry", "key_ingredients": "Vitamin C, Moisture Wrap Tech"}
    },
    {
        "sku_id": "SKU-DYSON-AIRWRAP",
        "title": "Dyson Airwrap Multi-Styler Complete Long (Strawberry Bronze)",
        "brand": "Dyson",
        "price": 599.99,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Harnesses Coanda air airflow to curl, shape, and smooth hair without extreme heat damage.",
        "creator_commission_rate": 0.06,
        "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400",
        "specs": {"power": "1300W", "airflow": "13.5 L/s", "attachments": "6 Re-engineered Attachments", "heat_settings": "3 Temperature Controls"}
    },
    {
        "sku_id": "SKU-PAULAS-2BHA",
        "title": "Paula's Choice Skin Perfecting 2% BHA Liquid Exfoliant",
        "brand": "Paula's Choice",
        "price": 35.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Global cult-favorite leave-on salicylic acid exfoliant that unclogs pores and evens skin texture.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400",
        "specs": {"volume": "118ml / 4 fl.oz", "active": "2% Salicylic Acid (BHA)", "ph": "3.5 - 3.9", "target": "Pores & Blackheads"}
    },
    {
        "sku_id": "SKU-SKINC-CEFERULIC",
        "title": "SkinCeuticals C E Ferulic High-Potency Antioxidant Serum",
        "brand": "SkinCeuticals",
        "price": 182.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Patented daytime vitamin C serum yielding 8x environmental protection and visible anti-aging gains.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1608248597349-490b63384260?w=400",
        "specs": {"volume": "30ml / 1 fl.oz", "formula": "15% Pure L-Ascorbic Acid, 1% Alpha Tocopherol, 0.5% Ferulic Acid"}
    },
    {
        "sku_id": "SKU-SOL-BUMBUM240",
        "title": "Sol de Janeiro Brazilian Bum Bum Body Cream (240ml)",
        "brand": "Sol de Janeiro",
        "price": 48.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Fast-absorbing body cream with Guaraná extract to visibly tighten skin and iconic Cheirosa 62 scent.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=400",
        "specs": {"volume": "240ml / 8.1 fl.oz", "scent": "Pistachio & Salted Caramel", "key_ingredient": "Guaraná Extract"}
    },
    {
        "sku_id": "SKU-DRUNK-LALA",
        "title": "Drunk Elephant Lala Retro Whipped Cream Moisturizer",
        "brand": "Drunk Elephant",
        "price": 64.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Rescue cream with 6 African oils and plant ceramides that restores skin's natural moisture barrier.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400",
        "specs": {"volume": "50ml / 1.69 fl.oz", "ph": "5.2", "formulation": "Ceramide Complex + 6 African Oils"}
    },
    {
        "sku_id": "SKU-GLOSSIER-YOU",
        "title": "Glossier You Eau de Parfum (50ml)",
        "brand": "Glossier",
        "price": 72.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Personal skin-enhancer scent with warm pink pepper top notes and iris, ambrette, and ambrox base.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=400",
        "specs": {"volume": "50ml / 1.7 fl.oz", "family": "Soft Warm Musk", "key_notes": "Pink Pepper, Iris, Ambrox"}
    },
    {
        "sku_id": "SKU-THERA-FACEPRO",
        "title": "Therabody TheraFace PRO 8-in-1 Facial Health Device",
        "brand": "Therabody",
        "price": 399.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "FDA-cleared facial therapy wand combining percussive facial therapy, microcurrent, LED lights, and cleansing.",
        "creator_commission_rate": 0.10,
        "image_url": "https://images.unsplash.com/photo-1512290900676-26c2a4d4b5b3?w=400",
        "specs": {"treatments": "Percussive, Microcurrent, Red/Blue LED, Cleansing Ring", "fda_cleared": True, "battery": "120 mins"}
    },
    {
        "sku_id": "SKU-GLOSSIER-BLUSH",
        "title": "Glossier Cloud Paint Seamless Gel-Cream Blush (Storm)",
        "brand": "Glossier",
        "price": 22.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "User-friendly, buildable cheek color with sheer, natural, flush-from-within finish.",
        "creator_commission_rate": 0.12,
        "image_url": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400",
        "specs": {"volume": "10ml / 0.33 fl.oz", "shade": "Storm (Warm Rose)", "finish": "Dewy Natural"}
    },
    {
        "sku_id": "SKU-ANUA-TONER77",
        "title": "Anua Heartleaf 77% Soothing Toner (250ml)",
        "brand": "Anua",
        "price": 23.00,
        "currency": "USD",
        "in_stock": True,
        "category": "Beauty",
        "description": "Viral K-beauty sub-acidic toner featuring 77% Heartleaf extract to calm redness and acne-prone skin.",
        "creator_commission_rate": 0.15,
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400",
        "specs": {"volume": "250ml / 8.45 fl.oz", "key_ingredient": "77% Houttuynia Cordata (Heartleaf)", "ph": "5.5 - 6.0"}
    }
]

VIDEOS_DATA = [
    {
        "video_id": "vid_sony_alpha",
        "title": "Sony Alpha 7 IV & FE 24-70mm GM II Ultimate Review",
        "channel_name": "TechVision Pro (Zurich Studio)",
        "creator_id": "creator_techvision_88",
        "duration": 300.0,
        "category": "Tech",
        "creator_affiliate_settings": {"default_rate": 0.08, "custom_bonus": 0.02},
        "transcript_cues": [
            {
                "timestamp_start": 0.0,
                "timestamp_end": 15.0,
                "speaker": "Marc",
                "text": "Welcome back! Today we are testing the Sony Alpha 7 IV paired with the new 24-70mm GM II lens here in Zurich.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-SONY-A7IV", "SKU-SONY-2470GM2"]
            },
            {
                "timestamp_start": 15.1,
                "timestamp_end": 45.0,
                "speaker": "Marc",
                "text": "The 33-megapixel sensor gives incredible dynamic range, and the 24-70mm f/2.8 lens is surprisingly lightweight for handheld work.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-SONY-A7IV", "SKU-SONY-2470GM2"]
            },
            {
                "timestamp_start": 45.1,
                "timestamp_end": 90.0,
                "speaker": "Marc",
                "text": "For audio, I am recording with the Rode VideoMic Pro+ mounted directly on top of the Peak Design Travel Tripod.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-RODE-VMPPLUS", "SKU-PEAK-TRIPOD-CF"]
            },
            {
                "timestamp_start": 90.1,
                "timestamp_end": 180.0,
                "speaker": "Marc",
                "text": "If you want to step up to telephoto, the 70-200mm f/2.8 GM II provides unbelievable compression and isolation.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-SONY-70200GM2"]
            },
            {
                "timestamp_start": 180.1,
                "timestamp_end": 300.0,
                "speaker": "Marc",
                "text": "Overall this is my main video rig for 2026. Check the in-stream shop drawer below to get 1-click checkout with Google Pay!",
                "sensitive_tag": None,
                "featured_skus": ["SKU-SONY-A7IV", "SKU-SONY-2470GM2"]
            }
        ]
    },
    {
        "video_id": "vid_autumn_fashion",
        "title": "NYC Autumn Capsule Wardrobe & Fall Style Haul",
        "channel_name": "Elena Haute Zurich",
        "creator_id": "creator_elena_haute_14",
        "duration": 300.0,
        "category": "Apparel",
        "creator_affiliate_settings": {"default_rate": 0.12, "custom_bonus": 0.03},
        "transcript_cues": [
            {
                "timestamp_start": 0.0,
                "timestamp_end": 30.0,
                "speaker": "Elena",
                "text": "Hi everyone! Fall is finally here, so today I'm styling my essential Autumn capsule wardrobe pieces.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-ACNE-TRENCH-BRN"]
            },
            {
                "timestamp_start": 30.1,
                "timestamp_end": 75.0,
                "speaker": "Elena",
                "text": "First up is this Acne Studios double-breasted camel trench coat paired with the Reformation black recycled cashmere sweater.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-ACNE-TRENCH-BRN", "SKU-REF-CASHMERE-BLK"]
            },
            {
                "timestamp_start": 75.1,
                "timestamp_end": 140.0,
                "speaker": "Elena",
                "text": "For footwear, these Dr. Martens 1460 Pascal smooth leather boots give the outfit a nice structured edge.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-DRM-1460BOOTS"]
            },
            {
                "timestamp_start": 140.1,
                "timestamp_end": 210.0,
                "speaker": "Elena",
                "text": "I've wrapped this Toteme signature wool scarf around my shoulders, and carried the A.P.C. Grace leather bag.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-TOT-SCARF-BEIGE", "SKU-APC-BAG-GRACE"]
            },
            {
                "timestamp_start": 210.1,
                "timestamp_end": 300.0,
                "speaker": "Elena",
                "text": "Let me know your favorite piece in the comments! You can tap any item right now on screen for instant instant sizing and checkout.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-ACNE-TRENCH-BRN", "SKU-REF-CASHMERE-BLK", "SKU-DRM-1460BOOTS"]
            }
        ]
    },
    {
        "video_id": "vid_earthquake_news",
        "title": "BREAKING: 6.8 Earthquake Hits Pacific Rim - Emergency Response Live",
        "channel_name": "Global News Network Live",
        "creator_id": "creator_gnn_news_01",
        "duration": 300.0,
        "category": "News",
        "creator_affiliate_settings": {"default_rate": 0.00, "custom_bonus": 0.00},
        "transcript_cues": [
            {
                "timestamp_start": 0.0,
                "timestamp_end": 29.9,
                "speaker": "Anchor",
                "text": "Good morning. We are following breaking news from the Pacific region.",
                "sensitive_tag": None,
                "featured_skus": []
            },
            {
                "timestamp_start": 30.0,
                "timestamp_end": 120.0,
                "speaker": "Anchor",
                "text": "A severe magnitude 6.8 earthquake hit off the coastal region, triggering emergency evacuation orders. First responders and disaster relief medical teams are deployed.",
                "sensitive_tag": "disaster",
                "featured_skus": []
            },
            {
                "timestamp_start": 120.1,
                "timestamp_end": 220.0,
                "speaker": "Correspondent",
                "text": "Authorities report multiple structural damages and emergency hospital admissions. Relief operations are currently underway in affected zones.",
                "sensitive_tag": "tragedy",
                "featured_skus": []
            },
            {
                "timestamp_start": 220.1,
                "timestamp_end": 300.0,
                "speaker": "Anchor",
                "text": "We will remain live with official updates from the Red Cross and government crisis agencies.",
                "sensitive_tag": "medical_emergency",
                "featured_skus": []
            }
        ]
    },
    {
        "video_id": "vid_pro_gaming",
        "title": "Ultimate Desk Setup 2026: OLED Monitors & Custom Keyboards",
        "channel_name": "BattleStation Zurich",
        "creator_id": "creator_battlestation_99",
        "duration": 300.0,
        "category": "Gaming",
        "creator_affiliate_settings": {"default_rate": 0.10, "custom_bonus": 0.02},
        "transcript_cues": [
            {
                "timestamp_start": 0.0,
                "timestamp_end": 45.0,
                "speaker": "Lukas",
                "text": "This is the ultimate gaming setup upgrade for 2026. Centered around the LG 34-inch OLED curved monitor.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-LG-34OLED"]
            },
            {
                "timestamp_start": 45.1,
                "timestamp_end": 110.0,
                "speaker": "Lukas",
                "text": "I'm typing on the Keychron Q1 Pro wireless custom mechanical keyboard with banana tactile switches and Razer DeathAdder V3 Pro mouse.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-KEY-Q1PRO", "SKU-RAZER-DA-V3"]
            },
            {
                "timestamp_start": 110.1,
                "timestamp_end": 190.0,
                "speaker": "Lukas",
                "text": "Audio is handled by the SteelSeries Arctis Nova Pro wireless headset, and I switch scenes using the Elgato Stream Deck MK.2.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-STEEL-NOVAPRO", "SKU-ELG-STREAMDECK"]
            },
            {
                "timestamp_start": 190.1,
                "timestamp_end": 300.0,
                "speaker": "Lukas",
                "text": "To top it off, the Secretlab TITAN Evo chair keeps my posture supported during 8-hour streaming sessions!",
                "sensitive_tag": None,
                "featured_skus": ["SKU-SECRETLAB-EVO"]
            }
        ]
    },
    {
        "video_id": "vid_glass_skin",
        "title": "10-Step K-Beauty Glass Skin Evening Routine",
        "channel_name": "Glow Zurich K-Beauty",
        "creator_id": "creator_glow_zurich_55",
        "duration": 300.0,
        "category": "Beauty",
        "creator_affiliate_settings": {"default_rate": 0.15, "custom_bonus": 0.05},
        "transcript_cues": [
            {
                "timestamp_start": 0.0,
                "timestamp_end": 40.0,
                "speaker": "Chloe",
                "text": "Welcome back beauties! Tonight I'm taking you step-by-step through my nighttime glass skin K-beauty routine.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-ANUA-TONER77"]
            },
            {
                "timestamp_start": 40.1,
                "timestamp_end": 100.0,
                "speaker": "Chloe",
                "text": "First, after double cleansing, I layer the Anua Heartleaf 77% Soothing Toner followed by the COSRX Snail 96 Mucin Power Essence.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-ANUA-TONER77", "SKU-COSRX-SNAIL96"]
            },
            {
                "timestamp_start": 100.1,
                "timestamp_end": 170.0,
                "speaker": "Chloe",
                "text": "Next is Paula's Choice 2% BHA liquid exfoliant to clear out pores, followed by Drunk Elephant Lala Retro Whipped Cream.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-PAULAS-2BHA", "SKU-DRUNK-LALA"]
            },
            {
                "timestamp_start": 170.1,
                "timestamp_end": 230.0,
                "speaker": "Chloe",
                "text": "Before bed, I coat my lips in Laneige Berry Lip Sleeping Mask and apply Sol de Janeiro Bum Bum Cream.",
                "sensitive_tag": None,
                "featured_skus": ["SKU-LANEIGE-LIPMASK", "SKU-SOL-BUMBUM240"]
            },
            {
                "timestamp_start": 230.1,
                "timestamp_end": 300.0,
                "speaker": "Chloe",
                "text": "Wake up with ultra glowing skin! Tap any product on screen to buy directly with instant Google Pay checkout!",
                "sensitive_tag": None,
                "featured_skus": ["SKU-COSRX-SNAIL96", "SKU-BOJ-RELIEFSUN", "SKU-LANEIGE-LIPMASK"]
            }
        ]
    }
]

def init_db(db_path: Path = CATALOG_DB_PATH):
    """Initialize SQLite database schema and seed products and video metadata."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Drop existing tables to ensure clean initialization
    cursor.execute("DROP TABLE IF EXISTS merchant_products")
    cursor.execute("DROP TABLE IF EXISTS video_metadata")
    cursor.execute("DROP TABLE IF EXISTS video_transcripts")

    # Create merchant_products table
    cursor.execute("""
        CREATE TABLE merchant_products (
            sku_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            brand TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'USD',
            in_stock INTEGER NOT NULL DEFAULT 1,
            category TEXT NOT NULL,
            description TEXT,
            specs_json TEXT NOT NULL,
            creator_commission_rate REAL NOT NULL DEFAULT 0.08,
            image_url TEXT
        )
    """)

    # Create video_metadata table
    cursor.execute("""
        CREATE TABLE video_metadata (
            video_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            channel_name TEXT NOT NULL,
            creator_id TEXT NOT NULL,
            duration REAL NOT NULL,
            category TEXT NOT NULL,
            affiliate_settings_json TEXT NOT NULL
        )
    """)

    # Create video_transcripts table
    cursor.execute("""
        CREATE TABLE video_transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            timestamp_start REAL NOT NULL,
            timestamp_end REAL NOT NULL,
            speaker TEXT NOT NULL,
            text TEXT NOT NULL,
            sensitive_tag TEXT,
            featured_skus_json TEXT NOT NULL,
            FOREIGN KEY (video_id) REFERENCES video_metadata (video_id)
        )
    """)

    # Insert Products
    for p in PRODUCTS_DATA:
        cursor.execute("""
            INSERT INTO merchant_products 
            (sku_id, title, brand, price, currency, in_stock, category, description, specs_json, creator_commission_rate, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["sku_id"],
            p["title"],
            p["brand"],
            p["price"],
            p["currency"],
            1 if p["in_stock"] else 0,
            p["category"],
            p["description"],
            json.dumps(p["specs"]),
            p["creator_commission_rate"],
            p["image_url"]
        ))

    # Insert Video Metadata & Transcripts
    for v in VIDEOS_DATA:
        cursor.execute("""
            INSERT INTO video_metadata 
            (video_id, title, channel_name, creator_id, duration, category, affiliate_settings_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            v["video_id"],
            v["title"],
            v["channel_name"],
            v["creator_id"],
            v["duration"],
            v["category"],
            json.dumps(v["creator_affiliate_settings"])
        ))

        for cue in v["transcript_cues"]:
            cursor.execute("""
                INSERT INTO video_transcripts
                (video_id, timestamp_start, timestamp_end, speaker, text, sensitive_tag, featured_skus_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                v["video_id"],
                cue["timestamp_start"],
                cue["timestamp_end"],
                cue["speaker"],
                cue["text"],
                cue["sensitive_tag"],
                json.dumps(cue["featured_skus"])
            ))

    conn.commit()
    conn.close()
    print(f"Catalog DB initialized successfully at {db_path} with {len(PRODUCTS_DATA)} products and {len(VIDEOS_DATA)} videos.")

def export_transcripts_json(json_path: Path = TRANSCRIPTS_JSON_PATH):
    """Export video transcripts data to JSON for offline viewing."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(VIDEOS_DATA, f, indent=2)
    print(f"Transcripts exported to {json_path}")

if __name__ == "__main__":
    init_db()
    export_transcripts_json()
