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

    qty_to_manufacture = fields.Float(
        string="Manufacturable quantity",
        compute="_compute_material_requirement_line",
        readonly=True,
    )

    qty_available = fields.Float(
        string="On Hand",
        readonly=True,
        compute="_compute_material_requirement_line",
    )

    qty_promised = fields.Float(
        string="Potential quantity",
        readonly=True,
        compute="_compute_material_requirement_line",
    )

    bom = fields.Many2one(comodel_name="mrp.bom", string="BOM")

    material_requirement_line = fields.One2many(
        "material.requirement.line",
        "material_requirement_id",
        string="Material Requirement Line",
        readonly=False,
    )

    product_variants = fields.Many2one(
        comodel_name="product.product",
        string="Product Variant",
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
        self._compute_material_requirement_line()

    def create_requirement_lines(self, vals, rec):
        """Create Requirement Lines using BoM values"""

        attributes = vals.bom_product_template_attribute_value_ids.mapped(
            "display_name"
        )

        attributes = attributes and ", ".join(attributes) or ""

        if attributes.startswith("u'"):
            attributes = attributes.replace("u'", "'", 1)

        multiplier = 0
        smallest_multiplier = []
        product_bom = []
        qtys = []
        ch_smallest = 0

        if vals.product_id.bom_ids:
            for bom in vals.product_id.bom_ids:
                product_bom.append(bom)

            lines = vals.product_id.bom_ids[0].bom_line_ids

            for line in lines:
                ch_smallest, qtys = self.get_smallest_multiplier(rec, line, qtys)

                line_avail_qty = line.product_id.qty_available

                multiplier = (
                    int((line_avail_qty + ch_smallest) / line.product_qty)
                    if (line_avail_qty > 0 and line.product_qty)
                    else 0
                )

                smallest_multiplier.append(multiplier)
                multiplier = smallest_multiplier and min(smallest_multiplier) or 0

        product_bom = product_bom and product_bom[0].id or False

        if not self.manufacturing_level:
            multiplier = 0

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

    def get_smallest_multiplier(self, requir, line, multiplier_qtys):
        min_qty = 0
        if requir.manufacturing_level == "level_two" and line.product_id.bom_ids:
            child_lines = line.product_id.bom_ids[0].bom_line_ids

            for child_line in child_lines:
                avail_qty = child_line.product_id.qty_available

                qty = int(avail_qty / child_line.product_qty) if avail_qty > 0 else 0

                multiplier_qtys.append(qty)

            min_qty = multiplier_qtys and min(multiplier_qtys) or 0
        return min_qty, multiplier_qtys

    @api.onchange(
        "product",
        "product_variants",
        "manufacturing_level",
        "bom",
    )
    def _compute_material_requirement_line(self):
        """ "Get Material requirement line"""
        mrp_bom = self.env["mrp.bom"]
        for rec in self:
            if not rec.product and not rec.product_variants:
                continue
            # limit=1 by defauly on _bom_find() function
            bom_id = rec.bom or mrp_bom._bom_find(
                product_tmpl=rec.product, product=rec.product_variants
            )

            material_line = self.env["material.requirement.line"]
            smallest_multiplier = []
            qtys = []
            ch_smallest = 0

            for line in bom_id.bom_line_ids:
                smallest_multiplier_line = []
                if all(
                    elem in rec.product_variants.product_template_attribute_value_ids
                    for elem in line.bom_product_template_attribute_value_ids
                ):
                    line_values = rec.create_requirement_lines(line, rec)
                    material_line += material_line.create(line_values)

                    if (
                        rec.manufacturing_level in ["level_one", "level_two"]
                        and line.product_id.bom_ids
                    ):
                        for child_line in line.product_id.bom_ids[0].bom_line_ids:
                            ch_smallest, qtys = self.get_smallest_multiplier(
                                rec, child_line, qtys
                            )

                            ch_avail_qty = child_line.product_id.qty_available
                            if (
                                ch_avail_qty + ch_smallest <= 0
                                or not child_line.product_qty
                            ):
                                multiplier_line = 0
                            else:
                                multiplier_line = int(
                                    (ch_avail_qty + ch_smallest)
                                    / child_line.product_qty
                                )

                            smallest_multiplier_line.append(multiplier_line)

                    multiplier_line = (
                        smallest_multiplier_line and min(smallest_multiplier_line) or 0
                    )

                    multiplier = (
                        line.product_qty
                        and int(
                            (line.product_id.qty_available + multiplier_line)
                            / line.product_qty
                        )
                        or 0
                    )

                    smallest_multiplier.append(multiplier)

            smallest = smallest_multiplier and min(smallest_multiplier) or 0

            rec.bom = rec.bom or bom_id
            rec.qty_to_manufacture = smallest
            rec.qty_available = rec.product.qty_available
            rec.qty_promised = rec.qty_available + rec.qty_to_manufacture
            rec.material_requirement_line = [(6, 0, material_line.ids)]

    def compute_lines(self):
        self._compute_material_requirement_line()
