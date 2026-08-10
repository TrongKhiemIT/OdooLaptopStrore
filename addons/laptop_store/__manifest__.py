{
    "name": "Laptop Store",
    "version": "1.0",
    "category": "Sales",
    "summary": "Quản lý cửa hàng laptop",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/laptop_product_views.xml",
        "views/laptop_sale_order_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
