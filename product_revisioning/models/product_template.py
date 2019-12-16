# -*- coding: utf-8 -*-
from odoo import models, api, exceptions, _
import re


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def create_revision(self):
        self.ensure_one()

        default_code = self.get_next_revision_number(self.default_code)

        # Create a copy of the current product, mark it as active in case the
        # old one was not
        new_product = self.copy({
            'name': self.name,
            'default_code': default_code,
        })
        new_product.active = True

        # Archive the current product
        self.active = False

        view_action = {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_product.id,
            'views': [(False, 'form')],
            'target': 'current',
        }

        return new_product, view_action

    def get_next_revision_number(self, code):
        """
        Get next revision number
        Only supports suffix ending in numbers only
        TODO: make generic purpose
        """
        suffix_re = '[0-9]+$'

        if re.search(suffix_re, code):
            sequence = re.search(suffix_re, code).group()
            new_sequence = str(int(sequence) + 1).zfill(len(sequence))

            return re.sub(suffix_re, new_sequence, code)

        return False

    def action_create_revision(self):
        self.ensure_one()

        if self.product_variant_count > 1:
            msg = _('Revisioning products with variants is not allowed')
            raise exceptions.UserError(msg)

        new_product, view_action = self.create_revision()

        # Find all BOMs that include the current product in the BOM lines
        matching_boms = self.env['mrp.bom'].search(
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

        # Redirect to new product view
        return view_action

    @api.multi
    def action_create_full_revision(self):
        view_action = self.action_create_revision()

        for bom in self.bom_ids:
            reference = self.get_next_revision_number(self.default_code)
            bom.copy({
                'product_tmpl_id': view_action.get('res_id'),
                'code': reference,
                'product_reference': reference,
            })
            bom.active = False

        # Redirect to new product view
        return view_action
