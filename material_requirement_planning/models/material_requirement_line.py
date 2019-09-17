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

    product_availability = fields.Char(
            string='Available quantity',
            readonly=False,
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
            string="Quantity to Manufacture",
            readonly=False,
            )

#     bom = fields.Many2one(
#             'mrp.bom',
#             string='BoM',
#             readonly=False,
#             )

    bom = fields.Char(string="BoM")

#     bom = fields.Selection(
#             string="BoM",
#             )

    bom_lines = fields.Many2many(
            comodel_name='mrp.bom.line',
            string='BoM lines',
            readonly=False,
            )
