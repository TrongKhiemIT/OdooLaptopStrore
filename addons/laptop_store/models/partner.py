from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_laptop_customer = fields.Boolean(string="Khách hàng laptop", default=True)
