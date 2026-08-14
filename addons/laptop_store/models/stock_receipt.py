from odoo import models, fields
from odoo.exceptions import UserError


class LaptopStockReceipt(models.Model):
    _name = "laptop.stock.receipt"
    _description = "Nhập kho Laptop"

    name = fields.Char(string="Mã đơn nhập", default="/")
    date = fields.Date(string="Ngày nhập", default=fields.Date.today)
    state = fields.Selection(
        [
            ("draft", "Nháp"),
            ("done", "Hoàn thành"),
        ],
        default="draft",
        string="Trạng thái",
    )
    line_ids = fields.One2many(
        "laptop.stock.receipt.line", "receipt_id", string="Chi tiết đơn nhập"
    )

    def action_confirm(self):
        if self.state != "draft":
            raise UserError("Bạn chỉ xác nhận khi còn là nháp")
        else:
            for line in self.line_ids:
                line.product_id.stock_qty += line.qty
            self.state = "done"

    def action_cancel(self):
        if self.state != "done":
            raise UserError("Bạn không thể hủy khi chưa nhập kho")
        else:
            for line in self.line_ids:
                line.product_id.stock_qty -= line.qty
        self.state = "draft"


class LaptopStockReceiptLine(models.Model):
    _name = "laptop.stock.receipt.line"
    _description = "Dòng chi tiết đơn nhập"

    receipt_id = fields.Many2one(
        "laptop.stock.receipt", string="đơn nhập", ondelete="cascade"
    )
    product_id = fields.Many2one("laptop.product", string="Mã sản phẩm", required=True)
    qty = fields.Integer(string="Số lượng", default=1)
