from odoo import fields, models, sys


class MrpMove(models.Model):
    _inherit = "mrp.move"

    customer_name = fields.Text("Customer", store=True, compute="_customer_name_compute")

    def _customer_name_compute(self):
        for record in self:
            if record.mrp_order_number:
                sale_order = record.env['sale.order'].search([('name', '=', record.mrp_order_number)])
                record.customer_name = sale_order.partner_id.name
            else:
                record.customer_name = ""
