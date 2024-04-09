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

            lines.append([ident, [bom_line, bom_line.product_qty * bom_factor_used]])

            if bom_line.child_bom_id:
                bom_factor_used = bom_line.product_qty * bom_factor_used
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
        self, product_id, sheet2, row, level, quantity, parent_code, parent
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
            sheet2.write(a, 9, mater.type)  # Material type
            sheet2.write(a, 10, mater.net_weight)  # Material weight / per unit
            sheet2.write(a, 11, mater.net_weight_uom_id.name)  # Net weight UoM
            sheet2.write(a, 12, mater.recycled_percentage)  # Recycled material %
            sheet2.write(
                a, 13, mater.product_material_waste_component_id.name
            )  # Waste procuts
            sheet2.write(
                a, 14, mater.product_material_waste_endpoint_id.name
            )  # Waste endpoint

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
            sheet4.write(c, 12, mater.type)  # Material type
            sheet4.write(c, 13, mater.net_weight)  # Material weight / per unit
            sheet4.write(c, 14, mater.net_weight_uom_id.name)  # Net weight UoM
            sheet4.write(c, 15, mater.recycled_percentage)  # Recycled material %
            sheet4.write(
                c, 16, mater.product_material_waste_component_id.name
            )  # Waste procuts
            sheet4.write(
                c, 17, mater.product_material_waste_endpoint_id.name
            )  # Waste endpoint

            time_in_year = parent.company_id.time_in_year

            grams = self.env.ref("uom.product_uom_gram")

            weight_in_grams = product_id.weight_uom_id._compute_quantity(
                product_id.weight, grams
            )

            #  Check that time_in_year is not zero
            consumed_weight = (
                time_in_year
                and (
                    (quantity * weight_in_grams / time_in_year)
                    * (oper.duration_total * 60)
                )
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
                d, 8, mater.net_weight, sheet5_style
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

        sheet2.write(a, 15, main_vendor[0])  # Vendor
        sheet2.write(a, 16, main_vendor[1])  # Vendor address
        sheet2.write(a, 17, vendor)  # Supply address

        sheet2.write(
            a, 18, ch.product_id.origin_country_id.name or ""
        )  # Country of origin

        a = self.print_materials(
            product_id=ch.product_id,
            sheet2=sheet2,
            row=a,
            level=level,
            quantity=quantities[ident][1],
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
            )
        j -= 1
        return a

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
            ch.product_id.weight, grams
        )

        #  Check that time_in_year is not zero
        consumed_weight = (
            time_in_year
            and (
                (quantities[ident][1] * weight_in_grams / time_in_year)
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
                    bom.product_id.weight, grams
                )
            elif bom.product_tmpl_id and bom.product_tmpl_id.weight:
                weight_in_grams = bom.product_tmpl_id.weight_uom_id._compute_quantity(
                    bom.product_tmpl_id.weight, grams
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
        sheet2.set_column(1, 1, 18)
        sheet2.set_column(2, 2, 20)
        sheet2.set_column(3, 3, 56)
        sheet2.set_column(4, 4, 15)
        sheet2.set_column(5, 6, 25)
        sheet2.set_column(7, 7, 28)
        sheet2.set_column(8, 9, 26)
        sheet2.set_column(10, 10, 22)
        sheet2.set_column(11, 11, 20)
        sheet2.set_column(12, 12, 20)
        sheet2.set_column(13, 13, 20)
        sheet2.set_column(14, 14, 25)
        sheet2.set_column(15, 15, 25)
        sheet2.set_column(16, 16, 28)
        sheet2.set_column(17, 17, 25)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
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
            _("Material weight / per unit"),  # 9 (K)
            _("Weight unit"),  # 10 (L)
            _("Recycle material %"),  # 11 (M)
            _("Waste products"),  # 12 (N)
            _("Waste endpoint"),  # 13 (O)
            _("Vendor"),  # 14 (P)
            _("Vendor Address"),  # 15 (Q)
            _("Supply Address"),  # 16 (R)
            _("Country of origin"),  # 17 (S)
        ]

        sheet2.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_2):
            sheet2.write(0, title[0], title[1] or "", title_style_product_level)

        sheet2.freeze_panes(2, 0)

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

        sheet3.freeze_panes(2, 0)

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

        sheet4.freeze_panes(2, 0)

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

        sheet5.freeze_panes(2, 0)

        a = 1
        b = 1
        c = 1
        d = 1

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

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

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

    # ************************************ #
    # *----------------------------------* #
    # *----- Code below is not used -----* #
    # *----------------------------------* #
    # ************************************ #


#    def print_bom_children(
#        self,
#        ch,
#        sheet,
#        row,
#        level,
#        parent,
#        parent_level,
#        child_number,
#        quantities,
#        identifier,
#    ):
#        i, j = row, level
#        j += 1
#
#        ident = "{}{}{}".format(identifier, "0000", ch.id)
#        level = "{}.{}".format(parent_level, child_number)
#
#        parent_with_code = "{}{}".format(
#            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
#        )
#
#        sheet.write(i, 0, ch.product_id.default_code)
#        sheet.write(i, 1, level)
#        sheet.write(i, 2, ch.product_id.name)
#        sheet.write(i, 3, parent_with_code)
#        sheet.write(
#            i,
#            4,
#            ", ".join(
#                [attr.name for attr in ch.bom_product_template_attribute_value_ids]
#            ),
#        )
#        sheet.write(i, 5, ch.product_id.manufacturer.name or "")
#        sheet.write(i, 6, ch.product_id.manufacturer_pref or "")
#        sheet.write(i, 7, quantities[ident][1])
#        sheet.write(i, 8, ch.product_uom_id.name)
#        sheet.write(
#            i,
#            9,
#            ch.product_id.route_ids
#            and ", ".join([route.name for route in ch.product_id.route_ids])
#            or "",
#        )
#        sheet.write(i, 10, ch.product_id.categ_id.name)
#
#        material_info = ""
#
#        for mater in ch.product_id.product_material_composition_ids:
#            if mater.name:
#                if not material_info:
#                    material_info += mater.name
#                else:
#                    material_info += "{}{}".format("\n\n", mater.name)
#
#        sheet.write(i, 11, material_info or "")
#        sheet.write(i, 12, ch.product_id.origin_country_id.name or "")
#        sheet.write(
#            i, 13, ", ".join([seller.name.name for seller in ch.product_id.seller_ids])
#        )
#        sheet.write(
#            i,
#            14,
#            ch.product_id.seller_ids and ch.product_id.seller_ids[0].product_code or "",
#        )
#        sheet.write(i, 15, ch.product_id.weight)
#        sheet.write(i, 16, ch.product_id.weight * quantities[ident][1])
#        sheet.write(i, 17, ch.product_id.weight)
#        sheet.write(i, 18, ch.product_id.weight * quantities[ident][1])
#        i += 1
#        child_number = 0
#        for child in ch.child_line_ids:
#            child_number += 1
#
#            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
#            ident = "{}{}{}".format(identifier, "0000", child_bom.id)
#
#            i = self.print_bom_children(
#                child,
#                sheet,
#                i,
#                j,
#                parent=ch.product_id,
#                parent_level=level,
#                child_number=child_number,
#                quantities=quantities,
#                identifier=ident,
#            )
#        j -= 1
#        return i
#
#    def generate_xlsx_report_old(self, workbook, data, objects):
#
#        sheet = workbook.add_worksheet(_("BOM Structure recursive"))
#        sheet.set_landscape()
#        sheet.fit_to_pages(1, 0)
#        sheet.set_zoom(80)
#
#        # Some column sizes changed to match their title
#        sheet.set_column(0, 0, 18)
#        sheet.set_column(1, 1, 12)
#        sheet.set_column(2, 3, 56)
#        sheet.set_column(4, 4, 40)
#        sheet.set_column(5, 5, 27)
#        sheet.set_column(6, 6, 29)
#        sheet.set_column(7, 7, 11)
#        sheet.set_column(8, 8, 20)
#        sheet.set_column(9, 9, 20)
#        sheet.set_column(10, 10, 17)
#        sheet.set_column(11, 11, 42)
#        sheet.set_column(12, 12, 20)
#        sheet.set_column(13, 13, 52)
#        sheet.set_column(14, 14, 22)
#        sheet.set_column(15, 15, 17)
#        sheet.set_column(16, 16, 20)
#        sheet.set_column(17, 17, 16)
#        sheet.set_column(18, 18, 20)
#
#        # Column styles
#        bold = workbook.add_format({"bold": True})
#
#        title_style = workbook.add_format(
#            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
#        )
#
#        title_style_weight = workbook.add_format(
#            {"bold": True, "bg_color": "#DEBF6B", "bottom": 1}
#        )
#
#        title_style_vendor = workbook.add_format(
#            {"bold": True, "bg_color": "#A4AAFF", "bottom": 1}
#        )
#
#        title_style_product_level = workbook.add_format(
#            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
#        )
#
#        sheet_title_product_level = [
#            _("Internal Reference"),
#            _("Level"),
#            _("Name"),
#            _("Parent"),
#            _("Apply on Variants"),
#        ]
#
#        sheet_title = [
#            _("Manufacturer"),
#            _("Manufacturer Product Code"),
#            _("Quantity"),
#            _("Unit of Measure"),
#            _("Routes"),
#            _("Internal Category"),
#            _("Material"),
#            _("Country of Origin"),
#        ]
#
#        sheet_title_vendor = [
#            _("Vendors"),
#            _("Primary Vendor Code"),
#        ]
#
#        sheet_title_weight = [
#            _("Net weight"),
#            _("Total net weight"),
#            _("Gross weight"),
#            _("Total gross weight"),
#        ]
#
#        sheet.set_row(0, None, None, {"collapsed": 1})
#        sheet.write_row(1, 0, sheet_title_product_level, title_style_product_level)
#        sheet.write_row(1, 5, sheet_title, title_style)
#        sheet.write_row(1, 13, sheet_title_vendor, title_style_vendor)
#        sheet.write_row(1, 15, sheet_title_weight, title_style_weight)
#        sheet.freeze_panes(2, 0)
#
#        i = 2
#
#        for o in objects:
#            ident = "{}".format(o.id)
#
#            quantities = self.get_bom_quantities(o)
#
#            sheet.write(i, 0, o.product_id.default_code or "", bold)
#            sheet.write(i, 1, "1", bold)
#            sheet.write(i, 2, o.product_tmpl_id.name, bold)
#            sheet.write(i, 3, "N/A")  # No parent, since it's the top level
#            sheet.write(i, 4, "N/A")  # No Apply on Variants, since it's the top level
#            sheet.write(i, 5, o.product_tmpl_id.manufacturer.name or "")
#            sheet.write(i, 6, o.product_tmpl_id.manufacturer_pref or "")
#            sheet.write(i, 7, o.product_qty, bold)
#            sheet.write(i, 8, o.product_uom_id.name, bold)
#            sheet.write(
#                i, 9, ", ".join([route.name for route in o.product_tmpl_id.route_ids])
#            )
#            sheet.write(i, 10, o.product_tmpl_id.categ_id.name)
#
#            material_info = ""
#
#            for mater in o.product_id.product_material_composition_ids:
#                if mater.name:
#                    if not material_info:
#                        material_info += mater.name
#                    else:
#                        material_info += "{}{}".format("\n\n", mater.name)
#
#            sheet.write(i, 11, material_info or "", bold)
#            sheet.write(i, 12, o.product_id.origin_country_id.name or "", bold)
#            sheet.write(
#                i,
#                13,
#                ", ".join(
#                    [seller.name.name for seller in o.product_tmpl_id.seller_ids]
#                ),
#            )
#            sheet.write(
#                i,
#                14,
#                o.product_tmpl_id.seller_ids
#                and o.product_tmpl_id.seller_ids[0].product_code
#                or "",
#            )
#            sheet.write(i, 15, o.product_id.weight, bold)
#            sheet.write(i, 16, o.product_id.weight * o.product_qty, bold)
#            sheet.write(i, 17, o.product_id.weight, bold)
#            sheet.write(i, 18, o.product_id.weight * o.product_qty, bold)
#
#            parent_level = i - 1
#            i += 1
#
#            j = 0
#
#            child_number = 0
#            for ch in o.bom_line_ids:
#                child_number += 1
#                i = self.print_bom_children(
#                    ch,
#                    sheet,
#                    i,
#                    j,
#                    parent=o.product_tmpl_id,
#                    parent_level=parent_level,
#                    child_number=child_number,
#                    quantities=quantities,
#                    identifier=ident,
#                )
