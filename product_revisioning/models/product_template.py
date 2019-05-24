from odoo import models, api, _, exceptions


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def create_revision(self):
        self.ensure_one()

        if self.bom_count > 0:
            msg = _('Revisioning products with BOMs is not allowed')
            raise exceptions.UserError(msg)
        if self.product_variant_count > 1:
            msg = _('Revisioning products with variants is not allowed')
            raise exceptions.UserError(msg)

        bom_model = self.env['mrp.bom']

        # Create a copy of the current product, mark it as active in case the
        # old one was not
        new_product = self.copy()
        new_product.active = True

        # Find all BOMs that include the current product in the BOM lines
        matching_boms = bom_model.search(
            args=[('bom_line_ids.product_id', '=', self.product_variant_id.id)]
        )

        # Set all BOMs inactive one by one, and create replacement BOMs.
        # Go through the BOM lines and replace the old product with the new
        for bom_to_copy in matching_boms:
            new_bom = bom_to_copy.copy()
            bom_to_copy.active = False

            for new_bom_line in new_bom.bom_line_ids:
                if new_bom_line.product_id == self.product_variant_id:
                    new_bom_line.product_id = new_product.product_variant_id.id

        # Archive the current product and redirect to the new product's
        # form view
        self.active = False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_product.id,
            'views': [(False, 'form')],
            'target': 'current',
        }
