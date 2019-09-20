# -*- cofing: utf-8 -*-


from __future__ import division
from odoo import api, fields, models


class MaterialRequirementLine(models.Model):

    _name = 'material.requirement.line'
    _description = 'Material Requirement Line'

    product_id = fields.Many2one(
            'product.product',
            string='Product',
            store=True,
            readonly=False,
            )

    product_availability = fields.Float(
            string='Available quantity',
            readonly=False,
            )

    product_uom_id = fields.Many2one(
            'product.uom',
            'Product Unit of Measure',
            )

    promised_qty_line = fields.Char(
#             string='Promised Quantity',
            )

    variant = fields.Char(
            string='Variant',
            )

    material_requirement_id = fields.Many2one(
            'material.requirement',
            string='Material Requirement',
            readonly=False,
            )

    qty_to_manufacture = fields.Float(
            string="Product Quantity",
            readonly=False,
            )

#     manufacturing_level_line = fields.Char(
# #             _compute='_get_manufacturing_level',
#             related='material_requirement_id.manufacturing_level.name'
#             )


    manufacturing_level_line = fields.Boolean(
#             _compute='_get_manufacturing_level',
            related='material_requirement_id.manufacturing_level'
            )

#     manufacturing_level_line = fields.Selection(
# #             _compute='_get_manufacturing_level',
#             related='material_requirement_id.manufacturing_level'
#             )

    can_be_manufactured = fields.Float(
            string="Quantity to Manufacture",
            readonly=False,
            )

#     bom = fields.Many2one(
#             'mrp.bom',
#             string='BoM',
#             readonly=False,
#             )

    bom = fields.Char(string="BoM")

    bom_lines = fields.Many2many(
            comodel_name='mrp.bom.line',
            string='BoM lines',
            readonly=False,
            )

#     @api.multi
#     def _get_manufacturing_level(self):
#         print "SELF MANUFACTUGIN LEVEL: ", self.manufacturing_level
#         self.manufacturing_level = self.material_requirement_id.manufacturing_level
#
