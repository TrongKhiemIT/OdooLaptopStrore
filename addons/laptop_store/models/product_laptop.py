from odoo import models, fields


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
