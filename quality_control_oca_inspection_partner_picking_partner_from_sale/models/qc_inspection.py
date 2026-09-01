from odoo import api, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _get_object_partner(self):
        """Prefer the picking's sale-order customer (then the picking's own
        partner) for inspections that reference a stock move or picking.

        ``picking_id`` is provided by ``quality_control_stock_oca`` and is set
        for both ``stock.move`` and ``stock.picking`` references.
        """
        self.ensure_one()
        picking = self.picking_id
        if picking:
            partner = picking.sale_id.partner_id or picking.partner_id
            if partner:
                return partner[:1]
        return super()._get_object_partner()

    @api.depends(
        "object_id",
        "picking_id",
        "picking_id.sale_id",
        "picking_id.sale_id.partner_id",
        "picking_id.partner_id",
    )
    def _compute_partner_id(self):
        return super()._compute_partner_id()
