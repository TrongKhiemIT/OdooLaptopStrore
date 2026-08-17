{
    "name": "Laptop Store",
    "version": "1.0",
    "category": "Sales",
    "summary": "Quản lý cửa hàng laptop",
    "depends": ["base", "mail"],
    "data": [
        "security/laptop_security.xml",
        "security/ir.model.access.csv",
        "views/laptop_product_views.xml",
        "views/laptop_sale_order_views.xml",
        "reports/laptop_sale_order_report.xml",
        "reports/laptop_sale_order_email.xml",
        "views/laptop_stock_receipt_views.xml",
        "views/laptop_dashboard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "laptop_store/static/src/js/laptop_stock_badge.js",
            "laptop_store/static/src/xml/laptop_stock_badge.xml",
            "laptop_store/static/src/js/laptop_dashboard.js",
            "laptop_store/static/src/xml/laptop_dashboard.xml",
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
