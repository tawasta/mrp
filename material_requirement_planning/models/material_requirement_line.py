
from __future__ import division
from odoo import fields, models


class MaterialRequirementLine(models.Model):

    _name = "material.requirement.line"
    _description = "Material Requirement Line"

    bom = fields.Many2one(
        comodel_name="mrp.bom",
        string="BoM",
        readonly=True,
    )

    bom_lines = fields.Many2many(
        comodel_name="mrp.bom.line",
        string="BoM lines",
        readonly=True,
    )

    can_be_manufactured = fields.Float(
        string="Manufacturable quantity",
        readonly=True,
    )

    cost = fields.Float(
        related="product_id.standard_price"
    )

    incoming = fields.Integer(
        string="Incoming Qty",
        compute="_compute_transfer_counts"
    )

    outgoing = fields.Integer(
        string="Outgoing Qty",
        compute="_compute_transfer_counts"
    )

    material_requirement_id = fields.Many2one(
        "material.requirement",
        string="Material Requirement",
        readonly=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        store=True,
        readonly=True,
    )

    product_availability = fields.Float(
        string="On Hand",
        readonly=True,
    )

    product_uom_id = fields.Char(
        related="product_id.uom_name",
        string="Product Unit of Measure",
    )

    promised_qty_line = fields.Char(
        string="Potential quantity",
        readonly=True,
    )

    qty_to_manufacture = fields.Float(
        string="Qty used in BOM",
        readonly=True,
    )

    variant = fields.Char(
        string="Variant",
        readonly=True,
    )

    vendor = fields.Char(
        string="Preferred supplier",
        compute="_compute_preferred_supplier",
    )

    def _compute_preferred_supplier(self):
        for line in self:
            if line.product_id.seller_ids:
                line.vendor = line.product_id.seller_ids[0].name.name

    def _compute_transfer_counts(self):
        for line in self:
            stock_moves = self.env['stock.move'].search([
                ('product_id', '=', line.product_id.id),
                ('picking_id.state', 'in', ['confirmed', 'assigned'])
            ])
            line.incoming = sum(
                [x.reserved_availability for x in stock_moves
                 if x.purchase_line_id]
            )
            line.outgoing = sum(
                [x.reserved_availability for x in stock_moves
                 if x.sale_line_id]
            )
