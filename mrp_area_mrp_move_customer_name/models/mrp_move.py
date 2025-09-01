from odoo import fields, models, sys, _


class MrpMove(models.Model):
    _inherit = "mrp.move"

    customer = _("Customer")

    customer_name = fields.Text(customer, store=True, compute="_customer_name_compute")

    def _customer_name_compute(self):
        for record in self:
            if record.mrp_order_number:
                sale_order = record.env['sale.order'].search([('name', '=', record.mrp_order_number)])
                record.customer_name = sale_order.partner_id.name
            elif record.origin:
                sale_order = record.env['sale.order'].search([('name', '=', record.origin)])
                record.customer_name = sale_order.partner_id.name
            else:
                record.customer_name = ""
