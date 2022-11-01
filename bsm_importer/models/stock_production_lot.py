from odoo import fields, models


class StockProductionLot(models.Model):
    _name = "stock.production.lot"
    _inherit = "stock.production.lot"

    bsm_ids = fields.Many2many(
        "bsm.data", "bsm_data_rel", "bsm_id", "prodlot_id", "BSM Serials"
    )

    def write(self, vals):
        res = super(StockProductionLot, self).write(vals)

        for record in self:
            for bsm in record.bsm_ids:
                bsm.write({"bsm_used": True, "bsm_prodlot_id": record.id})

        return res
