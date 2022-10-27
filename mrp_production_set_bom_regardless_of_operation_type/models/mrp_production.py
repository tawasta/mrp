from odoo import api, models


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    @api.onchange("product_id", "picking_type_id", "company_id")
    def onchange_product_id(self):
        super().onchange_product_id()
        if not self.product_id:
            self.bom_id = False
        elif (
            not self.bom_id
            or self.bom_id.product_tmpl_id != self.product_tmpl_id
            or (self.bom_id.product_id and self.bom_id.product_id != self.product_id)
        ):
            bom = self.env["mrp.bom"]._bom_find(
                product=self.product_id,
                company_id=self.company_id.id,
                bom_type="normal",
            )
            if bom:
                self.bom_id = bom.id
                self.product_qty = self.bom_id.product_qty
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id
