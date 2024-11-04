import math
from collections import defaultdict

from odoo import _, fields, models


class ReportMrpBomStructureXlsxRecursiveStructure(models.AbstractModel):

    _name = "report.mrp_bom_structure_xlsx.recursive_structure"
    _description = "BOM Structure XLSX Report recursive"
    _inherit = "report.mrp_bom_structure_xlsx.bom_structure_xlsx"

    product_id = fields.Many2one("product.product", string="Product Variant")
    product_tmpl_id = fields.Many2one("product.template", "Product")
    multi_print = fields.Boolean("Multi print")

    def get_sub_lines(self, current_bom, bom_factor, original_bom_lines, identifier):
        """ The purpose of this function is to gather quantities from BoM lines
        and multiply them by their parent BoMs quantities. The identifier-parameter
        is used to precisely mark which route the BoM line is reached. That way the
        quantities will not be confused with each other. For example BoM A and its
        lines B and X. Then the BoM B and its lines X and Y:

                     A
                    / \
                   B   X
                  / \
                 X   Y

        Their X lines will get different identifiers. If the main BoM A has id of 1
        and B's line id is 2 and X's line id is 3 and Y's line id is 4, then their
        identifiers would be
        B: 100002
        X: 100003
        X: 10000200003
        Y: 10000200004
        These same values are used on the print_bom_children-function to assign
        quantities.
        """

        lines = []

        for bom_line in current_bom.bom_line_ids:

            ident = "{}{}{}".format(identifier, "0000", bom_line.id)

            # TODO: Create a condition to check if parent BoM contains
            # BoMs that are the same as the parent BoM. The commented
            # code below does not work.
            # if current_bom.id == bom_line.child_bom_id.id:
            #     msg = _("A BoM should not have a child BoM which is the same "
            #             "as the parent BoM. Excel export was not possible "
            #             "because of this reason.")
            #     raise UserError(msg)

            product_id = bom_line.product_id
            if bom_line in original_bom_lines:
                bom_factor_used = 1
            else:
                bom_factor_used = bom_factor

            lines.append(
                [
                    ident,
                    [
                        bom_line,
                        (bom_line.alt_qty or bom_line.product_qty) * bom_factor_used,
                    ],
                ]
            )

            if bom_line.child_bom_id:
                bom_factor_used = (
                    bom_line.alt_qty or bom_line.product_qty
                ) * bom_factor_used
                child_bom = product_id.bom_ids and product_id.bom_ids[0]

                ident = "{}{}{}".format(identifier, "0000", child_bom.id)

                lines += self.get_sub_lines(
                    child_bom, bom_factor_used, original_bom_lines, ident
                )
        return lines

    def get_bom_quantities(self, bom):

        line_factors = self.get_sub_lines(bom, 1, bom.bom_line_ids, bom.id)

        # Very important to use defaultdict here for the loop below to work
        # properly!
        quantities = defaultdict(lambda: 0.0)

        for line, quantity in line_factors:
            quantities[line] = quantity
        return quantities

    def print_materials(
        self,
        product_id,
        sheet2,
        row,
        level,
        quantity,
        parent_code,
        parent,
        upper_parent,
        bom,
        center_cell,
    ):
        a, level = row, level

        materials = self.env["product.material.composition"].search(
            [("product_product_id", "=", product_id.id)]
        )

        for mater in materials:
            sheet2.write(a, 0, parent_code)  # Internal category/display name
            sheet2.write(a, 1, str(level))  # Level
            sheet2.write(a, 2, product_id.default_code or "")  # Internal reference
            sheet2.write(a, 3, parent.product_tmpl_id.name)  # Name
            sheet2.write(a, 4, parent.product_uom_id.name or "")  # Unit
            sheet2.write(a, 5, quantity)  # Quantity in products
            sheet2.write(a, 6, mater.name or "")  # Part name
            sheet2.write(a, 7, mater.product_material_id.name or "")  # Material
            sheet2.write(
                a, 8, mater.product_material_class_id.name or ""
            )  # Material class
            sheet2.write(
                a, 9, dict(mater._fields["type"].selection).get(mater.type)
            )  # Material type
            sheet2.write(
                a, 10, mater.product_material_upper_category_id.name or ""
            )  # Upper category

            bom_product_id = upper_parent or bom.product_tmpl_id.product_variant_id

            multiply_with = 1

            if product_id.multiply_with_partial_weight:
                multiply_with = (
                    product_id.weight
                    and (bom_product_id.weight / product_id.weight)
                    or 1
                )

            if product_id.ignore_component_qty:
                quantity = 1

            if mater.type == "product_packaging":
                sheet2.write(
                    a, 11, mater.net_weight * quantity * multiply_with
                )  # Incoming packaging Material weight / per unit
            elif mater.type == "product" and not mater.is_delivery_package:
                sheet2.write(
                    a, 12, mater.net_weight * quantity * multiply_with
                )  # Product Material weight / per unit
            elif mater.type == "product" and mater.is_delivery_package:
                sheet2.write(
                    a, 13, mater.net_weight * quantity * multiply_with
                )  # Product and Delivery package Material weight / per unit

            sheet2.write(
                a, 14, mater.net_weight_uom_id.name, center_cell
            )  # Net weight UoM
            sheet2.write(a, 15, mater.recycled_percentage)  # Recycled material %
            sheet2.write(
                a, 16, mater.product_material_waste_component_id.name or ""
            )  # Waste procuts
            sheet2.write(
                a, 17, mater.product_material_waste_endpoint_id.name or ""
            )  # Waste endpoint
            sheet2.write(a, 22, mater.description or "")  # Material notes

            if len(materials.ids) > 1:
                a += 1

        if len(materials.ids) > 1:
            a -= 1

        return a

    def print_materials_sheet4(
        self, product_id, sheet4, row, level, quantity, parent_code, parent, oper, bom
    ):
        c, level = row, level

        materials = self.env["product.material.composition"].search(
            [("product_product_id", "=", product_id.id)]
        )

        for mater in materials:
            sheet4.write(c, 0, bom.product_tmpl_id.name or "")  # Internal reference
            sheet4.write(c, 1, bom.product_id.default_code or "")  # Name
            sheet4.write(
                c, 2, bom.product_tmpl_id.name or ""
            )  # Internal category/display name
            sheet4.write(c, 3, oper.id or "")  # Operation ID
            sheet4.write(c, 4, oper.name or "")  # Operation name
            #            sheet4.write(c, 5, quantity)  # Quantity in products

            sheet4.write(c, 7, product_id.default_code or "")  # Internal reference
            sheet4.write(c, 8, product_id.name)  # Name

            sheet4.write(c, 9, mater.name or "")  # Part name
            sheet4.write(c, 10, mater.product_material_id.name or "")  # Material
            sheet4.write(
                c, 11, mater.product_material_class_id.name or ""
            )  # Material class
            sheet4.write(
                c, 12, dict(mater._fields["type"].selection).get(mater.type)
            )  # Material type
            sheet4.write(c, 15, mater.recycled_percentage)  # Recycled material %
            sheet4.write(
                c, 16, mater.product_material_waste_component_id.name
            )  # Waste procuts
            sheet4.write(
                c, 17, mater.product_material_waste_endpoint_id.name
            )  # Waste endpoint

            time_in_year = parent.company_id.time_in_year

            grams = self.env.ref("uom.product_uom_gram")

            if (
                parent.product_uom_id.category_id.id
                == self.env.ref("uom.product_uom_categ_kgm").id
            ):
                weight_in_grams = parent.product_uom_id._compute_quantity(
                    mater.net_weight * quantity, grams, round=False
                )
            else:
                weight_in_grams = mater.net_weight_uom_id._compute_quantity(
                    mater.net_weight * quantity, grams, round=False
                )

            sheet4.write(c, 13, weight_in_grams)  # Material weight / per unit
            sheet4.write(c, 14, grams.name)  # Net weight UoM

            #  Check that time_in_year is not zero
            consumed_weight = (
                time_in_year
                and ((weight_in_grams / time_in_year) * (oper.duration_total * 60))
                or 0
            )

            sheet4.write(
                c, 18, consumed_weight
            )  # Energy consumption during an operation / Total/(kWh)

            sheet4.write(c, 19, "g" or "")  # Unit

            if len(materials.ids) > 1:
                c += 1

        if len(materials.ids) > 1:
            c -= 1

        return c

    def print_material_requirements(
        self, product_id, sheet5, row, level, quantity, style, parent_code, parent
    ):
        d, level = row, level
        sheet5_style = style

        materials = self.env["product.material.composition"].search(
            [("product_product_id", "=", product_id.id)]
        )

        for mater in materials:
            sheet5.write(
                d, 0, parent_code, sheet5_style
            )  # Internal category/display name
            sheet5.write(d, 1, str(level), sheet5_style)  # Level
            sheet5.write(
                d, 2, product_id.default_code or "", sheet5_style
            )  # Internal reference
            sheet5.write(d, 3, product_id.name or "", sheet5_style)  # Name
            sheet5.write(d, 4, parent.product_uom_id.name or "", sheet5_style)  # Unit

            sheet5.write(d, 5, mater.name or "", sheet5_style)  # Part name
            sheet5.write(
                d, 6, mater.product_material_id.name or "", sheet5_style
            )  # Material
            sheet5.write(
                d, 7, mater.product_material_class_id.name, sheet5_style
            )  # Material class
            sheet5.write(
                d, 8, mater.net_weight * quantity, sheet5_style
            )  # Net weight in a product
            sheet5.write(
                d, 9, mater.net_weight_uom_id.name or "", sheet5_style
            )  # Net weight Unit
            sheet5.write(
                d, 10, mater.chemicals_compliant.name or "", sheet5_style
            )  # Dangerous materials / Chemicals Compliant
            sheet5.write(d, 11, mater.rohs_compliant.name or "", sheet5_style)  # RoHS
            sheet5.write(d, 12, mater.reach_compliant.name or "", sheet5_style)  # REACH
            sheet5.write(d, 13, mater.scip_compliant.name or "", sheet5_style)  # SCIP
            sheet5.write(
                d, 14, mater.pop_compliant.name or "", sheet5_style
            )  # POP (Persistant Organic Pollutants)
            sheet5.write(
                d, 15, mater.halogen_compliant.name or "", sheet5_style
            )  # Halogens
            sheet5.write(
                d, 16, mater.conflict_area_minerals_compliant.name or "", sheet5_style
            )  # Conflict Area Minerals
            sheet5.write(
                d, 17, mater.recycled_percentage or "", sheet5_style
            )  # Recycle material %
            sheet5.write(
                d,
                18,
                mater.product_material_waste_component_id.name or "",
                sheet5_style,
            )  # Waste product
            sheet5.write(
                d, 19, mater.product_material_waste_endpoint_id.name or "", sheet5_style
            )  # Waste endpoint

            if len(materials.ids) > 1:
                d += 1

        if len(materials.ids) > 1:
            d -= 1

        return d

    def print_bom_children_2(
        self,
        ch,
        sheet2,
        row,
        level,
        parent,
        parent_level,
        child_number,
        quantities,
        identifier,
        parent_bom,
        upper_parent,
        center_cell,
    ):
        a, j = row, level
        j += 1
        a += 1

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet2.write(a, 0, parent_with_code)  # Internal category/display name
        sheet2.write(a, 1, level)  # Level
        sheet2.write(a, 2, ch.product_id.default_code or "")  # Internal reference
        sheet2.write(a, 3, ch.product_tmpl_id.name)  # Name
        sheet2.write(a, 4, ch.product_id.uom_id.name)  # Unit
        sheet2.write(a, 5, quantities[ident][1])  # Quantity in products

        main_vendor = ch.product_id.seller_ids and ch.product_id.seller_ids.filtered(
            lambda v: v.company_id == ch.company_id
        )

        main_vendor = main_vendor and main_vendor[0] or ""

        if main_vendor:
            vendor = main_vendor.name.address_ids.filtered(lambda r: r.type == "other")
            vendor = vendor and vendor[0].name or ""
        else:
            vendor = ""

        main_vendor = (
            main_vendor
            and (
                main_vendor[0].name.name,
                "{}{}{}".format(
                    main_vendor[0].name.country_id.name,
                    main_vendor[0].name.street
                    and " {}".format(main_vendor[0].name.street)
                    or "",
                    main_vendor[0].name.city
                    and " {}".format(main_vendor[0].name.city)
                    or "",
                )
                or "",
            )
            or ("N/A", "N/A")
        )

        sheet2.write(a, 18, main_vendor[0])  # Vendor
        sheet2.write(a, 19, main_vendor[1])  # Vendor address
        sheet2.write(a, 20, vendor)  # Supply address

        sheet2.write(
            a, 21, ch.product_id.origin_country_id.name or ""
        )  # Country of origin

        a = self.print_materials(
            product_id=ch.product_id,
            sheet2=sheet2,
            row=a,
            level=level,
            quantity=quantities[ident][1],
            parent_code=parent_with_code,
            parent=ch,
            upper_parent=upper_parent,
            bom=parent_bom,
            center_cell=center_cell,
        )

        child_number = 0
        for child in ch.child_line_ids:
            if child._skip_bom_line(ch.product_id):
                continue

            child_number += 1
            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            a = self.print_bom_children_2(
                child,
                sheet2,
                a,
                j,
                parent=ch.product_id,
                parent_level=level,
                child_number=child_number,
                quantities=quantities,
                identifier=ident,
                parent_bom=child_bom,
                upper_parent=ch.product_id,
                center_cell=center_cell,
            )
        j -= 1
        return a

    def product_material_summary(
        self,
        sheet6,
        bom,
        product_variant,
        style,
        child_number,
        materials_dict,
        multiplier=1,
    ):
        wood_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Wood")]
        )
        glue_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Glue")]
        )
        metal_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Metal")]
        )
        plastic_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Plastic")]
        )
        eee_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "EEE")]
        )
        oil_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "OIL")]
        )

        for ch in bom.bom_line_ids:
            if product_variant and ch._skip_bom_line(product_variant):
                continue

            if ch.product_id.ignore_component_qty:
                quantity = 1
            else:
                quantity = ch.alt_qty or ch.product_qty

            bom_product_id = product_variant or bom.product_tmpl_id.product_variant_id

            multiply_with = 1

            if ch.product_id.multiply_with_partial_weight:
                multiply_with = (
                    ch.product_id.weight
                    and (bom_product_id.weight / ch.product_id.weight)
                    or 1
                )

            materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("is_delivery_package", "=", False),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["materials_weight"] += sum(
                mater.net_weight * quantity * multiplier * multiply_with
                for mater in materials
            )
            materials_dict["materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * quantity
                * multiplier
                * multiply_with
                for mater in materials
            )

            wood_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", wood_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", False),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["wood_materials_weight"] += sum(
                mater.net_weight * quantity * multiplier * multiply_with
                for mater in wood_materials
            )
            materials_dict["wood_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * quantity
                * multiplier
                * multiply_with
                for mater in wood_materials
            )

            glue_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", glue_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", False),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["glue_materials_weight"] += sum(
                mater.net_weight * quantity * multiplier * multiply_with
                for mater in glue_materials
            )
            materials_dict["glue_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * quantity
                * multiplier
                * multiply_with
                for mater in glue_materials
            )

            metal_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", metal_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", False),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["metal_materials_weight"] += sum(
                mater.net_weight * quantity * multiplier * multiply_with
                for mater in metal_materials
            )
            materials_dict["metal_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * quantity
                * multiplier
                * multiply_with
                for mater in metal_materials
            )

            plastic_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", plastic_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", False),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["plastic_materials_weight"] += sum(
                mater.net_weight * quantity * multiplier * multiply_with
                for mater in plastic_materials
            )
            materials_dict["plastic_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * quantity
                * multiplier
                * multiply_with
                for mater in plastic_materials
            )

            eee_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", eee_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", False),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["eee_materials_weight"] += sum(
                mater.net_weight * quantity * multiplier * multiply_with
                for mater in eee_materials
            )
            materials_dict["eee_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * quantity
                * multiplier
                * multiply_with
                for mater in eee_materials
            )

            oil_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", oil_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", False),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["oil_materials_weight"] += sum(
                mater.net_weight * quantity * multiplier * multiply_with
                for mater in oil_materials
            )
            materials_dict["oil_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * quantity
                * multiplier
                * multiply_with
                for mater in oil_materials
            )

            if ch.child_bom_id:
                materials_dict = self.product_material_summary(
                    sheet6,
                    product_variant=ch.product_id,
                    style=None,
                    bom=ch.child_bom_id,
                    child_number=child_number,
                    materials_dict=materials_dict,
                    multiplier=multiplier * quantity,
                )
        return materials_dict

    def packaging_material_summary(
        self,
        sheet6,
        bom,
        product_variant,
        style,
        child_number,
        materials_dict,
        multiplier=1,
    ):
        cardboard_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Cardboard")]
        )
        paper_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Paper")]
        )
        plastic_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Plastic")]
        )
        metal_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Metal")]
        )
        wood_category_id = self.env["product.material.upper.category"].search(
            [("name", "=", "Wood")]
        )

        for ch in bom.bom_line_ids:
            if product_variant and ch._skip_bom_line(product_variant):
                continue

            materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("is_delivery_package", "=", True),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["materials_weight"] += sum(
                mater.net_weight * (ch.alt_qty or ch.product_qty) * multiplier
                for mater in materials
            )
            materials_dict["materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * (ch.alt_qty or ch.product_qty)
                * multiplier
                for mater in materials
            )

            cardboard_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    (
                        "product_material_upper_category_id",
                        "=",
                        cardboard_category_id.id,
                    ),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", True),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["cardboard_materials_weight"] += sum(
                mater.net_weight * (ch.alt_qty or ch.product_qty) * multiplier
                for mater in cardboard_materials
            )
            materials_dict["cardboard_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * (ch.alt_qty or ch.product_qty)
                * multiplier
                for mater in cardboard_materials
            )

            paper_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", paper_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", True),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["paper_materials_weight"] += sum(
                mater.net_weight * (ch.alt_qty or ch.product_qty) * multiplier
                for mater in paper_materials
            )
            materials_dict["paper_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * (ch.alt_qty or ch.product_qty)
                * multiplier
                for mater in paper_materials
            )

            plastic_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", plastic_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", True),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["plastic_materials_weight"] += sum(
                mater.net_weight * (ch.alt_qty or ch.product_qty) * multiplier
                for mater in plastic_materials
            )
            materials_dict["plastic_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * (ch.alt_qty or ch.product_qty)
                * multiplier
                for mater in plastic_materials
            )

            metal_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", metal_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", True),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["metal_materials_weight"] += sum(
                mater.net_weight * (ch.alt_qty or ch.product_qty) * multiplier
                for mater in metal_materials
            )
            materials_dict["metal_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * (ch.alt_qty or ch.product_qty)
                * multiplier
                for mater in metal_materials
            )

            wood_materials = self.env["product.material.composition"].search(
                [
                    ("product_product_id", "=", ch.product_id.id),
                    ("product_material_upper_category_id", "=", wood_category_id.id),
                    ("product_material_upper_category_id", "!=", False),
                    ("is_delivery_package", "=", True),
                    ("type", "=", "product"),
                ]
            )
            materials_dict["wood_materials_weight"] += sum(
                mater.net_weight * (ch.alt_qty or ch.product_qty) * multiplier
                for mater in wood_materials
            )
            materials_dict["wood_materials_recyc_weight"] += sum(
                (mater.recycled_percentage / 100)
                * mater.net_weight
                * (ch.alt_qty or ch.product_qty)
                * multiplier
                for mater in wood_materials
            )

            if ch.child_bom_id:
                materials_dict = self.packaging_material_summary(
                    sheet6,
                    product_variant=ch.product_id,
                    style=None,
                    bom=ch.child_bom_id,
                    child_number=child_number,
                    materials_dict=materials_dict,
                    multiplier=multiplier * (ch.alt_qty or ch.product_qty),
                )
        return materials_dict

    def all_bom_consus(self, bom, product_variant, consu_oper_durat):
        for oper in bom.operation_ids:
            consu = oper.workcenter_id.bom_consu

            if consu:
                consu_oper_durat.append(
                    [oper.workcenter_id.bom_consu, oper.duration_total * 60]
                )

        for ch in bom.bom_line_ids:
            if product_variant and ch._skip_bom_line(product_variant):
                continue
            if ch.child_bom_id:
                bom_consus = self.all_bom_consus(
                    bom=ch.child_bom_id,
                    product_variant=ch.product_id,
                    consu_oper_durat=consu_oper_durat,
                )
        return consu_oper_durat

    def all_material_summary(
        self,
        sheet6,
        bom,
        product_variant,
        style,
        child_number,
        products,
        multiplier=1,
    ):
        for ch in bom.bom_line_ids:
            if product_variant and ch._skip_bom_line(product_variant):
                continue

            product = self.env["product.product"].browse(ch.product_id.id)

            if product:
                products.append(
                    [
                        product,
                        (ch.alt_qty or ch.product_qty) * multiplier,
                        ch.product_uom_id,
                        bom,
                        product_variant,
                    ]
                )

            if ch.child_bom_id:
                products = self.all_material_summary(
                    sheet6,
                    product_variant=ch.product_id,
                    style=None,
                    bom=ch.child_bom_id,
                    child_number=child_number,
                    products=products,
                    multiplier=multiplier * (ch.alt_qty or ch.product_qty),
                )
        return products

    def print_by_products(
        self,
        sheet3,
        row,
        level,
        parent_level,
        bom,
        product_variant,
        style,
        child_number,
        multiplier=1,
    ):
        b, j = row, level
        j += 1
        bold = style

        if level:
            level = "{}.{}".format(parent_level, child_number)
        else:
            level = str(1)

        for by_product in bom.byproduct_ids:

            # -------------------------------#
            # ----------- Sheet 3 -----------#
            # -------------------------------#

            "{}".format(bom.id)

            self.get_bom_quantities(bom)

            sheet3.write(
                b, 0, bom.product_tmpl_id.name, bold
            )  # Internal category/display name
            sheet3.write(b, 1, level)  # Level
            sheet3.write(
                b, 2, by_product.product_id.product_tmpl_id.name, bold
            )  # Product to which operation is done
            sheet3.write(
                b,
                3,
                bom.product_tmpl_id.default_code or product_variant.default_code or "",
                bold,
            )  # Product internal reference

            sheet3.write(b, 4, by_product.operation_id.sequence, bold)  # Operation ID
            sheet3.write(b, 5, by_product.operation_id.name, bold)  # Operation name

            sheet3.write(
                b, 6, by_product.product_id.product_tmpl_id.name, bold
            )  # Waste product name

            if product_variant.multiply_with_by_products:
                weight_result = product_variant.gross_weight - product_variant.weight
                sheet3.write(
                    b, 7, weight_result * multiplier or 0, bold
                )  # Waste amount
            else:
                sheet3.write(b, 7, by_product.product_qty or 0, bold)  # Waste amount

            sheet3.write(b, 8, by_product.product_uom_id.name, bold)  # Waste unit

            b += 1

        for ch in bom.bom_line_ids:
            if product_variant and ch._skip_bom_line(product_variant):
                continue

            child_number += 1

            if ch.child_bom_id:
                b = self.print_by_products(
                    sheet3,
                    row=b,
                    level=j,
                    parent_level=level,
                    product_variant=ch.product_id,
                    style=None,
                    bom=ch.child_bom_id,
                    child_number=child_number,
                    multiplier=multiplier * (ch.alt_qty or ch.product_qty),
                )

        j -= 1
        return b

    def print_bom_children_4(
        self,
        ch,
        sheet4,
        row,
        level,
        parent,
        parent_level,
        child_number,
        quantities,
        identifier,
        operation,
        bom,
    ):
        c, j = row, level
        j += 1

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet4.write(c, 0, ch.product_id.name or "")  # Internal reference
        sheet4.write(c, 1, parent.default_code or "")  # Name
        sheet4.write(c, 2, parent_with_code)  # Internal category/display name
        sheet4.write(c, 3, operation.id or "")  # Operation ID
        sheet4.write(c, 4, operation.name or "")  # Operation name

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        sheet4.write(c, 7, ch.product_id.default_code or "")  # Internal reference
        sheet4.write(c, 8, ch.product_id.name)  # Name

        time_in_year = ch.company_id.time_in_year

        grams = self.env.ref("uom.product_uom_gram")

        weight_in_grams = ch.product_id.weight_uom_id._compute_quantity(
            ch.product_id.weight, grams, round=False
        )

        use_quantity = quantities and quantities[ident][1] or 1

        #  Check that time_in_year is not zero
        consumed_weight = (
            time_in_year
            and (
                (use_quantity * weight_in_grams / time_in_year)
                * (operation.duration_total * 60)
            )
            or 0
        )

        c = self.print_materials_sheet4(
            product_id=ch.product_id,
            sheet4=sheet4,
            row=c,
            level=level,
            quantity=quantities[ident][1],
            parent_code=parent_with_code,
            parent=ch,
            oper=operation,
            bom=bom,
        )

        has_materials = self.env["product.material.composition"].search(
            [("product_product_id", "=", ch.product_id.id)]
        )

        if len(has_materials.ids) < 1:
            sheet4.write(
                c, 18, consumed_weight
            )  # Energy consumption during an operation / Total/(kWh)

            sheet4.write(c, 19, "g" or "")  # Unit

        c += 1
        child_number = 0
        for child in ch.child_line_ids:
            if child._skip_bom_line(ch.product_id):
                continue

            child_number += 1
            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            c = self.print_bom_children_4(
                child,
                sheet4,
                c,
                j,
                parent=ch.product_id,
                parent_level=level,
                child_number=child_number,
                quantities=quantities,
                identifier=ident,
                bom=bom,
            )
        j -= 1
        return c

    def print_bom_children_5(
        self,
        ch,
        sheet5,
        row,
        level,
        parent,
        parent_level,
        child_number,
        quantities,
        identifier,
    ):
        d, j = row, level
        j += 1
        d += 1

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet5.write(d, 0, parent_with_code)  # Internal category/display name
        sheet5.write(d, 1, level)  # Internal category/display name
        sheet5.write(d, 2, ch.product_id.default_code or "")  # Internal reference
        sheet5.write(d, 3, ch.product_id.name)  # Name
        sheet5.write(d, 4, ch.product_uom_id.name or "")  # Unit

        d = self.print_material_requirements(
            product_id=ch.product_id,
            sheet5=sheet5,
            row=d,
            level=level,
            quantity=quantities[ident][1],
            style=None,
            parent_code=parent_with_code,
            parent=ch,
        )

        child_number = 0
        for child in ch.child_line_ids:
            if child._skip_bom_line(ch.product_id):
                continue

            child_number += 1
            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            d = self.print_bom_children_5(
                child,
                sheet5,
                d,
                j,
                parent=ch.product_id,
                parent_level=level,
                child_number=child_number,
                quantities=quantities,
                identifier=ident,
            )
        j -= 1
        return d

    def energy_summary(self, bom, product_variant, sheet6, operations):

        for oper in bom.operation_ids:
            operations += oper

        for ch in bom.bom_line_ids:
            if product_variant and ch._skip_bom_line(product_variant):
                continue
            if ch.child_bom_id:
                operations = self.energy_summary(
                    bom=ch.child_bom_id,
                    product_variant=ch.product_id,
                    sheet6=sheet6,
                    operations=operations,
                )
        return operations

    # flake8: noqa: C901
    def operation_bom_consus(
        self, bom, product_variant, sheet4, row, level, parent_level, identifier, style
    ):

        parent_bom = bom

        bold = style
        c, j = row, level

        for oper in parent_bom.operation_ids:
            j += 1

            bom = oper.workcenter_id.bom_consu
            ident = "{}".format(bom.id)

            quantities = self.get_bom_quantities(bom)

            sheet4.write(
                c, 0, bom.product_tmpl_id.name or ""
            )  # Internal category/display name
            sheet4.write(
                c, 1, bom.product_id.default_code or "", bold
            )  # Product internal reference
            sheet4.write(c, 2, bom.product_tmpl_id.name or "", bold)  # Name
            sheet4.write(c, 3, oper.id or "", bold)  # Operation ID
            sheet4.write(c, 4, oper.name or "", bold)  # Operation name

            workcenter = oper.workcenter_id

            # Note that oper.duration_active and oper.duration_passive are in minutes
            total_energy = (
                (workcenter.energy_consumption * oper.duration_active)
                + (workcenter.energy_consumption_passive * oper.duration_passive)
            ) / 60

            sheet4.write(
                c, 5, total_energy, bold
            )  # Energy consumption during an operation / Total/(kWh)

            sheet4.write(c, 6, "kWh", bold)
            sheet4.write(c, 7, "N/A", bold)  # Operation consumptions product ID

            sheet4.write(
                c, 8, "N/A", bold
            )  # Name of the product consumed in an operation

            time_in_year = bom.company_id.time_in_year

            grams = self.env.ref("uom.product_uom_gram")

            # Either use variant or template weight
            if bom.product_id and bom.product_id.weight:
                weight_in_grams = bom.product_id.weight_uom_id._compute_quantity(
                    bom.product_id.weight, grams, round=False
                )
            elif bom.product_tmpl_id and bom.product_tmpl_id.weight:
                weight_in_grams = bom.product_tmpl_id.weight_uom_id._compute_quantity(
                    bom.product_tmpl_id.weight, grams, round=False
                )
            else:
                weight_in_grams = 0

            #  Check that time_in_year is not zero
            consumed_weight = (
                time_in_year
                and (
                    (bom.product_qty * weight_in_grams / time_in_year)
                    * (oper.duration_total * 60)
                )
                or 0
            )

            sheet4.write(
                c, 18, consumed_weight, bold
            )  # Consumed amount / produced 1 product

            sheet4.write(c, 19, "g", bold)  # Unit

            parent_level_4 = c - 1
            c += 1
            j = 0

            child_number = 0
            for ch in bom.bom_line_ids:
                if product_variant and ch._skip_bom_line(product_variant):
                    continue
                child_number += 1
                c = self.print_bom_children_4(
                    ch,
                    sheet4,
                    c,
                    j,
                    parent=bom.product_tmpl_id,
                    parent_level=parent_level_4,
                    child_number=child_number,
                    quantities=quantities,
                    identifier=ident,
                    operation=oper,
                    bom=bom,
                )

        parent_level_4 = c - 1
        j = 0

        child_number = 0

        for ch in parent_bom.bom_line_ids:
            if product_variant and ch._skip_bom_line(product_variant):
                continue
            child_number += 1
            ident = "{}".format(ch.child_bom_id.id)

            if ch.child_bom_id:
                c = self.operation_bom_consus(
                    bom=ch.child_bom_id,
                    product_variant=ch.product_id,
                    sheet4=sheet4,
                    row=c,
                    level=j,
                    parent_level=parent_level_4,
                    identifier=ident,
                    style=None,
                )
        j -= 1
        return c

    def generate_xlsx_report(self, workbook, data, objects):

        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 14.0"}
        )

        # -------------------------------#
        # ----------- Sheet 2 -----------#
        # -------------------------------#

        sheet2 = workbook.add_worksheet(_("BOM materials"))

        sheet2.set_landscape()
        sheet2.fit_to_pages(1, 0)
        sheet2.set_zoom(80)

        # Some column sizes changed to match their title
        sheet2.set_column(0, 0, 56)
        sheet2.set_column(1, 1, 15)
        sheet2.set_column(2, 2, 20)
        sheet2.set_column(3, 3, 56)
        sheet2.set_column(4, 4, 15)
        sheet2.set_column(5, 6, 25)
        sheet2.set_column(7, 7, 28)
        sheet2.set_column(8, 9, 26)
        sheet2.set_column(10, 10, 24)
        sheet2.set_column(11, 11, 22)
        sheet2.set_column(12, 12, 22)
        sheet2.set_column(13, 13, 22)
        sheet2.set_column(14, 14, 16)
        sheet2.set_column(15, 15, 20)
        sheet2.set_column(16, 16, 20)
        sheet2.set_column(17, 17, 25)
        sheet2.set_column(18, 18, 25)
        sheet2.set_column(19, 19, 28)
        sheet2.set_column(20, 20, 25)
        sheet2.set_column(21, 21, 27)
        sheet2.set_column(22, 22, 40)

        # Column styles
        bold = workbook.add_format({"bold": True})

        center_cell = workbook.add_format({"align": "center"})

        title_style_product_level = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#C6FF8D",
                "bottom": 1,
                "text_wrap": True,
                "align": "center",
                "valign": "vcenter",
            }
        )

        sheet_title_2 = [
            _("Internal category/display name"),  # 0 (A)
            _("Level"),  # 1 (B)
            _("Internal reference"),  # 2 (C)
            _("Name"),  # 3 (D)
            _("Unit"),  # 4 (E)
            _("Quantity in products"),  # 5 (F)
            _("Part name"),  # 6 (G)
            _("Material"),  # 7 (H)
            _("Material class"),  # 8 (I)
            _("Material type"),  # 9 (J)
            _("Upper category"),  # 10 (K)
            _("Incoming packaging Material weight / per unit"),  # 11 (L)
            _("Product Material weight / per unit"),  # 12 (M)
            _("Product and Delivery package Material weight / per unit"),  # 13 (N)
            _("Weight unit"),  # 14 (O)
            _("Recycle material %"),  # 15 (P)
            _("Waste products"),  # 16 (Q)
            _("Waste endpoint"),  # 17 (R)
            _("Vendor"),  # 18 (S)
            _("Vendor Address"),  # 19 (T)
            _("Supply Address"),  # 20 (U)
            _("Country of origin"),  # 21 (V)
            _("Material notes"),  # 22 (W)
        ]

        # sheet2.set_row(0, None, None, {"collapsed": 0})

        for title in enumerate(sheet_title_2):
            sheet2.merge_range(
                0, title[0], 2, title[0], title[1] or "", title_style_product_level
            )

        sheet2.freeze_panes(3, 0)

        # -------------------------------#
        # ----------- Sheet 3 -----------#
        # -------------------------------#

        sheet3 = workbook.add_worksheet(_("BOM by-products"))

        sheet3.set_landscape()
        sheet3.fit_to_pages(1, 0)
        sheet3.set_zoom(80)

        # Some column sizes changed to match their title
        sheet3.set_column(0, 0, 56)
        sheet3.set_column(1, 1, 18)
        sheet3.set_column(2, 2, 35)
        sheet3.set_column(3, 3, 25)
        sheet3.set_column(4, 4, 20)
        sheet3.set_column(5, 5, 48)
        sheet3.set_column(6, 6, 25)
        sheet3.set_column(7, 7, 28)
        sheet3.set_column(8, 8, 18)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C9C0FF", "bottom": 1}
        )

        sheet_title_3 = [
            _("Internal category/display name"),
            _("Level"),
            _("Product to which operation is done"),
            _("Product internal reference"),
            _("Operation ID"),
            _("Operation name"),
            _("Waste product name"),
            _("Waste amount"),
            _("Waste unit"),
        ]

        sheet3.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_3):
            sheet3.write(0, title[0], title[1] or "", title_style_product_level)

        sheet3.freeze_panes(1, 0)

        # -------------------------------#
        # ----------- Sheet 4 -----------#
        # -------------------------------#

        sheet4 = workbook.add_worksheet(_("Operations, energy, consumption"))

        sheet4.set_landscape()
        sheet4.fit_to_pages(1, 0)
        sheet4.set_zoom(80)

        # Some column sizes changed to match their title
        sheet4.set_column(0, 0, 39)  # A
        sheet4.set_column(1, 1, 20)  # B
        sheet4.set_column(2, 2, 47)  # C
        sheet4.set_column(3, 3, 18)  # D
        sheet4.set_column(4, 4, 25)  # E
        sheet4.set_column(5, 5, 40)  # F
        sheet4.set_column(6, 6, 18)  # G
        sheet4.set_column(7, 7, 35)  # H
        sheet4.set_column(8, 8, 45)  # I
        sheet4.set_column(9, 9, 25)  # J
        sheet4.set_column(10, 10, 28)  # K
        sheet4.set_column(11, 11, 26)  # L
        sheet4.set_column(12, 12, 26)  # M
        sheet4.set_column(13, 13, 22)  # N
        sheet4.set_column(14, 14, 20)  # O
        sheet4.set_column(15, 15, 20)  # P
        sheet4.set_column(16, 16, 20)  # Q
        sheet4.set_column(17, 17, 20)  # R
        sheet4.set_column(18, 18, 40)  # S
        sheet4.set_column(19, 19, 12)  # T

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#ECB18F", "bottom": 1}
        )

        sheet_title_4 = [
            _("Internal category/display name"),  # 0 (A)
            _("Product internal reference"),  # 1 (B)
            _("Name"),  # 2 (C)
            _("Operation ID"),  # 3 (D)
            _("Operation name"),  # 4 (E)
            _("Energy consumption during an operation / Total(kWh)"),  # 5 (F)
            _("Energy Unit"),  # 6 (G)
            _("Operation consumptions product ID"),  # 7 (H)
            _("Name of the product consumed in an operation"),  # 8 (I)
            _("Part name"),  # 9 (J)
            _("Material"),  # 10 (K)
            _("Material class"),  # 11 (L)
            _("Material type"),  # 12 (M)
            _("Material weight / per unit"),  # 13 (N)
            _("Weight unit"),  # 14 (O)
            _("Recycle material %"),  # 15 (P)
            _("Waste products"),  # 16 (Q)
            _("Waste endpoint"),  # 17 (R)
            _("Consumed amount / produced 1 product"),  # 18 (S)
            _("Unit"),  # 19 (T)
        ]

        sheet4.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_4):
            sheet4.write(0, title[0], title[1] or "", title_style_product_level)

        sheet4.freeze_panes(1, 0)

        # -------------------------------#
        # ----------- Sheet 5 -----------#
        # -------------------------------#

        sheet5 = workbook.add_worksheet(_("Product requirements"))

        sheet5.set_landscape()
        sheet5.fit_to_pages(1, 0)
        sheet5.set_zoom(80)

        # Some column sizes changed to match their title
        sheet5.set_column(0, 0, 47)
        sheet5.set_column(1, 1, 12)
        sheet5.set_column(2, 2, 25)
        sheet5.set_column(3, 3, 47)
        sheet5.set_column(4, 4, 20)
        sheet5.set_column(5, 7, 29)
        sheet5.set_column(8, 8, 25)
        sheet5.set_column(9, 9, 20)
        sheet5.set_column(10, 10, 20)
        sheet5.set_column(11, 11, 20)
        sheet5.set_column(12, 12, 20)
        sheet5.set_column(13, 13, 20)
        sheet5.set_column(14, 14, 34)
        sheet5.set_column(15, 15, 20)
        sheet5.set_column(16, 16, 28)
        sheet5.set_column(17, 17, 20)
        sheet5.set_column(18, 18, 20)
        sheet5.set_column(19, 19, 20)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#6AD25F", "bottom": 1}
        )

        sheet_title_5 = [
            _("Internal category/display name"),
            _("Level"),
            _("Product internal reference"),
            _("Name"),
            _("Unit"),
            _("Part name"),
            _("Material"),
            _("Material class"),
            _("Net weight in a product"),
            _("Net weight Unit"),
            _("Dangerous materials"),
            _("RoHS"),
            _("REACH"),
            _("SCIP"),
            _("POP (Persistant Organic Pollutants"),
            _("Halogens"),
            _("Conflict Area Minerals"),
            _("Recycle material %"),
            _("Waste product"),
            _("Waste endpoint"),
        ]

        sheet5.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_5):
            sheet5.write(0, title[0], title[1] or "", title_style_product_level)

        sheet5.freeze_panes(1, 0)

        # -------------------------------#
        # ----------- Sheet 6 -----------#
        # -------------------------------#

        sheet6 = workbook.add_worksheet(_("Material summaries"))

        sheet6.set_landscape()
        sheet6.fit_to_pages(1, 0)
        sheet6.set_zoom(80)

        column = 0
        columns_1 = 0
        columns_2 = 0
        columns_3 = 0
        columns_4 = 0
        columns_5 = 0
        columns_6 = 0
        columns_7 = 0
        columns_8 = 0
        columns_9 = 0

        # Some column sizes changed to match their title

        # 1. Product Materials Summary
        sheet6.set_column(column, column, 33)  # A
        column += 1
        sheet6.set_column(column, column, 17)  # B
        column += 1
        sheet6.set_column(column, column, 13)  # C
        column += 1
        sheet6.set_column(column, column, 33)  # D
        column += 1
        columns_1 = column

        # 2. Packaging Materials Summary
        sheet6.set_column(column, column, 33)  # D
        column += 1
        sheet6.set_column(column, column, 17)  # E
        column += 1
        sheet6.set_column(column, column, 13)  # F
        column += 1
        sheet6.set_column(column, column, 33)  # G
        column += 1
        columns_2 = column

        # 3. Product component materials
        sheet6.set_column(column, column, 33)  # O
        column += 1
        sheet6.set_column(column, column, 17)  # P
        column += 1
        sheet6.set_column(column, column, 13)  # Q
        column += 1
        sheet6.set_column(column, column, 33)  # R
        column += 1
        sheet6.set_column(column, column, 33)  # W
        column += 1
        sheet6.set_column(column, column, 31)  # X
        column += 1
        sheet6.set_column(column, column, 32)  # R
        column += 1
        sheet6.set_column(column, column, 26)  # W
        column += 1
        sheet6.set_column(column, column, 30)  # X
        column += 1
        columns_3 = column

        # 4. Delivery Packaging materials
        sheet6.set_column(column, column, 33)  # S
        column += 1
        sheet6.set_column(column, column, 17)  # T
        column += 1
        sheet6.set_column(column, column, 14)  # U
        column += 1
        sheet6.set_column(column, column, 11)  # V
        column += 1
        sheet6.set_column(column, column, 33)  # W
        column += 1
        sheet6.set_column(column, column, 31)  # X
        column += 1
        sheet6.set_column(column, column, 32)  # V
        column += 1
        sheet6.set_column(column, column, 26)  # W
        column += 1
        sheet6.set_column(column, column, 30)  # X
        column += 1
        columns_4 = column

        # 5. All materials consumed in production
        sheet6.set_column(column, column, 33)  # Y
        column += 1
        sheet6.set_column(column, column, 21)  # Z
        column += 1
        sheet6.set_column(column, column, 21)  # AA
        column += 1
        sheet6.set_column(column, column, 13)  # AB
        column += 1
        sheet6.set_column(column, column, 33)  # W
        column += 1
        sheet6.set_column(column, column, 27)  # X
        column += 1
        sheet6.set_column(column, column, 27)  # X
        column += 1
        columns_5 = column

        # 6. All materials in Incoming packaging
        sheet6.set_column(column, column, 33)  # H
        column += 1
        sheet6.set_column(column, column, 17)  # I
        column += 1
        sheet6.set_column(column, column, 13)  # J
        column += 1
        sheet6.set_column(column, column, 33)  # K
        column += 1
        sheet6.set_column(column, column, 33)  # W
        column += 1
        sheet6.set_column(column, column, 18)  # X
        column += 1
        sheet6.set_column(column, column, 18)  # X
        column += 1
        columns_6 = column

        # 7. Summary of all materials
        sheet6.set_column(column, column, 33)  # AC
        column += 1
        sheet6.set_column(column, column, 17)  # AD
        column += 1
        sheet6.set_column(column, column, 17)  # AE
        column += 1
        sheet6.set_column(column, column, 13)  # AF
        column += 1
        sheet6.set_column(column, column, 33)  # W
        column += 1
        sheet6.set_column(column, column, 27)  # X
        column += 1
        sheet6.set_column(column, column, 27)  # X
        column += 1
        columns_7 = column

        # 8. Workcenters Energy summary
        sheet6.set_column(column, column, 35)  # L
        column += 1
        sheet6.set_column(column, column, 18)  # M
        column += 1
        sheet6.set_column(column, column, 13)  # N
        column += 1
        columns_8 = column

        # 9. Operations Energy summary
        sheet6.set_column(column, column, 35)  # L
        column += 1
        sheet6.set_column(column, column, 18)  # M
        column += 1
        sheet6.set_column(column, column, 13)  # N
        column += 1
        columns_9 = column

        title_style_main_1 = workbook.add_format(
            {"bold": True, "bg_color": "#83B9F7", "bottom": 1}
        )
        title_style_main_1.set_align("center")
        title_style_main_1.set_align("vcenter")

        title_style_1 = workbook.add_format(
            {"bold": True, "bg_color": "AFCDFF", "bottom": 1}
        )

        # --------------------------------------------------------------------- #
        # ----------------- 1. Product Materials Summary ---------------------- #
        # --------------------------------------------------------------------- #

        sheet_title_6 = [
            _("Material"),  # 0 (A)
            _("Total amount (g)"),  # 1 (B)
            _("% of total"),  # 2 (C)
            _("Post-consumer material, weight % "),  # 3 (D)
        ]

        sheet6.merge_range(
            0,
            0,
            1,
            columns_1 - 1,
            _("1. Product Materials Summary"),
            title_style_main_1,
        )
        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_6):
            sheet6.write(2, title[0], title[1] or "", title_style_1)

        sheet6.freeze_panes(2, 0)

        # --------------------------------------------------------------------- #
        # ----------------- 2. Packaging Materials Summary -------------------- #
        # --------------------------------------------------------------------- #

        sheet_title_6_recyc = [
            _("Material"),
            _("Total amount (g)"),
            _("% of total"),
            _("Post-consumer material, weight %"),
        ]

        title_style_main_2 = workbook.add_format(
            {"bold": True, "bg_color": "#97E55C", "bottom": 1}
        )
        title_style_main_2.set_align("center")
        title_style_main_2.set_align("vcenter")

        title_style_sub_2 = workbook.add_format(
            {"bold": True, "bg_color": "#D9F776", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_1,
            1,
            columns_2 - 1,
            _("2. Packaging Materials Summary"),
            title_style_main_2,
        )
        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_6_recyc):
            sheet6.write(2, title[0] + columns_1, title[1] or "", title_style_sub_2)

        # --------------------------------------------------------------------- #
        # ------------------ 3. Product component materials ------------------- #
        # --------------------------------------------------------------------- #

        sheet_title_material_template = [
            _("Material"),
            _("Total amount (g)"),
            _("Weight, kg"),
            _("% of total"),
            _("Post-consumer material, weight %"),
            _("Renewable (Biogenic) % weight"),
            _("Renewable (Biogenic) Weight (kg)"),
            _("Biogenic carbon, weight-%"),
            _("Biogenic carbon, kg C/product"),
        ]

        sheet_title_content = [
            _("Product components"),
            _("Weight, kg"),
            _("Post-consumer material, weight-%"),
        ]

        title_style_main_7 = workbook.add_format(
            {"bold": True, "bg_color": "#CB93FC", "bottom": 1}
        )
        title_style_main_7.set_align("center")
        title_style_main_7.set_align("vcenter")

        title_style_sub_7 = workbook.add_format(
            {"bold": True, "bg_color": "#DFC3F7", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_2,
            1,
            columns_3 - 1,
            _("3. Product component materials"),
            title_style_main_7,
        )
        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_material_template):
            sheet6.write(2, title[0] + columns_2, title[1] or "", title_style_sub_7)

        # --------------------------------------------------------------------- #
        # --------------- 4. Delivery Packaging materials --------------------- #
        # --------------------------------------------------------------------- #

        sheet_title_material_template = [
            _("Material"),
            _("Total amount (g)"),
            _("Weight, kg"),
            _("% of total"),
            _("Post-consumer material, weight %"),
            _("Renewable (Biogenic) % weight"),
            _("Renewable (Biogenic) Weight (kg)"),
            _("Biogenic carbon, weight-%"),
            _("Biogenic carbon, kg C/product"),
        ]

        sheet_title_packaging_info = [
            _("Product components"),
            _("Weight, kg"),
            _("Weight-% (versus the product)"),
            _("Weight biogenic carbon, kg C/kg"),
        ]

        title_style_main_8 = workbook.add_format(
            {"bold": True, "bg_color": "#61B975", "bottom": 1}
        )
        title_style_main_8.set_align("center")
        title_style_main_8.set_align("vcenter")

        title_style_sub_8 = workbook.add_format(
            {"bold": True, "bg_color": "#92B099", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_3,
            1,
            columns_4 - 1,
            _("4. Delivery Packaging materials"),
            title_style_main_8,
        )
        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_material_template):
            sheet6.write(2, title[0] + columns_3, title[1] or "", title_style_sub_8)

        # --------------------------------------------------------------------- #
        # ----------- 5. All materials consumed in production ----------------- #
        # --------------------------------------------------------------------- #

        sheet_title_material_template = [
            _("Material"),
            _("Total amount (g)"),
            _("Weight, kg"),
            _("% of total"),
            _("Post-consumer material, weight %"),
            _("Renewable (Biogenic) % weight"),
            _("Biogenic carbon, kg C/product"),
        ]

        title_style_main_5 = workbook.add_format(
            {"bold": True, "bg_color": "#A8E669", "bottom": 1}
        )
        title_style_main_5.set_align("center")
        title_style_main_5.set_align("vcenter")

        title_style_sub_5 = workbook.add_format(
            {"bold": True, "bg_color": "#BAE58E", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_4,
            1,
            columns_5 - 1,
            _("5. All materials consumed in production"),
            title_style_main_5,
        )

        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_material_template):
            sheet6.write(2, title[0] + columns_4, title[1] or "", title_style_sub_5)

        # --------------------------------------------------------------------- #
        # ------------ 6. All materials in Incoming packaging ----------------- #
        # --------------------------------------------------------------------- #

        sheet_title_incoming_material = [
            _("Material"),
            _("Total amount (g)"),
            _("Weight, kg"),
            _("% of total"),
            _("Post-consumer material, weight %"),
            _("Waste flow"),
            _("Waste fate"),
        ]

        title_style_main_3 = workbook.add_format(
            {"bold": True, "bg_color": "#E2C0FF", "bottom": 1}
        )
        title_style_main_3.set_align("center")
        title_style_main_3.set_align("vcenter")

        title_style_sub_3 = workbook.add_format(
            {"bold": True, "bg_color": "#E8DCF2", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_5,
            1,
            columns_6 - 1,
            _("6. All materials in Incoming packaging"),
            title_style_main_3,
        )
        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_incoming_material):
            sheet6.write(2, title[0] + columns_5, title[1] or "", title_style_sub_3)

        # --------------------------------------------------------------------- #
        # ----------------- 7. Summary of all materials ----------------------- #
        # --------------------------------------------------------------------- #

        sheet_title_total_material = [
            _("Material"),
            _("Total amount (g)"),
            _("Weight, kg"),
            _("% of total"),
            _("Post-consumer material, weight %"),
            _("Biogenic carbon, weight-%"),
            _("Biogenic carbon, kg C/product"),
        ]

        title_style_main_6 = workbook.add_format(
            {"bold": True, "bg_color": "#938DE5", "bottom": 1}
        )
        title_style_main_6.set_align("center")
        title_style_main_6.set_align("vcenter")

        title_style_sub_6 = workbook.add_format(
            {"bold": True, "bg_color": "#C1BFDF", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_6,
            1,
            columns_7 - 1,
            _("7. Summary of all materials"),
            title_style_main_6,
        )

        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_total_material):
            sheet6.write(2, title[0] + columns_6, title[1] or "", title_style_sub_6)

        # --------------------------------------------------------------------- #
        # ---------------- 8. Workcenters Energy summary ---------------------- #
        # --------------------------------------------------------------------- #

        sheet_title_energy_work = [
            _("Workcenter"),  # 6 (G)
            _("Energy use (kwH)"),  # 7 (H)
            _("% of total"),  # 8 (I)
        ]

        title_style_main_4 = workbook.add_format(
            {"bold": True, "bg_color": "#FF5050", "bottom": 1}
        )
        title_style_main_4.set_align("center")
        title_style_main_4.set_align("vcenter")

        title_style_sub_4 = workbook.add_format(
            {"bold": True, "bg_color": "#FF7373", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_7,
            1,
            columns_8 - 1,
            _("8. Workcenters Energy summary"),
            title_style_main_4,
        )
        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_energy_work):
            sheet6.write(2, title[0] + columns_7, title[1] or "", title_style_sub_4)

        # --------------------------------------------------------------------- #
        # ------------- 9. Operations Energy summary -------------------------- #
        # --------------------------------------------------------------------- #

        sheet_title_energy_6 = [
            _("Process"),  # 6 (G)
            _("Energy use (kwH)"),  # 7 (H)
            _("% of total"),  # 8 (I)
        ]

        title_style_main_oper = workbook.add_format(
            {"bold": True, "bg_color": "#FF9537", "bottom": 1}
        )
        title_style_main_oper.set_align("center")
        title_style_main_oper.set_align("vcenter")

        title_style_sub_oper = workbook.add_format(
            {"bold": True, "bg_color": "#FFB675", "bottom": 1}
        )

        sheet6.merge_range(
            0,
            columns_8,
            1,
            columns_9 - 1,
            _("9. Operations Energy summary"),
            title_style_main_oper,
        )
        sheet6.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_energy_6):
            sheet6.write(2, title[0] + columns_8, title[1] or "", title_style_sub_oper)

        # -------------------------------------------------------------------- #

        a = 3
        b = 1
        c = 1
        d = 1

        accu = 2

        for o in objects:

            # --------------------------------------------------------------------- #
            # ------------------------------ Sheet 2 ------------------------------ #
            # --------------------------------------------------------------------- #

            product_variant = o._context.get("product_id")
            product_variant = product_variant and self.env["product.product"].browse(
                product_variant
            )

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet2.write(a, 0, "N/A")  # Internal category/display name
            sheet2.write(a, 1, "1")  # Level
            sheet2.write(
                a,
                2,
                o.product_id.default_code
                or (product_variant and product_variant.default_code)
                or "",
                bold,
            )  # Internal reference
            sheet2.write(a, 3, o.product_tmpl_id.name, bold)  # Name
            sheet2.write(a, 4, o.product_uom_id.name or "", bold)  # Unit
            sheet2.write(a, 5, o.product_qty, bold)  # Quantity in products

            main_vendor = o.product_id.seller_ids and o.product_id.seller_ids.filtered(
                lambda v: v.company_id == o.company_id
            )

            main_vendor = main_vendor and main_vendor[0] or ""

            if main_vendor:
                vendor = main_vendor.name.address_ids.filtered(
                    lambda r: r.type == "other"
                )
                vendor = vendor and vendor[0].name or ""
            else:
                vendor = ""

            main_vendor = (
                main_vendor
                and (
                    main_vendor[0].name.name,
                    "{}{}{}".format(
                        main_vendor[0].name.country_id.name,
                        main_vendor[0].name.street
                        and " {}".format(main_vendor[0].name.street)
                        or "",
                        main_vendor[0].name.city
                        and " {}".format(main_vendor[0].name.city)
                        or "",
                    )
                    or "",
                )
                or ("N/A", "N/A")
            )

            sheet2.write(a, 15, main_vendor[0], bold)  # Vendor
            sheet2.write(a, 16, main_vendor[1], bold)  # Vendor address
            sheet2.write(a, 17, vendor, bold)  # Supply address

            sheet2.write(
                a, 18, o.product_id.origin_country_id.name or "", bold
            )  # Country of origin

            j = 0

            material_variant = product_variant or o.product_tmpl_id.product_variant_id

            a = self.print_materials(
                product_id=material_variant,
                sheet2=sheet2,
                row=a,
                level=1,
                quantity=o.product_qty,
                parent_code="N/A",
                parent=o,
                upper_parent=material_variant,
                bom=o,
                center_cell=center_cell,
            )

            # --------------------------------------------------------------------- #
            # ------------------------------ Sheet 3 ------------------------------ #
            # --------------------------------------------------------------------- #

            self.print_by_products(
                sheet3,
                row=b,
                level=0,
                parent_level=1,
                bom=o,
                product_variant=product_variant,
                style=None,
                child_number=0,
            )

            # --------------------------------------------------------------------- #
            # ------------------------------ Sheet 4 ------------------------------ #
            # --------------------------------------------------------------------- #

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            self.operation_bom_consus(
                bom=o,
                product_variant=product_variant,
                sheet4=sheet4,
                row=c,
                level=j,
                parent_level=c,
                identifier=ident,
                style=None,
            )

            # --------------------------------------------------------------------- #
            # ------------------------------ Sheet 5 ------------------------------ #
            # --------------------------------------------------------------------- #

            sheet5_style = None

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet5.write(d, 0, "N/A", sheet5_style)  # Internal category/display name
            sheet5.write(d, 1, "1", sheet5_style)  # Level
            sheet5.write(
                d,
                2,
                o.product_id.default_code
                or (product_variant and product_variant.default_code)
                or "",
                sheet5_style,
            )  # Internal reference
            sheet5.write(d, 3, o.product_tmpl_id.name, sheet5_style)  # Name
            sheet5.write(d, 4, o.product_uom_id.name or "", sheet5_style)  # Unit

            parent_level_2 = 1
            parent_level_5 = 1

            j = 0

            material_variant = product_variant or o.product_tmpl_id.product_variant_id

            d = self.print_material_requirements(
                product_id=material_variant,
                sheet5=sheet5,
                row=d,
                level=1,
                quantity=o.product_qty,
                style=None,
                parent_code="N/A",
                parent=o,
            )

            def round_to_significant_figures(num, significant_figures):
                if num == 0:
                    return 0.0

                if abs(num) >= 1:
                    return round(num, significant_figures)

                exponent_position = math.floor(math.log10(abs(num)))

                decimal_places = significant_figures - exponent_position - 1

                return round(num, decimal_places)

            # --------------------------------------------------------------------- #
            # ------------------------------ Sheet 6 ------------------------------ #
            # --------------------------------------------------------------------- #

            # --------------------------------------------------------------------- #
            # ----------------- 1. Product Materials Summary ---------------------- #
            # --------------------------------------------------------------------- #

            # NOT IN INCOMING PACKAGING
            # IS NOT A DELIVERY PACKAGE

            ident = "{}".format(o.id)
            quantities = self.get_bom_quantities(o)

            materials_dict = {
                "materials_weight": 0,
                "wood_materials_weight": 0,
                "glue_materials_weight": 0,
                "metal_materials_weight": 0,
                "plastic_materials_weight": 0,
                "eee_materials_weight": 0,
                "oil_materials_weight": 0,
                "materials_recyc_weight": 0,
                "wood_materials_recyc_weight": 0,
                "glue_materials_recyc_weight": 0,
                "metal_materials_recyc_weight": 0,
                "plastic_materials_recyc_weight": 0,
                "eee_materials_recyc_weight": 0,
                "oil_materials_recyc_weight": 0,
            }

            materials_dict = self.product_material_summary(
                sheet6,
                bom=o,
                product_variant=material_variant,
                style=None,
                child_number=0,
                materials_dict=materials_dict,
            )

            total_wood_material_weight = materials_dict.get("wood_materials_weight", 0)
            total_wood_material_recyc = materials_dict.get(
                "wood_materials_recyc_weight", 0
            )
            total_glue_material_weight = materials_dict.get("glue_materials_weight", 0)
            total_glue_material_recyc = materials_dict.get(
                "glue_materials_recyc_weight", 0
            )
            total_metal_material_weight = materials_dict.get(
                "metal_materials_weight", 0
            )
            total_metal_material_recyc = materials_dict.get(
                "metal_materials_recyc_weight", 0
            )
            total_plastic_material_weight = materials_dict.get(
                "plastic_materials_weight", 0
            )
            total_plastic_material_recyc = materials_dict.get(
                "plastic_materials_recyc_weight", 0
            )
            total_eee_material_weight = materials_dict.get("eee_materials_weight", 0)
            total_eee_material_recyc = materials_dict.get(
                "eee_materials_recyc_weight", 0
            )
            total_oil_material_weight = materials_dict.get("oil_materials_weight", 0)
            total_oil_material_recyc = materials_dict.get(
                "oil_materials_recyc_weight", 0
            )

            total_material_weight = (
                total_wood_material_weight
                + total_glue_material_weight
                + total_metal_material_weight
                + total_plastic_material_weight
                + total_eee_material_weight
                + total_oil_material_weight
            )

            materials_dict.get("materials_recyc_weight", 0)

            sheet6.write(3, 0, "Wood")
            sheet6.write(
                3, 1, round_to_significant_figures(total_wood_material_weight, accu)
            )
            sheet6.write(
                3,
                2,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_wood_material_weight / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                3,
                3,
                round_to_significant_figures(
                    (
                        total_wood_material_weight
                        and (total_wood_material_recyc / total_wood_material_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(4, 0, "Glue")
            sheet6.write(
                4, 1, round_to_significant_figures(total_glue_material_weight, accu)
            )
            sheet6.write(
                4,
                2,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_glue_material_weight / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                4,
                3,
                round_to_significant_figures(
                    (
                        total_glue_material_weight
                        and (total_glue_material_recyc / total_glue_material_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(5, 0, "Metal")
            sheet6.write(
                5, 1, round_to_significant_figures(total_metal_material_weight, accu)
            )
            sheet6.write(
                5,
                2,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_metal_material_weight / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                5,
                3,
                round_to_significant_figures(
                    (
                        total_metal_material_weight
                        and (total_metal_material_recyc / total_metal_material_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(6, 0, "Plastic")
            sheet6.write(
                6, 1, round_to_significant_figures(total_plastic_material_weight, accu)
            )
            sheet6.write(
                6,
                2,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_plastic_material_weight / total_material_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                6,
                3,
                round_to_significant_figures(
                    (
                        total_plastic_material_weight
                        and (
                            total_plastic_material_recyc / total_plastic_material_weight
                        )
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(7, 0, "EEE")
            sheet6.write(
                7, 1, round_to_significant_figures(total_eee_material_weight, accu)
            )
            sheet6.write(
                7,
                2,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_eee_material_weight / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                7,
                3,
                round_to_significant_figures(
                    (
                        total_eee_material_weight
                        and (total_eee_material_recyc / total_eee_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(8, 0, "OIL")
            sheet6.write(
                8, 1, round_to_significant_figures(total_oil_material_weight, accu)
            )
            sheet6.write(
                8,
                2,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_oil_material_weight / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                8,
                3,
                round_to_significant_figures(
                    (
                        total_oil_material_weight
                        and (total_oil_material_recyc / total_oil_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(9, 0, "Total")
            total_all = (
                total_wood_material_weight
                + total_glue_material_weight
                + total_metal_material_weight
                + total_plastic_material_weight
                + total_eee_material_weight
                + total_oil_material_weight
            )
            total_all_recyc = (
                total_wood_material_recyc
                + total_glue_material_recyc
                + total_metal_material_recyc
                + total_plastic_material_recyc
                + total_eee_material_recyc
                + total_oil_material_recyc
            )
            sheet6.write(9, 1, round_to_significant_figures(total_all, accu))
            sheet6.write(
                9,
                2,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_all / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                9,
                3,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_all_recyc / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )

            # --------------------------------------------------------------------- #
            # ----------------- 2. Packaging Materials Summary -------------------- #
            # --------------------------------------------------------------------- #

            # NOT IN INCOMING PACKAGING
            # IS A DELIVERY PACKAGE

            ident = "{}".format(o.id)
            quantities = self.get_bom_quantities(o)

            materials_dict = {
                "materials_weight": 0,
                "cardboard_materials_weight": 0,
                "paper_materials_weight": 0,
                "plastic_materials_weight": 0,
                "metal_materials_weight": 0,
                "wood_materials_weight": 0,
                "materials_recyc_weight": 0,
                "cardboard_materials_recyc_weight": 0,
                "paper_materials_recyc_weight": 0,
                "plastic_materials_recyc_weight": 0,
                "metal_materials_recyc_weight": 0,
                "wood_materials_recyc_weight": 0,
            }

            materials_dict = self.packaging_material_summary(
                sheet6,
                bom=o,
                product_variant=material_variant,
                style=None,
                child_number=0,
                materials_dict=materials_dict,
            )

            total_cardboard_material_weight = materials_dict.get(
                "cardboard_materials_weight", 0
            )
            total_cardboard_material_recyc = materials_dict.get(
                "cardboard_materials_recyc_weight", 0
            )
            total_paper_material_weight = materials_dict.get(
                "paper_materials_weight", 0
            )
            total_paper_material_recyc = materials_dict.get(
                "paper_materials_recyc_weight", 0
            )
            total_plastic_material_weight = materials_dict.get(
                "plastic_materials_weight", 0
            )
            total_plastic_material_recyc = materials_dict.get(
                "plastic_materials_recyc_weight", 0
            )
            total_metal_material_weight = materials_dict.get(
                "metal_materials_weight", 0
            )
            total_metal_material_recyc = materials_dict.get(
                "metal_materials_recyc_weight", 0
            )
            total_wood_material_weight = materials_dict.get("wood_materials_weight", 0)
            total_wood_material_recyc = materials_dict.get(
                "wood_materials_recyc_weight", 0
            )

            total_material_weight = (
                total_cardboard_material_weight
                + total_paper_material_weight
                + total_plastic_material_weight
                + total_metal_material_weight
                + total_wood_material_weight
            )

            materials_dict.get("materials_recyc_weight", 0)

            sheet6.write(3, 4, "Cardboard")
            sheet6.write(
                3,
                5,
                round_to_significant_figures(total_cardboard_material_weight, accu),
            )
            sheet6.write(
                3,
                6,
                round_to_significant_figures(
                    (
                        (
                            total_material_weight
                            and total_cardboard_material_weight / total_material_weight
                            or 0
                        )
                        * 100
                    ),
                    accu,
                ),
            )
            sheet6.write(
                3,
                7,
                round_to_significant_figures(
                    (
                        total_cardboard_material_weight
                        and (
                            total_cardboard_material_recyc
                            / total_cardboard_material_weight
                        )
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(4, 4, "Paper")
            sheet6.write(
                4, 5, round_to_significant_figures(total_paper_material_weight, accu)
            )
            sheet6.write(
                4,
                6,
                round_to_significant_figures(
                    (
                        (
                            total_material_weight
                            and total_paper_material_weight / total_material_weight
                            or 0
                        )
                        * 100
                    ),
                    accu,
                ),
            )
            sheet6.write(
                4,
                7,
                round_to_significant_figures(
                    (
                        total_paper_material_weight
                        and (total_paper_material_recyc / total_paper_material_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(5, 4, "Plastic")
            sheet6.write(
                5, 5, round_to_significant_figures(total_plastic_material_weight, accu)
            )
            sheet6.write(
                5,
                6,
                round_to_significant_figures(
                    (
                        (
                            total_material_weight
                            and total_plastic_material_weight / total_material_weight
                            or 0
                        )
                        * 100
                    ),
                    accu,
                ),
            )
            sheet6.write(
                5,
                7,
                round_to_significant_figures(
                    (
                        total_plastic_material_weight
                        and (
                            total_plastic_material_recyc / total_plastic_material_weight
                        )
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(6, 4, "Metal")
            sheet6.write(
                6, 5, round_to_significant_figures(total_metal_material_weight, accu)
            )
            sheet6.write(
                6,
                6,
                round_to_significant_figures(
                    (
                        (
                            total_material_weight
                            and total_metal_material_weight / total_material_weight
                            or 0
                        )
                        * 100
                    ),
                    accu,
                ),
            )
            sheet6.write(
                6,
                7,
                round_to_significant_figures(
                    (
                        total_metal_material_weight
                        and (total_metal_material_recyc / total_metal_material_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(7, 4, "Wood")
            sheet6.write(
                7, 5, round_to_significant_figures(total_wood_material_weight, accu)
            )
            sheet6.write(
                7,
                6,
                round_to_significant_figures(
                    (
                        (
                            total_material_weight
                            and total_wood_material_weight / total_material_weight
                            or 0
                        )
                        * 100
                    ),
                    accu,
                ),
            )
            sheet6.write(
                7,
                7,
                round_to_significant_figures(
                    (
                        total_wood_material_weight
                        and (total_wood_material_recyc / total_wood_material_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(8, 4, "Total")
            total_all = (
                total_cardboard_material_weight
                + total_paper_material_weight
                + total_plastic_material_weight
                + total_metal_material_weight
                + total_wood_material_weight
            )
            total_all_recyc = (
                total_cardboard_material_recyc
                + total_paper_material_recyc
                + total_plastic_material_recyc
                + total_metal_material_recyc
                + total_wood_material_recyc
            )
            sheet6.write(8, 5, round_to_significant_figures(total_all, accu))
            sheet6.write(
                8,
                6,
                round_to_significant_figures(
                    (
                        (
                            total_material_weight
                            and total_all / total_material_weight
                            or 0
                        )
                        * 100
                    ),
                    accu,
                ),
            )
            sheet6.write(
                8,
                7,
                round_to_significant_figures(
                    (
                        total_material_weight
                        and (total_all_recyc / total_material_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )

            # --------------------------------------------------------------------- #
            # ------------------ 3. Product component materials ------------------- #
            # --------------------------------------------------------------------- #

            # NOT IN INCOMING PACKAGING
            # IS NOT A DELIVERY PACKAGE

            content_products = []

            content_products = self.all_material_summary(
                sheet6,
                bom=o,
                product_variant=material_variant,
                style=None,
                child_number=0,
                products=content_products,
            )

            name_and_weight = {}

            for product, qty, uom, bom, product_variant in content_products:
                materials = self.env["product.material.composition"].search(
                    domain=[
                        ("product_product_id", "=", product.id),
                        ("type", "!=", "product_packaging"),
                        ("is_delivery_package", "=", False),
                    ],
                )

                bom_product_id = (
                    product_variant or bom.product_tmpl_id.product_variant_id
                )

                multiply_with = 1

                if product.multiply_with_partial_weight:
                    multiply_with = (
                        product.weight and (bom_product_id.weight / product.weight) or 1
                    )

                if product.ignore_component_qty:
                    qty = 1

                qty = qty * multiply_with

                for material in materials:
                    product_material = material.product_material_id
                    if not name_and_weight.get(product_material):
                        name_and_weight[product_material] = [
                            material.net_weight * qty,
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty,
                            (product_material.biogenic_material_weight_percentage / 100)
                            * material.net_weight
                            * qty,
                            (product_material.renewable_weight_percentage / 100)
                            * material.net_weight
                            * qty,
                        ]
                    else:
                        name_and_weight[product_material][0] += (
                            material.net_weight * qty
                        )
                        name_and_weight[product_material][1] += (
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty
                        )
                        name_and_weight[product_material][2] += (
                            (product_material.biogenic_material_weight_percentage / 100)
                            * material.net_weight
                            * qty
                        )
                        name_and_weight[product_material][2] += (
                            (product_material.renewable_weight_percentage / 100)
                            * material.net_weight
                            * qty
                        )

            r = 3

            total_grouped_net_weight = 0

            for weight, _recyc, _biogenic, _renew in name_and_weight.values():
                total_grouped_net_weight += weight

            check_weight = 0
            total_grouped_recycled_weight = 0
            total_grouped_biogenic_weight = 0
            total_grouped_renewable_weight = 0

            name_and_weight = dict(
                sorted(
                    name_and_weight.items(),
                    key=lambda item: (item[0].name is None, str(item[0].name).lower()),
                )
            )

            for material, weight_recyc in name_and_weight.items():
                net_weight = weight_recyc[0]
                sheet6.write(r, 8, material.name)
                sheet6.write(r, 9, round_to_significant_figures(net_weight, accu))
                sheet6.write(
                    r, 10, round_to_significant_figures(net_weight * 0.001, accu)
                )  # weight in kg
                sheet6.write(
                    r,
                    11,
                    round_to_significant_figures(
                        (
                            total_grouped_net_weight
                            and (net_weight / total_grouped_net_weight) * 100
                            or 0
                        ),
                        accu,
                    ),
                )
                check_weight += net_weight

                total_grouped_recycled_weight += weight_recyc[1]
                sheet6.write(
                    r,
                    12,
                    round_to_significant_figures(
                        (net_weight and (weight_recyc[1] / net_weight) * 100 or 0), accu
                    ),
                )

                total_grouped_biogenic_weight += (
                    material.biogenic_material_weight_percentage / 100
                ) * net_weight

                total_grouped_renewable_weight += (
                    material.renewable_weight_percentage / 100
                ) * net_weight

                sheet6.write(
                    r,
                    13,
                    round_to_significant_figures(
                        (material.renewable_weight_percentage or 0), accu
                    ),
                )
                sheet6.write(
                    r,
                    14,
                    round_to_significant_figures(
                        (
                            (material.renewable_weight_percentage / 100)
                            * net_weight
                            * 0.001
                        ),
                        accu,
                    ),
                )

                sheet6.write(
                    r,
                    15,
                    round_to_significant_figures(
                        (material.biogenic_material_weight_percentage or 0), accu
                    ),
                )
                sheet6.write(
                    r,
                    16,
                    round_to_significant_figures(
                        (
                            (material.biogenic_material_weight_percentage / 100)
                            * net_weight
                            * 0.001
                        ),
                        accu,
                    ),
                )
                r += 1

            sheet6.write(r, 8, "Total")
            sheet6.write(
                r, 9, round_to_significant_figures(total_grouped_net_weight, accu)
            )
            sheet6.write(
                r,
                10,
                round_to_significant_figures(total_grouped_net_weight * 0.001, accu),
            )
            sheet6.write(
                r,
                11,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (check_weight / total_grouped_net_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                12,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_recycled_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )

            sheet6.write(
                r,
                13,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_renewable_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                14,
                round_to_significant_figures(
                    total_grouped_renewable_weight * 0.001, accu
                ),
            )

            sheet6.write(
                r,
                15,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_biogenic_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                16,
                round_to_significant_figures(
                    total_grouped_biogenic_weight * 0.001, accu
                ),
            )

            # --------------------------------------------------------------------- #
            # --------------- 4. Delivery Packaging materials --------------------- #
            # --------------------------------------------------------------------- #

            # NOT IN INCOMING PACKAGING
            # IS A DELIVERY PACKAGE

            pack_products = []

            pack_products = self.all_material_summary(
                sheet6,
                bom=o,
                product_variant=material_variant,
                style=None,
                child_number=0,
                products=pack_products,
            )

            name_and_weight = {}

            for product, qty, uom, bom, product_variant in pack_products:
                materials = self.env["product.material.composition"].search(
                    domain=[
                        ("product_product_id", "=", product.id),
                        ("type", "!=", "product_packaging"),
                        ("is_delivery_package", "=", True),
                    ],
                )

                for material in materials:
                    product_material = material.product_material_id
                    if not name_and_weight.get(product_material):
                        name_and_weight[product_material] = [
                            material.net_weight * qty,
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty,
                            (product_material.biogenic_material_weight_percentage / 100)
                            * material.net_weight
                            * qty,
                            (product_material.renewable_weight_percentage / 100)
                            * material.net_weight
                            * qty,
                        ]
                    else:
                        name_and_weight[product_material][0] += (
                            material.net_weight * qty
                        )
                        name_and_weight[product_material][1] += (
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty
                        )
                        name_and_weight[product_material][2] += (
                            (product_material.biogenic_material_weight_percentage / 100)
                            * material.net_weight
                            * qty
                        )
                        name_and_weight[product_material][2] += (
                            (product_material.renewable_weight_percentage / 100)
                            * material.net_weight
                            * qty
                        )

            r = 3

            total_grouped_net_weight = 0

            for weight, _recyc, _biogenic, _renew in name_and_weight.values():
                total_grouped_net_weight += weight

            check_weight = 0
            total_grouped_recycled_weight = 0
            total_grouped_biogenic_weight = 0
            total_grouped_renewable_weight = 0

            name_and_weight = dict(
                sorted(
                    name_and_weight.items(),
                    key=lambda item: (item[0].name is None, str(item[0].name).lower()),
                )
            )

            for material, weight_recyc in name_and_weight.items():
                net_weight = weight_recyc[0]
                sheet6.write(r, 17, material.name)
                sheet6.write(r, 18, round_to_significant_figures(net_weight, accu))
                sheet6.write(
                    r, 19, round_to_significant_figures(net_weight * 0.001, accu)
                )  # weight in kg
                sheet6.write(
                    r,
                    20,
                    round_to_significant_figures(
                        (
                            total_grouped_net_weight
                            and (net_weight / total_grouped_net_weight) * 100
                            or 0
                        ),
                        accu,
                    ),
                )
                check_weight += net_weight

                total_grouped_recycled_weight += weight_recyc[1]
                sheet6.write(
                    r,
                    21,
                    round_to_significant_figures(
                        (net_weight and (weight_recyc[1] / net_weight) * 100 or 0), accu
                    ),
                )

                total_grouped_renewable_weight += (
                    material.renewable_weight_percentage / 100
                ) * net_weight
                sheet6.write(
                    r,
                    22,
                    round_to_significant_figures(
                        material.renewable_weight_percentage or 0, accu
                    ),
                )
                sheet6.write(
                    r,
                    23,
                    round_to_significant_figures(
                        (
                            (material.renewable_weight_percentage / 100)
                            * net_weight
                            * 0.001
                        ),
                        accu,
                    ),
                )

                total_grouped_biogenic_weight += (
                    material.biogenic_material_weight_percentage / 100
                ) * net_weight
                sheet6.write(
                    r,
                    24,
                    round_to_significant_figures(
                        material.biogenic_material_weight_percentage or 0, accu
                    ),
                )
                sheet6.write(
                    r,
                    25,
                    round_to_significant_figures(
                        (
                            (material.biogenic_material_weight_percentage / 100)
                            * net_weight
                            * 0.001
                        ),
                        accu,
                    ),
                )

                r += 1

            sheet6.write(r, 17, "Total")
            sheet6.write(
                r, 18, round_to_significant_figures(total_grouped_net_weight, accu)
            )
            sheet6.write(
                r,
                19,
                round_to_significant_figures(total_grouped_net_weight * 0.001, accu),
            )
            sheet6.write(
                r,
                20,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (check_weight / total_grouped_net_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                21,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_recycled_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )

            sheet6.write(
                r,
                22,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_renewable_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                23,
                round_to_significant_figures(
                    total_grouped_renewable_weight * 0.001, accu
                ),
            )

            sheet6.write(
                r,
                24,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_biogenic_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                25,
                round_to_significant_figures(
                    total_grouped_biogenic_weight * 0.001, accu
                ),
            )

            # --------------------------------------------------------------------- #
            # ----------- 5. All materials consumed in production ----------------- #
            # --------------------------------------------------------------------- #

            # NOT IN INCOMING PACKAGING

            consu_oper_durat = []

            bom_consus = self.all_bom_consus(o, product_variant, consu_oper_durat)

            name_and_weight = {}
            time_in_year = o.company_id.time_in_year

            for consu_bom, oper_duration in bom_consus:
                consu_products = []

                consu_products = self.all_material_summary(
                    sheet6,
                    bom=consu_bom,
                    product_variant=material_variant,
                    style=None,
                    child_number=0,
                    products=consu_products,
                )

                for product, qty, uom, bom, product_variant in consu_products:
                    consu_materials = self.env["product.material.composition"].search(
                        domain=[
                            ("product_product_id", "=", product.id),
                            ("type", "!=", "product_packaging"),
                        ],
                    )

                    bom_product_id = (
                        product_variant or bom.product_tmpl_id.product_variant_id
                    )

                    multiply_with = 1

                    if product.multiply_with_partial_weight:
                        multiply_with = (
                            product.weight
                            and (bom_product_id.weight / product.weight)
                            or 1
                        )

                    if product.ignore_component_qty:
                        qty = 1

                    qty = qty * multiply_with

                    for material in consu_materials:
                        grams = self.env.ref("uom.product_uom_gram")

                        if (
                            uom.category_id.id
                            == self.env.ref("uom.product_uom_categ_kgm").id
                        ):
                            weight_in_grams = uom._compute_quantity(
                                material.net_weight * qty, grams, round=False
                            )
                        else:
                            weight_in_grams = (
                                material.net_weight_uom_id._compute_quantity(
                                    material.net_weight * qty, grams, round=False
                                )
                            )

                        if len(consu_materials) < 1:
                            weight_in_grams = product.weight_uom_id._compute_quantity(
                                product.weight * qty, grams, round=False
                            )

                        #  Check that time_in_year is not zero
                        consumed_weight = (
                            time_in_year
                            and ((weight_in_grams / time_in_year) * (oper_duration))
                            or 0
                        )

                        if not name_and_weight.get(material.product_material_id):
                            name_and_weight[material.product_material_id] = [
                                consumed_weight,
                                (material.recycled_percentage / 100) * consumed_weight,
                            ]
                        else:
                            name_and_weight[material.product_material_id][
                                0
                            ] += consumed_weight
                            name_and_weight[material.product_material_id][1] += (
                                material.recycled_percentage / 100
                            ) * consumed_weight

            r = 3

            total_grouped_net_weight = 0
            total_grouped_biogenic_weight = 0
            total_grouped_renewable_weight = 0

            for weight, _recyc in name_and_weight.values():
                total_grouped_net_weight += weight

            check_weight = 0
            total_grouped_recycled_weight = 0

            name_and_weight = dict(
                sorted(
                    name_and_weight.items(),
                    key=lambda item: (item[0].name is None, str(item[0].name).lower()),
                )
            )

            for material, weight_recyc in name_and_weight.items():
                net_weight = weight_recyc[0]
                sheet6.write(r, 26, material.name)
                sheet6.write(r, 27, round_to_significant_figures(net_weight, accu))
                sheet6.write(
                    r, 28, round_to_significant_figures(net_weight * 0.001, accu)
                )  # weight in kg
                sheet6.write(
                    r,
                    29,
                    round_to_significant_figures(
                        (
                            total_grouped_net_weight
                            and (net_weight / total_grouped_net_weight) * 100
                            or 0
                        ),
                        accu,
                    ),
                )
                check_weight += net_weight
                total_grouped_recycled_weight += weight_recyc[1]
                sheet6.write(
                    r,
                    30,
                    round_to_significant_figures(
                        (net_weight and (weight_recyc[1] / net_weight) * 100 or 0), accu
                    ),
                )

                total_grouped_biogenic_weight += (
                    material.biogenic_material_weight_percentage / 100
                ) * net_weight

                total_grouped_renewable_weight += (
                    material.renewable_weight_percentage / 100
                ) * net_weight

                sheet6.write(
                    r,
                    31,
                    round_to_significant_figures(
                        material.renewable_weight_percentage or 0, accu
                    ),
                )

                sheet6.write(
                    r,
                    32,
                    round_to_significant_figures(
                        (
                            (material.biogenic_material_weight_percentage / 100)
                            * net_weight
                            * 0.001
                        ),
                        accu,
                    ),
                )
                r += 1

            sheet6.write(r, 26, "Total")
            sheet6.write(
                r, 27, round_to_significant_figures(total_grouped_net_weight, accu)
            )
            sheet6.write(
                r,
                28,
                round_to_significant_figures(total_grouped_net_weight * 0.001, accu),
            )
            sheet6.write(
                r,
                29,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (check_weight / total_grouped_net_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                30,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_recycled_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )

            sheet6.write(
                r,
                31,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_renewable_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                32,
                round_to_significant_figures(
                    total_grouped_biogenic_weight * 0.001, accu
                ),
            )

            # --------------------------------------------------------------------- #
            # ------------ 6. All materials in Incoming packaging ----------------- #
            # --------------------------------------------------------------------- #

            # IS IN INCOMING PACKAGING

            products = []

            products = self.all_material_summary(
                sheet6,
                bom=o,
                product_variant=material_variant,
                style=None,
                child_number=0,
                products=products,
            )

            materials = self.env["product.material.composition"]
            name_and_weight = {}

            for product, qty, uom, bom, product_variant in products:
                materials = self.env["product.material.composition"].search(
                    domain=[
                        ("product_product_id", "=", product.id),
                        ("type", "=", "product_packaging"),
                    ],
                )

                for material in materials:
                    if not name_and_weight.get(material.product_material_id):
                        name_and_weight[material.product_material_id] = [
                            material.net_weight * qty,
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty,
                            material.product_material_waste_component_id,
                            material.product_material_waste_endpoint_id,
                        ]
                    else:
                        name_and_weight[material.product_material_id][0] += (
                            material.net_weight * qty
                        )
                        name_and_weight[material.product_material_id][1] += (
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty
                        )
                        name_and_weight[material.product_material_id][
                            2
                        ] += material.product_material_waste_component_id
                        name_and_weight[material.product_material_id][
                            3
                        ] += material.product_material_waste_endpoint_id

            r = 3

            total_grouped_net_weight = 0

            for weight, _recyc, _waste_comp, _waste_end in name_and_weight.values():
                total_grouped_net_weight += weight

            check_weight = 0
            total_grouped_recycled_weight = 0

            name_and_weight = dict(
                sorted(
                    name_and_weight.items(),
                    key=lambda item: (item[0].name is None, str(item[0].name).lower()),
                )
            )

            for material, weight_recyc in name_and_weight.items():
                sheet6.write(r, 33, material.name)
                sheet6.write(r, 34, round_to_significant_figures(weight_recyc[0], accu))
                sheet6.write(
                    r, 35, round_to_significant_figures(weight_recyc[0] * 0.001, accu)
                )  # weight in kg
                sheet6.write(
                    r,
                    36,
                    round_to_significant_figures(
                        (
                            total_grouped_net_weight
                            and (weight_recyc[0] / total_grouped_net_weight) * 100
                            or 0
                        ),
                        accu,
                    ),
                )
                check_weight += weight_recyc[0]
                total_grouped_recycled_weight += weight_recyc[1]
                sheet6.write(
                    r,
                    37,
                    round_to_significant_figures(
                        (
                            weight_recyc[0]
                            and (weight_recyc[1] / weight_recyc[0]) * 100
                            or 0
                        ),
                        accu,
                    ),
                )
                waste_component = weight_recyc[2] and weight_recyc[2][0].name or ""
                sheet6.write(r, 38, waste_component)
                waste_endpoint = weight_recyc[3] and weight_recyc[3][0].name or ""
                sheet6.write(r, 39, waste_endpoint)
                r += 1

            sheet6.write(r, 33, "Total")
            sheet6.write(
                r, 34, round_to_significant_figures(total_grouped_net_weight, accu)
            )
            sheet6.write(
                r,
                35,
                round_to_significant_figures(total_grouped_net_weight * 0.001, accu),
            )
            sheet6.write(
                r,
                36,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (check_weight / total_grouped_net_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                37,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_recycled_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )

            # --------------------------------------------------------------------- #
            # ----------------- 7. Summary of all materials ----------------------- #
            # --------------------------------------------------------------------- #

            products = []

            products = self.all_material_summary(
                sheet6,
                bom=o,
                product_variant=material_variant,
                style=None,
                child_number=0,
                products=products,
            )

            materials = self.env["product.material.composition"]
            name_and_weight = {}

            for product, qty, uom, bom, product_variant in products:
                materials = self.env["product.material.composition"].search(
                    domain=[
                        ("product_product_id", "=", product.id),
                    ],
                )

                bom_product_id = (
                    product_variant or bom.product_tmpl_id.product_variant_id
                )

                multiply_with = 1

                if product.multiply_with_partial_weight:
                    multiply_with = (
                        product.weight and (bom_product_id.weight / product.weight) or 1
                    )

                if product.ignore_component_qty:
                    qty = 1

                qty = qty * multiply_with

                for material in materials:
                    if not name_and_weight.get(material.product_material_id):
                        name_and_weight[material.product_material_id] = [
                            material.net_weight * qty,
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty,
                        ]
                    else:
                        name_and_weight[material.product_material_id][0] += (
                            material.net_weight * qty
                        )
                        name_and_weight[material.product_material_id][1] += (
                            (material.recycled_percentage / 100)
                            * material.net_weight
                            * qty
                        )

            r = 3

            total_grouped_net_weight = 0

            for weight, _recyc in name_and_weight.values():
                total_grouped_net_weight += weight

            check_weight = 0
            total_grouped_recycled_weight = 0
            total_grouped_biogenic_weight = 0

            name_and_weight = dict(
                sorted(
                    name_and_weight.items(),
                    key=lambda item: (item[0].name is None, str(item[0].name).lower()),
                )
            )

            for material, weight_recyc in name_and_weight.items():
                net_weight = weight_recyc[0]
                sheet6.write(r, 40, material.name)
                sheet6.write(r, 41, round_to_significant_figures(net_weight, accu))
                sheet6.write(
                    r, 42, round_to_significant_figures(net_weight * 0.001, accu)
                )  # weight in kg
                sheet6.write(
                    r,
                    43,
                    round_to_significant_figures(
                        (
                            total_grouped_net_weight
                            and (net_weight / total_grouped_net_weight) * 100
                            or 0
                        ),
                        accu,
                    ),
                )
                check_weight += net_weight
                total_grouped_recycled_weight += weight_recyc[1]
                sheet6.write(
                    r,
                    44,
                    round_to_significant_figures(
                        (net_weight and (weight_recyc[1] / net_weight) * 100 or 0), accu
                    ),
                )

                total_grouped_biogenic_weight += (
                    material.biogenic_material_weight_percentage / 100
                ) * net_weight
                sheet6.write(
                    r,
                    45,
                    round_to_significant_figures(
                        (material.biogenic_material_weight_percentage or 0), accu
                    ),
                )
                sheet6.write(
                    r,
                    46,
                    round_to_significant_figures(
                        (
                            (material.biogenic_material_weight_percentage / 100)
                            * net_weight
                            * 0.001
                        ),
                        accu,
                    ),
                )
                r += 1

            sheet6.write(r, 40, "Total")
            sheet6.write(
                r, 41, round_to_significant_figures(total_grouped_net_weight, accu)
            )
            sheet6.write(
                r,
                42,
                round_to_significant_figures(total_grouped_net_weight * 0.001, accu),
            )
            sheet6.write(
                r,
                43,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (check_weight / total_grouped_net_weight) * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                44,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_recycled_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                45,
                round_to_significant_figures(
                    (
                        total_grouped_net_weight
                        and (total_grouped_biogenic_weight / total_grouped_net_weight)
                        * 100
                        or 0
                    ),
                    accu,
                ),
            )
            sheet6.write(
                r,
                46,
                round_to_significant_figures(
                    total_grouped_biogenic_weight * 0.001, accu
                ),
            )

            # --------------------------------------------------------------------- #
            # ---------------- 8. Workcenters Energy summary ---------------------- #
            # --------------------------------------------------------------------- #

            operations = self.env["mrp.routing.workcenter"]

            operations = self.energy_summary(
                bom=o,
                product_variant=material_variant,
                sheet6=sheet6,
                operations=operations,
            )

            workcenter_and_energy = {}

            for oper in operations.sorted(key=lambda o: o.sequence):
                workcenter = oper.workcenter_id
                energy = (
                    (workcenter.energy_consumption * oper.duration_active)
                    + (workcenter.energy_consumption_passive * oper.duration_passive)
                ) / 60
                if not workcenter_and_energy.get(workcenter):
                    workcenter_and_energy[workcenter] = energy
                else:
                    workcenter_and_energy[workcenter] += energy
            t = 3

            total_grouped_energy = sum(workcenter_and_energy.values())

            for workcenter, energy in workcenter_and_energy.items():
                sheet6.write(t, 47, workcenter.name)
                sheet6.write(t, 48, energy)
                sheet6.write(
                    t,
                    49,
                    total_grouped_energy and (energy / total_grouped_energy) * 100,
                ) or 0
                t += 1

            # --------------------------------------------------------------------- #
            # ------------- 9. Operations Energy summary -------------------------- #
            # --------------------------------------------------------------------- #

            operations = self.env["mrp.routing.workcenter"]

            operations = self.energy_summary(
                bom=o,
                product_variant=material_variant,
                sheet6=sheet6,
                operations=operations,
            )

            operation_and_energy = {}

            for oper in operations.sorted(key=lambda o: o.sequence):
                workcenter = oper.workcenter_id
                energy = (
                    (workcenter.energy_consumption * oper.duration_active)
                    + (workcenter.energy_consumption_passive * oper.duration_passive)
                ) / 60
                if not operation_and_energy.get(oper):
                    operation_and_energy[oper] = energy
                else:
                    operation_and_energy[oper] += energy
            t = 3

            total_grouped_energy = sum(operation_and_energy.values())

            for operation, energy in operation_and_energy.items():
                sheet6.write(t, 50, operation.name)
                sheet6.write(t, 51, energy)
                sheet6.write(
                    t,
                    52,
                    total_grouped_energy and (energy / total_grouped_energy) * 100,
                ) or 0
                t += 1

            # --------------------------------------------------------------------- #

            child_number = 0
            for ch in o.bom_line_ids:
                if product_variant and ch._skip_bom_line(product_variant):
                    continue
                child_number += 1
                a = self.print_bom_children_2(
                    ch,
                    sheet2,
                    a,
                    j,
                    parent=o.product_tmpl_id,
                    parent_level=parent_level_2,
                    child_number=child_number,
                    quantities=quantities,
                    identifier=ident,
                    parent_bom=o,
                    upper_parent=product_variant,
                    center_cell=center_cell,
                )

                d = self.print_bom_children_5(
                    ch,
                    sheet5,
                    d,
                    j,
                    parent=o.product_tmpl_id,
                    parent_level=parent_level_5,
                    child_number=child_number,
                    quantities=quantities,
                    identifier=ident,
                )
