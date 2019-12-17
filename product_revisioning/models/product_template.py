# -*- coding: utf-8 -*-
from odoo import models, api, exceptions, _
import re


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def create_revision(self):
        """
        Create new revision. Not implemented on products with variants

        1. Try to get new revision number by product suffix
        2. Duplicate product
        3. Deactivate old product
        """

        self.ensure_one()

        if self.product_variant_count > 1:
            msg = _('Revisioning products with variants is not allowed')
            raise exceptions.UserError(msg)

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

        e.g.
        - PR-123 becomes PR-124
        - P456 becomes P457
        """
        if not code:
            return False

        suffix_re = '[0-9]+$'

        if re.search(suffix_re, code):
            sequence = re.search(suffix_re, code).group()
            new_sequence = str(int(sequence) + 1).zfill(len(sequence))

            return re.sub(suffix_re, new_sequence, code)

        return False

    def action_create_revision(self):
        """
        Create a product revision

        This is very similiar to default "duplicate/copy"-function, but
        it will not generate new default code by sequence, and will
        use the old product name (and won't add (copy) to the end)
        """
        new_product, view_action = self.create_revision()

        # Redirect to new product view
        return view_action

    @api.multi
    def action_create_full_revision(self):
        """
        Create a product revision and update BoMs

        1. Create a new product revision
        2. Search BoMs using the old product
        3. Make new BoM revisions for BoMs using the old product
        4. Search for old product BoM(s)
        5. Create new BoM(s) for new product using the old BoM revision
        """

        old_product_id = self.product_variant_id

        # Create a new product revision
        new_product, view_action = self.create_revision()

        # 2. Search BoMs using the old product in BoM lines
        domain = [
            ('bom_line_ids.product_id', '=', old_product_id.id)
        ]
        matching_boms = self.env['mrp.bom'].search(domain)

        # 3. Make new BoM revisions for BoMs using the old product
        for bom_to_copy in matching_boms:
            reference = self.get_next_revision_number(bom_to_copy.code)
            new_bom = bom_to_copy.copy({
                'code': reference,
                'product_reference': reference,
            })
            bom_to_copy.active = False

            # Replace any BoM lines using the old product, with new product
            for new_bom_line in new_bom.bom_line_ids:
                if new_bom_line.product_id == old_product_id:
                    new_bom_line.product_id = new_product.product_variant_id.id

        # 4. Search for old product BoM(s)
        for bom in self.bom_ids:
            # 5. Create new BoM(s) for new product using the old BoM revision
            reference = self.get_next_revision_number(bom.code)
            bom.copy({
                'product_tmpl_id': view_action.get('res_id'),
                'code': reference,
                'product_reference': reference,
            })
            bom.active = False

        # Redirect to new product view
        return view_action
