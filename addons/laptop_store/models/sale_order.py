from odoo import models, fields, api


@api.depends("line_ids.subtotal")
def _compute_total(self):
    for order in self:
        order.total = sum(order.line_ids.mapped("subtotal"))


class LaptopSaleOrder(models.Model):
    _name = "laptop.sale.order"
    _description = "Đơn bán Laptop"

    name = fields.Char(string="Mã đơn", required=True, default="/")
    customer_id = fields.Many2one("res.partner", string="Khách hàng", required=True)
    date = fields.Date(string="Ngày bán", default=fields.Date.today)
    state = fields.Selection(
        [
            ("draft", "Nháp"),
            ("confirmed", "Xác nhận"),
            ("done", "Hoàn thành"),
        ],
        string="Trạng thái",
        default="draft",
    )
    line_ids = fields.One2many(
        "laptop.sale.order.line", "order_id", string="Chi tiết đơn"
    )
    total = fields.Float(string="Tổng tiền", compute="_compute_total")

    @api.depends("line_ids.subtotal")
    def _compute_total(self):
        for order in self:
            order.total = sum(order.line_ids.mapped("subtotal"))


class LaptopSaleOrderLine(models.Model):
    _name = "laptop.sale.order.line"
    _description = "Dòng chi tiết đơn bán"

    order_id = fields.Many2one(
        "laptop.sale.order", string="Đơn bán", ondelete="cascade"
    )
    product_id = fields.Many2one("laptop.product", string="Laptop", required=True)
    qty = fields.Integer(string="Số lượng", default=1)
    unit_price = fields.Float(string="Đơn giá")
    subtotal = fields.Float(string="Thành tiền", compute="_compute_subtotal")

    @api.depends("qty", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.unit_price
