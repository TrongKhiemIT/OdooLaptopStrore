from odoo import models, fields, api
from odoo.exceptions import UserError


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

    def action_send_email(self):
        template = self.env.ref("laptop_store.email_template_laptop_sale_order")
        for order in self:
            template.send_mail(order.id, force_send=True)
        return True

    def action_print_report(self):
        return self.env.ref("laptop_store.report_laptop_sale_order").report_action(self)

    @api.depends("line_ids.subtotal")
    def _compute_total(self):
        for order in self:
            order.total = sum(order.line_ids.mapped("subtotal"))

    def action_confirm(self):
        if self.state != "draft":
            raise UserError("Chỉ được xác nhận đơn đang ở trạng thái Nháp.")
        for line in self.line_ids:
            if line.qty > line.product_id.stock_qty:
                raise UserError(f"Không đủ hàng cho Laptop {line.product_id.name}")
            else:
                line.product_id.stock_qty -= line.qty
        self.state = "confirmed"

    def action_done(self):
        self.state = "done"

    def action_cancel(self):
        if self.state == "confirmed" or self.state == "done":
            for line in self.line_ids:
                line.product_id.stock_qty += line.qty
                self.state = "draft"


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
