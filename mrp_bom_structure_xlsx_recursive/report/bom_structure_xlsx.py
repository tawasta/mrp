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

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        materials = self.env["product.material.composition"]

        for mater in ch.product_id.product_material_composition_ids:
            materials |= mater

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet2.write(a, 0, parent_with_code)  # Internal category/display name
        sheet2.write(a, 1, level)  # Level
        sheet2.write(a, 2, ch.product_id.default_code or "")  # Internal reference
        sheet2.write(a, 3, ch.product_tmpl_id.name)  # Name
        sheet2.write(a, 4, ch.product_id.uom_id.name)  # Unit
        sheet2.write(a, 5, ch.product_qty)  # Quantity in products

        classes = (
            str(m.product_material_class_id.name)
            for m in materials
            if m.product_material_class_id
        )
        classes = "\n".join(filter(None, classes))

        sheet2.write(a, 6, classes)  # Material class

        names = (str(m.name) for m in materials if m.name)
        names = "\n".join(filter(None, names))

        sheet2.write(a, 7, names)  # Material

        net_weights = (str(m.net_weight) for m in materials if m.net_weight)
        net_weights = "\n".join(filter(None, net_weights))

        sheet2.write(a, 8, net_weights)  # Material weight / per unit
        sheet2.write(a, 9, net_weights)  # Material total weight in product

        net_weight_uom = (
            str(m.net_weight_uom_id.name) for m in materials if m.net_weight_uom_id
        )
        net_weight_uom = "\n".join(filter(None, net_weight_uom))

        sheet2.write(a, 10, net_weight_uom)  # Net weight UoM

        recycled_percentage = (
            str(m.recycled_percentage) for m in materials if m.recycled_percentage
        )
        recycled_percentage = "\n".join(filter(None, recycled_percentage))

        sheet2.write(a, 11, recycled_percentage)  # Recycled material %

        waste_component = (
            str(m.product_material_waste_component_id.name)
            for m in materials
            if m.product_material_waste_component_id
        )
        waste_component = "\n".join(filter(None, waste_component))

        sheet2.write(a, 12, waste_component)  # Waste procuts

        waste_endpoint = (
            str(m.product_material_waste_endpoint_id.name)
            for m in materials
            if m.product_material_waste_endpoint_id
        )
        waste_endpoint = "\n".join(filter(None, waste_endpoint))

        sheet2.write(a, 13, waste_endpoint)  # Waste endpoint

        vendor = ch.product_id.seller_ids and ch.product_id.seller_ids.filtered(
            lambda r: r.name.type == "other"
        )
        vendor = (
            vendor
            and (
                vendor[0].name.name,
                "{}{}{}".format(
                    vendor[0].name.country_id.name,
                    vendor[0].name.street and " {}".format(vendor[0].name.street) or "",
                    vendor[0].name.city and " {}".format(vendor[0].name.city) or "",
                )
                or "",
            )
            or ("N/A", "N/A")
        )

        sheet2.write(a, 14, vendor[0])  # Vendor
        sheet2.write(a, 15, vendor[1])  # Supply address

        sheet2.write(
            a, 16, ch.product_id.origin_country_id.name or ""
        )  # Country of origin

        a += 1
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

    def print_bom_children_3(
        self,
        ch,
        sheet3,
        row,
        level,
        parent,
        parent_level,
        child_number,
        quantities,
        identifier,
    ):
        b, j = row, level
        j += 1

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        materials = self.env["product.material.composition"]

        for mater in ch.product_id.product_material_composition_ids:
            materials |= mater

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet3.write(b, 0, parent_with_code)  # Internal category/display name
        sheet3.write(b, 1, level)  # Level
        sheet3.write(b, 2, ch.product_id.name)  # Name
        sheet3.write(b, 3, ch.product_id.default_code or "")  # Internal reference

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        sheet3.write(b, 4, ch.operation_id.id or "")  # Operation ID

        sheet3.write(b, 5, ch.operation_id.name or "")  # Quantity in products

        electric_consumption = (
            ch.operation_id and ch.operation_id.workcenter_id.electric_consumption or 0
        )

        sheet3.write(
            b, 6, electric_consumption
        )  # Energy consumption during an operation / Total/(kWh)

        materials = self.env["product.material.composition"]

        for mater in ch.product_id.product_material_composition_ids:
            materials |= mater

        waste_component = (
            str(m.product_material_waste_component_id.name)
            for m in materials
            if m.product_material_waste_component_id
        )
        waste_component = "\n".join(filter(None, waste_component))

        sheet3.write(b, 7, waste_component)  # Waste product name

        waste_amount = (
            str(m.net_weight * m.recycled_percentage)
            for m in materials
            if m.net_weight and m.recycled_percentage
        )
        waste_amount = "\n".join(filter(None, waste_amount))

        sheet3.write(b, 8, waste_amount)  # Waste amount

        waste_unit = (
            str(m.net_weight_uom_id.name) for m in materials if m.net_weight_uom_id
        )
        waste_unit = "\n".join(filter(None, waste_unit))

        sheet3.write(b, 9, waste_unit)  # Waste unit

        b += 1
        child_number = 0
        for child in ch.child_line_ids:
            if child._skip_bom_line(ch.product_id):
                continue

            child_number += 1
            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            b = self.print_bom_children_3(
                child,
                sheet3,
                b,
                j,
                parent=ch.product_id,
                parent_level=level,
                child_number=child_number,
                quantities=quantities,
                identifier=ident,
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
    ):
        c, j = row, level
        j += 1

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        materials = self.env["product.material.composition"]

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        for mater in ch.product_id.product_material_composition_ids:
            materials |= mater

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet4.write(c, 0, ch.product_id.categ_id.name or "")  # Internal reference
        sheet4.write(c, 1, parent.default_code or "")  # Name
        sheet4.write(c, 2, parent_with_code)  # Internal category/display name
        sheet4.write(c, 3, operation.id or "")  # Operation ID
        sheet4.write(c, 4, operation.name or "")  # Operation name

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        sheet4.write(c, 5, ch.product_id.default_code or "")  # Internal reference
        sheet4.write(c, 6, ch.product_id.name)  # Name

        minutes_in_year = ch.company_id.minutes_in_year

        #  Check that minutes_in_year is not zero
        consumed_weight = (
            minutes_in_year
            and (
                (quantities[ident][1] * ch.product_id.weight / minutes_in_year)
                * ch.operation_id.time_cycle_manual
            )
            or 0
        )

        sheet4.write(
            c, 7, consumed_weight
        )  # Energy consumption during an operation / Total/(kWh)

        sheet4.write(c, 8, ch.product_uom_id.name or "")  # Unit

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

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        materials = self.env["product.material.composition"]

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        for mater in ch.product_id.product_material_composition_ids:
            materials |= mater

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet5.write(d, 0, parent_with_code)  # Internal category/display name
        sheet5.write(d, 1, level)  # Internal category/display name
        sheet5.write(d, 2, ch.product_id.default_code or "")  # Internal reference
        sheet5.write(d, 3, ch.product_id.name)  # Name
        sheet5.write(d, 4, ch.product_uom_id.name or "")  # Unit

        materials = self.env["product.material.composition"]

        for mater in ch.product_id.product_material_composition_ids:
            materials |= mater

        classes = (
            str(m.product_material_class_id.name)
            for m in materials
            if m.product_material_class_id
        )
        classes = "\n".join(filter(None, classes))

        sheet5.write(d, 5, classes)  # Material class

        names = (str(m.name) for m in materials if m.name)
        names = "\n".join(filter(None, names))

        sheet5.write(d, 6, names)  # Material
        sheet5.write(d, 7, ch.product_id.weight)  # Net weight in a product

        sheet5.write(d, 8, ch.product_id.weight_uom_id.name or "")  # Net weight Unit

        chemicals_compliant = (
            str(m.chemicals_compliant.name) for m in materials if m.chemicals_compliant
        )
        chemicals_compliant = "\n".join(filter(None, chemicals_compliant))

        sheet5.write(
            d, 9, chemicals_compliant or ""
        )  # Dangerous materials / Chemicals Compliant

        rohs_compliant = (
            str(m.rohs_compliant.name) for m in materials if m.rohs_compliant
        )
        rohs_compliant = "\n".join(filter(None, rohs_compliant))

        sheet5.write(d, 10, rohs_compliant or "")  # RoHS

        reach_compliant = (
            str(m.reach_compliant.name) for m in materials if m.reach_compliant
        )
        reach_compliant = "\n".join(filter(None, reach_compliant))

        sheet5.write(d, 11, reach_compliant or "")  # REACH

        scip_compliant = (
            str(m.scip_compliant.name) for m in materials if m.scip_compliant
        )
        scip_compliant = "\n".join(filter(None, scip_compliant))

        sheet5.write(d, 12, scip_compliant or "")  # SCIP

        pop_compliant = (
            str(m.pop_compliant.name) for m in materials if m.pop_compliant
        )
        pop_compliant = "\n".join(filter(None, pop_compliant))

        sheet5.write(d, 13, pop_compliant or "")  # POP (Persistant Organic Pollutants)

        halogen_compliant = (
            str(m.halogen_compliant.name) for m in materials if m.halogen_compliant
        )
        halogen_compliant = "\n".join(filter(None, halogen_compliant))

        sheet5.write(d, 14, halogen_compliant or "")  # Halogens

        conflict_area_minerals_compliant = (
            str(m.conflict_area_minerals_compliant.name)
            for m in materials
            if m.conflict_area_minerals_compliant
        )
        conflict_area_minerals_compliant = "\n".join(
            filter(None, conflict_area_minerals_compliant)
        )

        sheet5.write(
            d, 15, conflict_area_minerals_compliant or ""
        )  # Conflict Area Minerals

        recycled_percentage = (
            str(m.recycled_percentage) for m in materials if m.recycled_percentage
        )
        recycled_percentage = "\n".join(filter(None, recycled_percentage))

        sheet5.write(d, 16, recycled_percentage or "")  # Recycle material %

        product_material_waste_component_id = (
            str(m.product_material_waste_component_id.name)
            for m in materials
            if m.product_material_waste_component_id
        )
        product_material_waste_component_id = "\n".join(
            filter(None, product_material_waste_component_id)
        )

        sheet5.write(d, 17, product_material_waste_component_id or "")  # Waste product

        product_material_waste_endpoint_id = (
            str(m.product_material_waste_endpoint_id.name)
            for m in materials
            if m.product_material_waste_endpoint_id
        )
        product_material_waste_endpoint_id = "\n".join(
            filter(None, product_material_waste_endpoint_id)
        )

        sheet5.write(d, 18, product_material_waste_endpoint_id or "")  # Waste endpoint

        d += 1
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

    def generate_xlsx_report(self, workbook, data, objects):

        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 14.0"}
        )

        # ---------------------------- -#
        # ---------- Sheet 2 --------- -#
        # ---------------------------- -#

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
        sheet2.set_column(8, 8, 25)
        sheet2.set_column(9, 9, 25)
        sheet2.set_column(10, 10, 20)
        sheet2.set_column(11, 11, 20)
        sheet2.set_column(12, 12, 20)
        sheet2.set_column(13, 13, 20)
        sheet2.set_column(14, 14, 25)
        sheet2.set_column(15, 15, 25)
        sheet2.set_column(16, 16, 28)
        sheet2.set_column(17, 17, 20)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        sheet_title_2 = [
            _("Internal category/display name"),
            _("Level"),
            _("Internal reference"),
            _("Name"),
            _("Unit"),
            _("Quantity in products"),
            _("Material class"),
            _("Material"),
            _("Material weight / per unit"),
            _("Material total weight in product"),
            _("Weight unit"),
            _("Recycle material %"),
            _("Waste products"),
            _("Waste endpoint"),
            _("Vendor"),
            _("Supply address"),
            _("Country of origin"),
        ]

        sheet2.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_2):
            sheet2.write(1, title[0], title[1] or "", title_style_product_level)

        #        sheet2.write_row(1, 17, sheet_title_product_level, title_style_product_level)
        sheet2.freeze_panes(2, 0)

        # ---------------------------- -#
        # ---------- Sheet 3 --------- -#
        # ---------------------------- -#

        sheet3 = workbook.add_worksheet(_("BOM energy and by-products"))

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
        sheet3.set_column(6, 6, 35)
        sheet3.set_column(7, 7, 35)
        sheet3.set_column(8, 8, 25)
        sheet3.set_column(9, 9, 28)
        sheet3.set_column(10, 10, 18)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        sheet_title_3 = [
            _("Internal category/display name"),
            _("Level"),
            _("Product to which operation is done"),
            _("Product internal reference"),
            _("Operation ID"),
            _("Operation name"),
            _("Energy consumption during an operation / Total(kWh)"),
            _("Waste product name"),
            _("Waste amount"),
            _("Waste unit"),
        ]

        sheet3.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_3):
            sheet3.write(1, title[0], title[1] or "", title_style_product_level)

        sheet3.freeze_panes(2, 0)

        # ---------------------------- -#
        # ---------- Sheet 4 --------- -#
        # ---------------------------- -#

        sheet4 = workbook.add_worksheet(_("BOM operations and consumptions"))

        sheet4.set_landscape()
        sheet4.fit_to_pages(1, 0)
        sheet4.set_zoom(80)

        # Some column sizes changed to match their title
        sheet4.set_column(0, 0, 30)
        sheet4.set_column(1, 1, 25)
        sheet4.set_column(2, 2, 47)
        sheet4.set_column(3, 3, 18)
        sheet4.set_column(4, 4, 25)
        sheet4.set_column(5, 5, 35)
        sheet4.set_column(6, 6, 40)
        sheet4.set_column(7, 7, 30)
        sheet4.set_column(8, 8, 15)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        sheet_title_4 = [
            _("Internal category/display name"),
            _("Product internal reference"),
            _("Name"),
            _("Operation ID"),
            _("Operation name"),
            _("Operation consumptions product ID"),
            _("Name of the product consumed in an operation"),
            _("Consumed amount / produced 1 product"),
            _("Unit"),
        ]

        sheet4.set_row(0, None, None, {"collapsed": 1})

        for title in enumerate(sheet_title_4):
            sheet4.write(1, title[0], title[1] or "", title_style_product_level)

        sheet4.freeze_panes(2, 0)

        # ---------------------------- -#
        # ---------- Sheet 5 --------- -#
        # ---------------------------- -#

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
        sheet5.set_column(5, 5, 29)
        sheet5.set_column(6, 6, 29)
        sheet5.set_column(7, 7, 25)
        sheet5.set_column(8, 8, 20)
        sheet5.set_column(9, 9, 20)
        sheet5.set_column(10, 10, 20)
        sheet5.set_column(11, 11, 20)
        sheet5.set_column(12, 12, 20)
        sheet5.set_column(13, 13, 34)
        sheet5.set_column(14, 14, 20)
        sheet5.set_column(15, 15, 28)
        sheet5.set_column(16, 16, 20)
        sheet5.set_column(17, 17, 20)
        sheet5.set_column(18, 18, 20)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        sheet_title_5 = [
            _("Internal category/display name"),
            _("Level"),
            _("Product internal reference"),
            _("Name"),
            _("Unit"),
            _("Material class"),
            _("Material"),
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
            sheet5.write(1, title[0], title[1] or "", title_style_product_level)

        sheet5.freeze_panes(2, 0)

        a = 2
        b = 2
        c = 2
        d = 2

        ######################################################################

        for o in objects:
            product_variant = o._context.get("product_id")
            product_variant = product_variant and self.env["product.product"].browse(
                product_variant
            )

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            materials = self.env["product.material.composition"]

            for mater in o.product_id.product_material_composition_ids:
                materials |= mater

            sheet2.write(a, 0, "N/A")  # Internal category/display name
            sheet2.write(a, 1, "1")  # Level
            sheet2.write(
                a, 2, o.product_id.default_code or "", bold
            )  # Internal reference
            sheet2.write(a, 3, o.product_tmpl_id.name, bold)  # Name
            sheet2.write(a, 4, o.product_id.uom_id.name or "", bold)  # Unit
            sheet2.write(a, 5, o.product_qty, bold)  # Quantity in products

            classes = (
                str(m.product_material_class_id.name)
                for m in materials
                if m.product_material_class_id
            )
            classes = "\n".join(filter(None, classes))

            sheet2.write(a, 6, classes, bold)  # Material class

            names = (str(m.name) for m in materials if m.name)
            names = "\n".join(filter(None, names))

            sheet2.write(a, 7, names, bold)  # Material

            net_weights = (str(m.net_weight) for m in materials if m.net_weight)
            net_weights = "\n".join(filter(None, net_weights))

            sheet2.write(a, 8, net_weights, bold)  # Material weight / per unit
            sheet2.write(a, 9, net_weights, bold)  # Material total weight in product

            net_weight_uom = (
                str(m.net_weight_uom_id.name) for m in materials if m.net_weight_uom_id
            )
            net_weight_uom = "\n".join(filter(None, net_weight_uom))

            sheet2.write(
                a, 10, net_weight_uom, bold
            )  # Material total weight in product

            recycled_percentage = (
                str(m.recycled_percentage) for m in materials if m.recycled_percentage
            )
            recycled_percentage = "\n".join(filter(None, recycled_percentage))

            sheet2.write(a, 11, recycled_percentage, bold)  # Recycled material %

            waste_component = (
                str(m.product_material_waste_component_id.name)
                for m in materials
                if m.product_material_waste_component_id
            )
            waste_component = "\n".join(filter(None, waste_component))

            sheet2.write(a, 12, waste_component, bold)  # Waste procuts

            waste_endpoint = (
                str(m.product_material_waste_endpoint_id.name)
                for m in materials
                if m.product_material_waste_endpoint_id
            )
            waste_endpoint = "\n".join(filter(None, waste_endpoint))

            sheet2.write(a, 13, waste_endpoint, bold)  # Waste endpoint

            vendor = o.product_id.seller_ids and o.product_id.seller_ids.filtered(
                lambda r: r.name.type == "other"
            )
            vendor = (
                vendor
                and (
                    vendor[0].name.name,
                    "{}{}{}".format(
                        vendor[0].name.country_id.name,
                        vendor[0].name.street
                        and " {}".format(vendor[0].name.street)
                        or "",
                        vendor[0].name.city and " {}".format(vendor[0].name.city) or "",
                    )
                    or "",
                )
                or ("N/A", "N/A")
            )

            sheet2.write(a, 14, vendor[0], bold)  # Vendor
            sheet2.write(a, 15, vendor[1], bold)  # Supply address

            sheet2.write(
                a, 16, o.product_id.origin_country_id.name or "", bold
            )  # Country of origin

            # ---------------------------- -#
            # ---------- Sheet 3 --------- -#
            # ---------------------------- -#

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet3.write(b, 0, "N/A")  # Internal category/display name
            sheet3.write(b, 1, "1")  # Level
            sheet3.write(
                b, 2, o.product_tmpl_id.name, bold
            )  # Product to which operation is done
            sheet3.write(
                b, 3, o.product_id.default_code or "", bold
            )  # Product internal reference

            operations = self.env["mrp.routing.workcenter"]

            for oper in o.operation_ids:
                operations |= oper

            operation_ids = str(o.id for o in o.operation_ids)
            operation_ids = "\n".join(filter(None, operation_ids))

            sheet3.write(b, 4, "", bold)  # Operation ID

            operation_names = str(o.name for o in o.operation_ids)
            operation_names = "\n".join(filter(None, operation_names))

            sheet3.write(b, 5, "", bold)  # Operation name

            sheet3.write(
                b, 6, "", bold
            )  # Energy consumption during an operation / Total/(kWh)

            materials = self.env["product.material.composition"]

            for mater in o.product_id.product_material_composition_ids:
                materials |= mater

            sheet3.write(b, 7, waste_component, bold)  # Waste product name
            sheet3.write(b, 8, "N/A", bold)  # Waste amount
            sheet3.write(b, 9, "N/A", bold)  # Waste unit

            # Sheet 4

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            for oper in o.operation_ids:
                bom = oper.workcenter_id.bom_consu

                sheet4.write(
                    c, 0, bom.product_tmpl_id.categ_id.name or ""
                )  # Internal category/display name
                sheet4.write(
                    c, 1, bom.product_id.default_code or "", bold
                )  # Product internal reference
                sheet4.write(c, 2, bom.product_tmpl_id.name, bold)  # Name
                sheet4.write(c, 3, oper.id or "", bold)  # Operation ID
                sheet4.write(c, 4, oper.name or "", bold)  # Operation name

                sheet4.write(c, 5, "N/A", bold)  # Operation consumptions product ID

                sheet4.write(
                    c, 6, "N/A", bold
                )  # Name of the product consumed in an operation

                minutes_in_year = bom.company_id.minutes_in_year

                #  Check that minutes_in_year is not zero
                consumed_weight = (
                    minutes_in_year
                    and (
                        (bom.product_qty * bom.product_id.weight / minutes_in_year)
                        * oper.time_cycle_manual
                    )
                    or 0
                )

                # Operaatiossa kuluva määrä vuodessa
                # Teknisissä asetuksissa voi vaihtaa minuuttimäärää

                sheet4.write(
                    c, 7, consumed_weight, bold
                )  # Consumed amount / produced 1 product

                sheet4.write(c, 8, bom.product_uom_id.name or "", bold)  # Unit

                parent_level_4 = c - 1
                c += 1
                j = 0

                child_number = 0
                for ch in bom.bom_line_ids:
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
                    )

            # Sheet 5

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet5.write(d, 0, "N/A", bold)  # Internal category/display name
            sheet5.write(d, 1, "1", bold)  # Level
            sheet5.write(d, 2, "N/A", bold)  # Internal reference
            sheet5.write(d, 3, "N/A", bold)  # Name
            sheet5.write(d, 4, o.product_uom_id.name or "", bold)  # Unit

            materials = self.env["product.material.composition"]

            for mater in o.product_id.product_material_composition_ids:
                materials |= mater

            classes = (
                str(m.product_material_class_id.name)
                for m in materials
                if m.product_material_class_id
            )
            classes = "\n".join(filter(None, classes))

            sheet5.write(d, 5, classes, bold)  # Material class

            names = (str(m.name) for m in materials if m.name)
            names = "\n".join(filter(None, names))

            sheet5.write(d, 6, names, bold)  # Material
            sheet5.write(d, 7, o.product_id.weight, bold)  # Net weight in a product
            sheet5.write(
                d, 8, o.product_id.weight_uom_name or "", bold
            )  # Net weight Unit

            chemicals_compliant = (
                str(m.chemicals_compliant) for m in materials if m.chemicals_compliant
            )
            chemicals_compliant = "\n".join(filter(None, chemicals_compliant))

            sheet5.write(
                d, 9, chemicals_compliant or "", bold
            )  # Dangerous materials / Chemicals Compliant

            rohs_compliant = (
                str(m.rohs_compliant.name) for m in materials if m.rohs_compliant
            )
            rohs_compliant = "\n".join(filter(None, rohs_compliant))

            sheet5.write(d, 10, rohs_compliant or "", bold)  # RoHS

            reach_compliant = (
                str(m.reach_compliant.name) for m in materials if m.reach_compliant
            )
            reach_compliant = "\n".join(filter(None, reach_compliant))

            sheet5.write(d, 11, reach_compliant or "", bold)  # REACH

            scip_compliant = (
                str(m.scip_compliant.name) for m in materials if m.scip_compliant
            )
            scip_compliant = "\n".join(filter(None, scip_compliant))

            sheet5.write(d, 12, scip_compliant or "", bold)  # SCIP

            pop_compliant = (
                str(m.pop_compliant.name) for m in materials if m.pop_compliant
            )
            pop_compliant = "\n".join(filter(None, pop_compliant))

            sheet5.write(
                d, 13, pop_compliant or "", bold
            )  # POP (Persistant Organic Pollutants)

            halogen_compliant = (
                str(m.halogen_compliant.name) for m in materials if m.halogen_compliant
            )
            halogen_compliant = "\n".join(filter(None, halogen_compliant))

            sheet5.write(d, 14, halogen_compliant or "", bold)  # Halogens

            conflict_area_minerals_compliant = (
                str(m.conflict_area_minerals_compliant.name)
                for m in materials
                if m.conflict_area_minerals_compliant
            )
            conflict_area_minerals_compliant = "\n".join(
                filter(None, conflict_area_minerals_compliant)
            )

            sheet5.write(
                d, 15, conflict_area_minerals_compliant or "", bold
            )  # Conflict Area Minerals

            recycled_percentage = (
                str(m.recycled_percentage) for m in materials if m.recycled_percentage
            )
            recycled_percentage = "\n".join(filter(None, recycled_percentage))

            sheet5.write(d, 16, recycled_percentage or "", bold)  # Recycle material %

            product_material_waste_component_id = (
                str(m.product_material_waste_component_id.name)
                for m in materials
                if m.product_material_waste_component_id
            )
            product_material_waste_component_id = "\n".join(
                filter(None, product_material_waste_component_id)
            )

            sheet5.write(
                d, 17, product_material_waste_component_id or "", bold
            )  # Waste product

            product_material_waste_endpoint_id = (
                str(m.product_material_waste_endpoint_id.name)
                for m in materials
                if m.product_material_waste_endpoint_id
            )
            product_material_waste_endpoint_id = "\n".join(
                filter(None, product_material_waste_endpoint_id)
            )

            sheet5.write(
                d, 18, product_material_waste_endpoint_id or "", bold
            )  # Waste endpoint

            parent_level_2 = a - 1
            parent_level_3 = b - 1
            #            parent_level_4 = c - 1
            parent_level_5 = d - 1

            a += 1
            b += 1
            d += 1

            j = 0

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
                b = self.print_bom_children_3(
                    ch,
                    sheet3,
                    b,
                    j,
                    parent=o.product_tmpl_id,
                    parent_level=parent_level_3,
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

    def print_bom_children(
        self,
        ch,
        sheet,
        row,
        level,
        parent,
        parent_level,
        child_number,
        quantities,
        identifier,
    ):
        i, j = row, level
        j += 1

        ident = "{}{}{}".format(identifier, "0000", ch.id)
        level = "{}.{}".format(parent_level, child_number)

        parent_with_code = "{}{}".format(
            parent.default_code and "[" + parent.default_code + "] " or "", parent.name
        )

        sheet.write(i, 0, ch.product_id.default_code)
        sheet.write(i, 1, level)
        sheet.write(i, 2, ch.product_id.name)
        sheet.write(i, 3, parent_with_code)
        sheet.write(
            i,
            4,
            ", ".join(
                [attr.name for attr in ch.bom_product_template_attribute_value_ids]
            ),
        )
        sheet.write(i, 5, ch.product_id.manufacturer.name or "")
        sheet.write(i, 6, ch.product_id.manufacturer_pref or "")
        sheet.write(i, 7, quantities[ident][1])
        sheet.write(i, 8, ch.product_uom_id.name)
        sheet.write(
            i,
            9,
            ch.product_id.route_ids
            and ", ".join([route.name for route in ch.product_id.route_ids])
            or "",
        )
        sheet.write(i, 10, ch.product_id.categ_id.name)

        material_info = ""

        for mater in ch.product_id.product_material_composition_ids:
            if mater.name:
                if not material_info:
                    material_info += mater.name
                else:
                    material_info += "{}{}".format("\n\n", mater.name)

        sheet.write(i, 11, material_info or "")
        sheet.write(i, 12, ch.product_id.origin_country_id.name or "")
        sheet.write(
            i, 13, ", ".join([seller.name.name for seller in ch.product_id.seller_ids])
        )
        sheet.write(
            i,
            14,
            ch.product_id.seller_ids and ch.product_id.seller_ids[0].product_code or "",
        )
        sheet.write(i, 15, ch.product_id.weight)
        sheet.write(i, 16, ch.product_id.weight * quantities[ident][1])
        sheet.write(i, 17, ch.product_id.weight)
        sheet.write(i, 18, ch.product_id.weight * quantities[ident][1])
        i += 1
        child_number = 0
        for child in ch.child_line_ids:
            child_number += 1

            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            i = self.print_bom_children(
                child,
                sheet,
                i,
                j,
                parent=ch.product_id,
                parent_level=level,
                child_number=child_number,
                quantities=quantities,
                identifier=ident,
            )
        j -= 1
        return i

    def generate_xlsx_report_old(self, workbook, data, objects):

        sheet = workbook.add_worksheet(_("BOM Structure recursive"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)

        # Some column sizes changed to match their title
        sheet.set_column(0, 0, 18)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 3, 56)
        sheet.set_column(4, 4, 40)
        sheet.set_column(5, 5, 27)
        sheet.set_column(6, 6, 29)
        sheet.set_column(7, 7, 11)
        sheet.set_column(8, 8, 20)
        sheet.set_column(9, 9, 20)
        sheet.set_column(10, 10, 17)
        sheet.set_column(11, 11, 42)
        sheet.set_column(12, 12, 20)
        sheet.set_column(13, 13, 52)
        sheet.set_column(14, 14, 22)
        sheet.set_column(15, 15, 17)
        sheet.set_column(16, 16, 20)
        sheet.set_column(17, 17, 16)
        sheet.set_column(18, 18, 20)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        title_style_weight = workbook.add_format(
            {"bold": True, "bg_color": "#DEBF6B", "bottom": 1}
        )

        title_style_vendor = workbook.add_format(
            {"bold": True, "bg_color": "#A4AAFF", "bottom": 1}
        )

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        sheet_title_product_level = [
            _("Internal Reference"),
            _("Level"),
            _("Name"),
            _("Parent"),
            _("Apply on Variants"),
        ]

        sheet_title = [
            _("Manufacturer"),
            _("Manufacturer Product Code"),
            _("Quantity"),
            _("Unit of Measure"),
            _("Routes"),
            _("Internal Category"),
            _("Material"),
            _("Country of Origin"),
        ]

        sheet_title_vendor = [
            _("Vendors"),
            _("Primary Vendor Code"),
        ]

        sheet_title_weight = [
            _("Net weight"),
            _("Total net weight"),
            _("Gross weight"),
            _("Total gross weight"),
        ]

        sheet.set_row(0, None, None, {"collapsed": 1})
        sheet.write_row(1, 0, sheet_title_product_level, title_style_product_level)
        sheet.write_row(1, 5, sheet_title, title_style)
        sheet.write_row(1, 13, sheet_title_vendor, title_style_vendor)
        sheet.write_row(1, 15, sheet_title_weight, title_style_weight)
        sheet.freeze_panes(2, 0)

        i = 2

        for o in objects:
            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet.write(i, 0, o.product_id.default_code or "", bold)
            sheet.write(i, 1, "1", bold)
            sheet.write(i, 2, o.product_tmpl_id.name, bold)
            sheet.write(i, 3, "N/A")  # No parent, since it's the top level
            sheet.write(i, 4, "N/A")  # No Apply on Variants, since it's the top level
            sheet.write(i, 5, o.product_tmpl_id.manufacturer.name or "")
            sheet.write(i, 6, o.product_tmpl_id.manufacturer_pref or "")
            sheet.write(i, 7, o.product_qty, bold)
            sheet.write(i, 8, o.product_uom_id.name, bold)
            sheet.write(
                i, 9, ", ".join([route.name for route in o.product_tmpl_id.route_ids])
            )
            sheet.write(i, 10, o.product_tmpl_id.categ_id.name)

            material_info = ""

            for mater in o.product_id.product_material_composition_ids:
                if mater.name:
                    if not material_info:
                        material_info += mater.name
                    else:
                        material_info += "{}{}".format("\n\n", mater.name)

            sheet.write(i, 11, material_info or "", bold)
            sheet.write(i, 12, o.product_id.origin_country_id.name or "", bold)
            sheet.write(
                i,
                13,
                ", ".join(
                    [seller.name.name for seller in o.product_tmpl_id.seller_ids]
                ),
            )
            sheet.write(
                i,
                14,
                o.product_tmpl_id.seller_ids
                and o.product_tmpl_id.seller_ids[0].product_code
                or "",
            )
            sheet.write(i, 15, o.product_id.weight, bold)
            sheet.write(i, 16, o.product_id.weight * o.product_qty, bold)
            sheet.write(i, 17, o.product_id.weight, bold)
            sheet.write(i, 18, o.product_id.weight * o.product_qty, bold)

            parent_level = i - 1
            i += 1

            j = 0

            child_number = 0
            for ch in o.bom_line_ids:
                child_number += 1
                i = self.print_bom_children(
                    ch,
                    sheet,
                    i,
                    j,
                    parent=o.product_tmpl_id,
                    parent_level=parent_level,
                    child_number=child_number,
                    quantities=quantities,
                    identifier=ident,
                )
