from __future__ import division
from odoo import api, fields, models


class MaterialRequirement(models.Model):
    _name = "material.requirement"
    _description = "Material Requirement"

    note = fields.Text(string="Notes")

    name = fields.Char(string="Name")

    manufacturing_level = fields.Selection(
        [("level_one", "Level 3"), ("level_two", "Level 4")],
        string="Choose BOM level",
        help="""Level 3 - Components' BOMs are included in the calculations
               Level 4 - Components' BOMs components' BOMs are included""",
    )

    product = fields.Many2one(
        comodel_name="product.template",
        string="Product",
        domain=[("bom_ids", "!=", False)],
    )

    product_attribute_name = fields.Char(string="Product Attributes",)

    product_variant_id = fields.Integer(
        string="Product Variant ID", compute="_compute_product_variant_id",
    )

    requirement = fields.Float(string="Requirement",)

    qty_to_manufacture = fields.Float(
        string="Manufacturable quantity",
        compute="_compute_material_requirement_line",
        readonly=True,
    )

    qty_available = fields.Float(
        string="On Hand", readonly=True, compute="_compute_material_requirement_line",
    )

    qty_promised = fields.Float(
        string="Potential quantity",
        readonly=True,
        compute="_compute_material_requirement_line",
    )

    bom = fields.Many2one(comodel_name="mrp.bom", string="BOM")

    bom_lines = fields.Many2many(comodel_name="mrp.bom.line", string="BoM lines",)

    bom_prod = fields.Integer(string="BOM Prod",)

    bom_product = fields.Char(string="BoM Product",)

    material_requirement_line = fields.One2many(
        "material.requirement.line",
        "material_requirement_id",
        string="Material Requirement Line",
        readonly=False,
    )

    product_variants = fields.Many2one(
        comodel_name="product.product", string="Product Variant",
    )

    @api.model
    def create(self, vals):
        """Assign next sequence"""
        vals["name"] = self.env["ir.sequence"].next_by_code("material.requirement")

        res = super(MaterialRequirement, self).create(vals)
        return res

    @api.onchange("product")
    def get_product_variants(self):
        """Get selected product's variants"""
        for record in self:
            if record.product:
                variants = record.product.product_variant_id
                for variant in variants:
                    record.product_variants = variant
                    record.product_variant_id = variant.id
        self._compute_material_requirement_line()

    @api.onchange("product_variants")
    def _compute_product_variant_id(self):
        """Get product variant id"""
        for record in self:
            record.product_variant_id = record.product_variants.id

    def create_requirement_lines(self, vals):
        """Create Requirement Lines using BoM values"""
        values = []

        for i in vals.attribute_value_ids:
            values.append(i.display_name)

        attributes = vals.attribute_value_ids.mapped("display_name")

        if not attributes:
            attributes = ""
        else:
            attributes = ", ".join(attributes)

        if attributes.startswith("u'"):
            attributes = attributes.replace("u'", "'", 1)

        multiplier = 0
        smallest_multiplier = []
        product_bom = []
        ch_multiplier_line = []
        ch_smallest = 0

        if vals.product_id.bom_ids:
            for bom in vals.product_id.bom_ids:
                product_bom.append(bom)

            lines = vals.product_id.bom_ids[0].bom_line_ids

            for line in lines:
                if self.manufacturing_level == "level_two" and line.product_id.bom_ids:
                    for ch_child_bom_line in line.product_id.bom_ids[0].bom_line_ids:
                        if ch_child_bom_line.product_id.qty_available <= 0:
                            ch_line = 0
                        else:
                            ch_line = int(
                                ch_child_bom_line.product_id.qty_available
                                / ch_child_bom_line.product_qty
                            )
                        ch_multiplier_line.append(ch_line)

                    if not ch_multiplier_line:
                        ch_smallest = 0
                    else:
                        ch_smallest = min(ch_multiplier_line)

                if line.product_id.qty_available <= 0:
                    multiplier = 0
                else:
                    multiplier = int(
                        (line.product_id.qty_available + ch_smallest) / line.product_qty
                    )

                smallest_multiplier.append(multiplier)

                if not smallest_multiplier:
                    multiplier = 0
                else:
                    multiplier = min(smallest_multiplier)
        else:
            product_bom = ""

        if not self.manufacturing_level:
            multiplier = 0

        product_bom = product_bom and product_bom[0] or False

        result = {
            "product_id": vals.product_id.id,
            "product_availability": vals.product_id.qty_available,
            "variant": attributes,
            "qty_to_manufacture": vals.product_qty,
            "product_uom_id": vals.product_id.uom_id.name,
            "can_be_manufactured": multiplier,
            "promised_qty_line": multiplier + vals.product_id.qty_available,
            "bom": product_bom,
        }

        return result

    @api.onchange(
        "product",
        "product_variants",
        "manufacturing_level",
        "material_requirement_line",
    )
    def _compute_material_requirement_line(self):
        """"Get Material requirement line"""
        mrp_bom = self.env["mrp.bom"]
        for rec in self:
            bom_id = mrp_bom.search(
                [
                    "&",
                    ("product_tmpl_id.id", "=", rec.product.id),
                    "|",
                    ("product_id", "=", rec.product_variant_id),
                    ("product_id", "=", False),
                ],
                limit=1,
            )

            material = self.env["material.requirement.line"]
            product_material_lines = []
            smallest_multiplier = []
            ch_multiplier_line = []
            ch_smallest = 0

            for line in bom_id.bom_line_ids:
                smallest_multiplier_line = []
                if all(
                    elem in rec.product_variants.attribute_value_ids.ids
                    for elem in line.attribute_value_ids.ids
                ):
                    product_material_lines.append(
                        material.new(rec.create_requirement_lines(line)).id
                    )
                    if (
                        rec.manufacturing_level in ["level_one", "level_two"]
                        and line.product_id.bom_ids
                    ):
                        for child_bom_line in line.product_id.bom_ids[0].bom_line_ids:
                            if (
                                rec.manufacturing_level == "level_two"
                                and child_bom_line.product_id.bom_ids
                            ):
                                for (
                                    ch_child_bom_line
                                ) in child_bom_line.product_id.bom_ids[0].bom_line_ids:
                                    if ch_child_bom_line.product_id.qty_available <= 0:
                                        ch_line = 0
                                    else:
                                        ch_line = int(
                                            ch_child_bom_line.product_id.qty_available
                                            / ch_child_bom_line.product_qty
                                        )
                                    ch_multiplier_line.append(ch_line)

                                if not ch_multiplier_line:
                                    ch_smallest = 0
                                else:
                                    ch_smallest = min(ch_multiplier_line)

                            if (
                                child_bom_line.product_id.qty_available + ch_smallest
                            ) <= 0:
                                multiplier_line = 0
                            else:
                                multiplier_line = int(
                                    (
                                        child_bom_line.product_id.qty_available
                                        + ch_smallest
                                    )
                                    / child_bom_line.product_qty
                                )
                            smallest_multiplier_line.append(multiplier_line)

                    if not smallest_multiplier_line:
                        multiplier_line = 0
                    else:
                        multiplier_line = min(smallest_multiplier_line)

                    if line.product_id.qty_available <= 0:
                        multiplier = 0
                    else:
                        multiplier = int(
                            (line.product_id.qty_available + multiplier_line)
                            / line.product_qty
                        )
                    smallest_multiplier.append(multiplier)

            if not smallest_multiplier:
                smallest = 0
            else:
                smallest = min(smallest_multiplier)

            rec.qty_to_manufacture = smallest
            rec.qty_available = rec.product.qty_available
            rec.qty_promised = rec.qty_available + rec.qty_to_manufacture
            rec.material_requirement_line = [(6, 0, product_material_lines)]

    def compute_lines(self):
        self._compute_material_requirement_line()

    @api.onchange(
        "product_variants",
        "product",
        "manufacturing_level",
        "material_requirement_line",
    )
    def get_bom(self):
        """When a product is selected, get that product's BoM"""
        mrp_bom = self.env["mrp.bom"]
        for record in self:
            product = self.env["product.template"].search(
                [("id", "=", int(record.product))]
            )

            bom_id = mrp_bom.search(
                [
                    "&",
                    ("product_tmpl_id.id", "=", record.product.id),
                    "|",
                    ("product_id", "=", record.product_variant_id),
                    ("product_id", "=", False),
                ],
                limit=1,
            )

            bom_id_2 = mrp_bom.search(
                [
                    "&",
                    ("product_tmpl_id.id", "=", record.product.id),
                    "|",
                    ("product_id", "=", record.product_variant_id),
                    ("product_id", "=", False),
                ]
            )

            prod = self.env["product.product"].search(
                [("id", "=", int(record.product_variants))]
            )

            attribute = prod.attribute_value_ids
            record.bom_prod = product.id

            for bom_record in bom_id_2:
                for line in bom_record.bom_line_ids:
                    if line.attribute_value_ids == attribute:
                        record.bom = bom_record.id
                        record.bom_lines = bom_record.bom_line_ids
                        return

            record.bom = bom_id.id
            record.bom_lines = bom_id.bom_line_ids
