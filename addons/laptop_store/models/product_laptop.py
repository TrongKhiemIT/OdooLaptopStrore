from odoo import models, fields


class ProductLaptop(models.Model):
    _name = "laptop.product"
    _description = "Laptop"

    name = fields.Char(string="Tên laptop", required=True)
    brand = fields.Char(string="Hãng")
    price = fields.Float(string="Giá bán")
    stock_qty = fields.Interger(string="Số lượng tồn kho")
    description = fields.Text(string="Mô tả")
