from odoo import api, fields, models


class BomStructureXlsxWizard(models.TransientModel):

    _name = "bom.structure.xlsx.wizard"

    product_id = fields.Many2one(
        "product.product",
        string="Product Variant",
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
    )
    product_tmpl_id = fields.Many2one("product.template", "Product", readonly=True)
    multi_print = fields.Boolean("Multi print")

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        boms = self._context.get("active_ids")
        if len(boms) > 1 or 0:
            vals["product_tmpl_id"] = False
            vals["multi_print"] = True
        else:
            bom = self.env["mrp.bom"].browse(self._context.get("active_ids"))
            template = bom.product_tmpl_id
            vals["product_tmpl_id"] = template.id
            vals["multi_print"] = False
        return vals

    def print_boms(self):
        boms = self.env["mrp.bom"].browse(self._context.get("active_ids"))
        close_window = {"type": "ir.actions.act_window_close"}
        res = False

        if boms:
            res = (
                self.env.ref(
                    "mrp_bom_structure_xlsx_recursive.bom_structures_recursive"
                )
                .with_context(
                    multi_print=self.multi_print,
                    product_tmpl_id=self.product_tmpl_id,
                    product_id=self.product_id.id,
                )
                .report_action(boms)
            )

        return {
            "type": "ir.actions.act_multi",
            "actions": [res, close_window],
        }
