from odoo import models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _get_default_inspection_email_recipients(self):
        partners = super()._get_default_inspection_email_recipients()
        sale = self.picking_id.sale_id
        if sale and sale.partner_id:
            partners |= sale.partner_id
        return partners
