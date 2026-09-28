from odoo import api, fields, models


class MrpRoutingWorkcenter(models.Model):
    # Operation model
    _inherit = "mrp.routing.workcenter"

    purchase_product_id = fields.Many2one(
        "product.product", string="Product to purchase"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            purchase_product_id = vals.get("purchase_product_id", False)
            if not purchase_product_id:
                workcenter_id = vals.get("workcenter_id", False)
                if workcenter_id:
                    workcenter = self.env["mrp.workcenter"].browse(workcenter_id)
                    default_purchase_product_id = (
                        workcenter and workcenter.default_purchase_product_id or False
                    )
                    if default_purchase_product_id:
                        vals["purchase_product_id"] = default_purchase_product_id.id
        return super().create(vals_list)
