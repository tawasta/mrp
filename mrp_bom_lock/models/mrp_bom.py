# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class MrpBom(models.Model):

    _inherit = "mrp.bom"

    locked = fields.Boolean(
        string='BOM locked',
        related='product_tmpl_id.bom_locked',
        help='This BOM is locked',
    )

    parent_locked = fields.Boolean(
        string='Parent BOM locked',
        help='A parent BOM locked',
        compute='compute_parent_locked',
    )

    parent_locked_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='Locked parent BOM',
        readonly=True,
    )

    def compute_parent_locked(self):
        """ Checks if given BOM or any of it's parent BOM's have
            their bom locked.

            Returns tuple with locked boolean and locked template record.
            This can be called from anywhere with a BOM record
        """

        for record in self:
            # The BOM itself is locked, no need to continue
            if record.locked:
                record.parent_locked
                record.parent_locked_id = record.id
                return

            # Get all variants for current product template
            product_ids = record.product_tmpl_id.product_variant_ids.ids

            # Search for any bom lines using current product variants
            line_ids = record.env["mrp.bom.line"].search(
                [("product_id", "in", product_ids)]
            )

            for line in line_ids:
                # Check if any parent BOMs are locked
                if line.bom_id.locked:
                    record.parent_locked = True
                    record.parent_locked_id = line.bom_id.id
                elif line.bom_id.parent_locked:
                    record.parent_locked = True
                    record.parent_locked_id = line.bom_id.parent_locked_id.id

    def display_locked_error(self):
        bom = self.parent_locked_id or self

        message = "BOM is locked for product: %s" % \
                  bom.product_tmpl_id.display_name
        raise UserError(message)

    @api.multi
    def write(self, values):
        """ Write triggers a locked check for current BOM """
        if not self.env["res.users"].\
                has_group("bom_lock.bom_lock_allow_write"):
            for bom in self:
                if bom.locked or bom.parent_locked:
                    self.display_locked_error()

        return super(MrpBom, self).write(values)
