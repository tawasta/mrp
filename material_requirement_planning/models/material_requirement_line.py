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
            string='Potential quantity',
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
            string="Component quantity",
            readonly=False,
            )

    can_be_manufactured = fields.Float(
            string="Manufacturable quantity",
            readonly=False,
            )

    bom = fields.Many2one(
            comodel_name='mrp.bom',
            string="BoM",
            )

    bom_lines = fields.Many2many(
            comodel_name='mrp.bom.line',
            string='BoM lines',
            readonly=False,
            )
