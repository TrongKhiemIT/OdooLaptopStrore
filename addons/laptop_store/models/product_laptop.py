from odoo import models, fields, api


class ProductLaptop(models.Model):
    _name = "laptop.product"
    _description = "Laptop"

    name = fields.Char(string="Tên laptop", required=True)
    brand = fields.Char(string="Hãng")
    price = fields.Float(string="Giá bán")
    stock_qty = fields.Integer(string="Số lượng tồn kho")
    description = fields.Text(string="Mô tả")
    cost_price = fields.Float(
        string="Giá vốn", groups="laptop_store.group_laptop_store_manager"
    )

    @api.model
    def get_dashboard_data(self):
        products = self.search([])
        orders = self.env["laptop.sale.order"].search(
            [("state", "in", ["confirmed", "done"])]
        )
        qty_sold = sum(orders.line_ids.mapped("qty"))
        revenue = sum(orders.mapped("total"))
        return {
            "product_count": len(products),
            "total_stock": sum(products.mapped("stock_qty")),
            "stock_value": sum(p.stock_qty * p.price for p in products),
            "qty_sold": qty_sold,
            "order_count": len(orders),
            "revenue": revenue,
        }
