from collections import defaultdict

from odoo import _, models

# from odoo.exceptions import UserError


class ReportMrpBomStructureXlsxRecursiveStructure(models.AbstractModel):

    _name = "report.mrp_bom_structure_xlsx.recursive_structure"
    _description = "BOM Structure XLSX Report recursive"
    _inherit = "report.mrp_bom_structure_xlsx.bom_structure_xlsx"

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
        sheet.write(i, 17, ch.product_id.gross_weight)
        sheet.write(i, 18, ch.product_id.gross_weight * quantities[ident][1])
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
        sheet2.write(a, 1, ch.product_id.default_code or "")  # Internal reference
        sheet2.write(a, 2, ch.product_tmpl_id.name)  # Name
        sheet2.write(a, 3, ch.product_id.uom_id.name)  # Unit
        sheet2.write(a, 4, ch.product_qty)  # Quantity in products

        classes = (
            str(m.product_material_class_id.name)
            for m in materials
            if m.product_material_class_id
        )
        classes = "\n".join(filter(None, classes))

        sheet2.write(a, 5, classes)  # Material class

        names = (str(m.name) for m in materials if m.name)
        names = "\n".join(filter(None, names))

        sheet2.write(a, 6, names)  # Material

        net_weights = (str(m.net_weight) for m in materials if m.net_weight)
        net_weights = "\n".join(filter(None, net_weights))

        sheet2.write(a, 7, net_weights)  # Material weight / per unit
        sheet2.write(a, 8, net_weights)  # Material total weight in product

        recycled_percentage = (
            str(m.recycled_percentage) for m in materials if m.recycled_percentage
        )
        recycled_percentage = "\n".join(filter(None, recycled_percentage))

        sheet2.write(a, 9, recycled_percentage)  # Recycled material %

        waste_component = (
            str(m.product_material_waste_component_id)
            for m in materials
            if m.product_material_waste_component_id
        )
        waste_component = "\n".join(filter(None, waste_component))

        sheet2.write(a, 10, waste_component)  # Waste procuts

        waste_endpoint = (
            str(m.product_material_waste_endpoint_id)
            for m in materials
            if m.product_material_waste_endpoint_id
        )
        waste_endpoint = "\n".join(filter(None, waste_endpoint))

        sheet2.write(a, 11, waste_endpoint)  # Waste endpoint
        sheet2.write(a, 12, "o.product_id.")  # Vendor
        sheet2.write(a, 13, "o.product_id.")  # Supply address
        sheet2.write(a, 14, ch.product_id.origin_country_id.name)  # Country of origin

        a += 1
        child_number = 0
        for child in ch.child_line_ids:
            child_number += 1

            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            a = self.print_bom_children(
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
        sheet3.write(b, 1, ch.product_id.name)  # Name
        sheet3.write(b, 2, ch.product_id.default_code or "")  # Internal reference

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        operations = self.env["mrp.routing.workcenter"]

        for oper in child_bom.operation_ids:
            operations |= oper

        operation_ids = str(o.id for o in child_bom.operation_ids)
        operation_ids = "\n".join(filter(None, operation_ids))

        sheet3.write(b, 3, operation_ids or "")  # Operation ID

        operation_names = str(o.name for o in child_bom.operation_ids)
        operation_names = "\n".join(filter(None, operation_names))

        sheet3.write(b, 4, operation_names or "")  # Quantity in products

        electric_consumption = str(
            o.workcenter_id.electric_consumption
            for o in child_bom.operation_ids
            if o.workcenter_id
        )
        electric_consumption = "\n".join(filter(None, electric_consumption))

        sheet3.write(
            b, 5, electric_consumption
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

        sheet3.write(b, 6, waste_component)  # Waste product name
        sheet3.write(b, 7, "")  # Waste amount
        sheet3.write(b, 8, "")  # Waste unit

        b += 1
        child_number = 0
        for child in ch.child_line_ids:
            child_number += 1

            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            b = self.print_bom_children(
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

        sheet4.write(c, 0, parent_with_code)  # Internal category/display name
        sheet4.write(c, 1, ch.product_id.default_code or "")  # Internal reference
        sheet4.write(c, 2, ch.product_id.name)  # Name

        operation_ids = str(o.id for o in child_bom.operation_ids)
        operation_ids = "\n".join(filter(None, operation_ids))

        sheet4.write(c, 3, operation_ids or "")  # Operation ID

        operation_names = str(o.name for o in child_bom.operation_ids)
        operation_names = "\n".join(filter(None, operation_names))

        sheet4.write(c, 4, operation_names or "")  # Operation name

        child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]

        bom_consu_prod_id = str(
            o.bom_consu.product_id.default_code
            for o in child_bom.operation_ids
            if o.bom_consu
        )
        bom_consu_prod_id = "\n".join(filter(None, bom_consu_prod_id))

        sheet4.write(c, 5, bom_consu_prod_id or "")  # Operation ID

        bom_consu_prod_name = str(
            o.bom_consu.product_id.name for o in child_bom.operation_ids if o.bom_consu
        )
        bom_consu_prod_name = "\n".join(filter(None, bom_consu_prod_name))

        sheet4.write(c, 6, bom_consu_prod_name or "")  # Quantity in products

        bom_consu_qty = str(
            o.bom_consu.product_qty for o in child_bom.operation_ids if o.bom_consu
        )
        bom_consu_qty = "\n".join(filter(None, bom_consu_qty))

        sheet4.write(
            c, 7, bom_consu_qty
        )  # Energy consumption during an operation / Total/(kWh)
        sheet4.write(c, 8, ch.product_uom_id.name or "")  # Unit

        c += 1
        child_number = 0
        for child in ch.child_line_ids:
            child_number += 1

            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            c = self.print_bom_children(
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
        sheet5.write(d, 1, ch.product_id.default_code or "")  # Internal reference
        sheet5.write(d, 2, ch.product_id.name)  # Name
        sheet5.write(d, 3, ch.product_uom_id.name or "")  # Unit

        materials = self.env["product.material.composition"]

        for mater in ch.product_id.product_material_composition_ids:
            materials |= mater

        classes = (
            str(m.product_material_class_id.name)
            for m in materials
            if m.product_material_class_id
        )
        classes = "\n".join(filter(None, classes))

        sheet5.write(d, 4, classes)  # Material class

        names = (str(m.name) for m in materials if m.name)
        names = "\n".join(filter(None, names))

        sheet5.write(d, 5, names)  # Material
        sheet5.write(d, 6, "")  # Net weight in a product

        bom_consu_prod_name = str(
            o.bom_consu.product_id.name for o in child_bom.operation_ids if o.bom_consu
        )
        bom_consu_prod_name = "\n".join(filter(None, bom_consu_prod_name))

        sheet5.write(d, 7, bom_consu_prod_name or "")  # Net weight Unit

        chemicals_compliant = (
            str(m.chemicals_compliant) for m in materials if m.chemicals_compliant
        )
        chemicals_compliant = "\n".join(filter(None, chemicals_compliant))

        sheet5.write(
            d, 8, chemicals_compliant or ""
        )  # Dangerous materials / Chemicals Compliant

        rohs_compliant = (
            str(m.rohs_compliant.name) for m in materials if m.rohs_compliant
        )
        rohs_compliant = "\n".join(filter(None, rohs_compliant))

        sheet5.write(d, 9, rohs_compliant or "")  # RoHS

        reach_compliant = (
            str(m.reach_compliant.name) for m in materials if m.reach_compliant
        )
        reach_compliant = "\n".join(filter(None, reach_compliant))

        sheet5.write(d, 10, reach_compliant or "")  # REACH

        scip_compliant = (
            str(m.scip_compliant.name) for m in materials if m.scip_compliant
        )
        scip_compliant = "\n".join(filter(None, scip_compliant))

        sheet5.write(d, 11, scip_compliant or "")  # SCIP

        pop_compliant = (
            str(m.pop_compliant.name) for m in materials if m.pop_compliant
        )
        pop_compliant = "\n".join(filter(None, pop_compliant))

        sheet5.write(d, 12, pop_compliant or "")  # POP (Persistant Organic Pollutants)

        halogen_compliant = (
            str(m.halogen_compliant.name) for m in materials if m.halogen_compliant
        )
        halogen_compliant = "\n".join(filter(None, halogen_compliant))

        sheet5.write(d, 13, halogen_compliant or "")  # Halogens

        conflict_area_minerals_compliant = (
            str(m.conflict_area_minerals_compliant.name)
            for m in materials
            if m.conflict_area_minerals_compliant
        )
        conflict_area_minerals_compliant = "\n".join(
            filter(None, conflict_area_minerals_compliant)
        )

        sheet5.write(
            d, 14, conflict_area_minerals_compliant or ""
        )  # Conflict Area Minerals

        recycled_percentage = (
            str(m.recycled_percentage) for m in materials if m.recycled_percentage
        )
        recycled_percentage = "\n".join(filter(None, recycled_percentage))

        sheet5.write(d, 15, recycled_percentage or "")  # Recycle material %

        product_material_waste_component_id = (
            str(m.product_material_waste_component_id.name)
            for m in materials
            if m.product_material_waste_component_id
        )
        product_material_waste_component_id = "\n".join(
            filter(None, product_material_waste_component_id)
        )

        sheet5.write(d, 16, product_material_waste_component_id or "")  # Waste product

        product_material_waste_endpoint_id = (
            str(m.product_material_waste_endpoint_id.name)
            for m in materials
            if m.product_material_waste_endpoint_id
        )
        product_material_waste_endpoint_id = "\n".join(
            filter(None, product_material_waste_endpoint_id)
        )

        sheet5.write(d, 17, product_material_waste_endpoint_id or "")  # Waste endpoint

        d += 1
        child_number = 0
        for child in ch.child_line_ids:
            child_number += 1

            child_bom = ch.product_id.bom_ids and ch.product_id.bom_ids[0]
            ident = "{}{}{}".format(identifier, "0000", child_bom.id)

            d = self.print_bom_children(
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

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        title_style = workbook.add_format(
            {"bold": True, "bg_color": "#FFFFCC", "bottom": 1}
        )

        title_style_weight = workbook.add_format(
            {"bold": True, "bg_color": "#DEBF6B", "bottom": 1}
        )

        title_style_vendor = workbook.add_format(
            {"bold": True, "bg_color": "#A4AAFF", "bottom": 1}
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

        # ---------------------------- -#
        # ---------- Sheet 2 --------- -#
        # ---------------------------- -#

        sheet2 = workbook.add_worksheet(_("BOM materials"))

        sheet2.set_landscape()
        sheet2.fit_to_pages(1, 0)
        sheet2.set_zoom(80)

        # Some column sizes changed to match their title
        sheet2.set_column(0, 0, 56)
        sheet2.set_column(1, 1, 20)
        sheet2.set_column(2, 2, 56)
        sheet2.set_column(3, 3, 15)
        sheet2.set_column(4, 5, 25)
        sheet2.set_column(6, 6, 28)
        sheet2.set_column(7, 7, 25)
        sheet2.set_column(8, 8, 25)
        sheet2.set_column(9, 9, 20)
        sheet2.set_column(10, 10, 20)
        sheet2.set_column(11, 11, 20)
        sheet2.set_column(12, 12, 20)
        sheet2.set_column(13, 13, 25)
        sheet2.set_column(14, 14, 25)
        sheet2.set_column(15, 15, 28)
        sheet2.set_column(16, 16, 20)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        sheet_title_2 = [
            _("Internal category/display name"),
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
        sheet3.set_column(1, 1, 35)
        sheet3.set_column(2, 2, 25)
        sheet3.set_column(3, 3, 20)
        sheet3.set_column(4, 4, 48)
        sheet3.set_column(5, 5, 35)
        sheet3.set_column(6, 6, 35)
        sheet3.set_column(7, 7, 25)
        sheet3.set_column(8, 8, 28)
        sheet3.set_column(9, 9, 18)

        # Column styles
        bold = workbook.add_format({"bold": True})

        title_style_product_level = workbook.add_format(
            {"bold": True, "bg_color": "#C6FF8D", "bottom": 1}
        )

        sheet_title_3 = [
            _("Internal category/display name"),
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
        sheet4.set_column(0, 0, 18)
        sheet4.set_column(1, 1, 12)
        sheet4.set_column(2, 3, 56)
        sheet4.set_column(4, 4, 40)
        sheet4.set_column(5, 5, 27)
        sheet4.set_column(6, 6, 29)
        sheet4.set_column(7, 7, 11)
        sheet4.set_column(8, 8, 20)
        sheet4.set_column(9, 9, 20)

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
        sheet5.set_column(0, 0, 18)
        sheet5.set_column(1, 1, 12)
        sheet5.set_column(2, 3, 56)
        sheet5.set_column(4, 4, 40)
        sheet5.set_column(5, 5, 27)
        sheet5.set_column(6, 6, 29)
        sheet5.set_column(7, 7, 11)
        sheet5.set_column(8, 8, 20)
        sheet5.set_column(9, 9, 20)
        sheet5.set_column(10, 10, 20)
        sheet5.set_column(11, 11, 20)
        sheet5.set_column(12, 12, 20)
        sheet5.set_column(13, 13, 20)
        sheet5.set_column(14, 14, 20)
        sheet5.set_column(15, 15, 20)
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

        i = 2
        a = 2
        b = 2
        c = 2
        d = 2

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
            sheet.write(i, 17, o.product_id.gross_weight, bold)
            sheet.write(i, 18, o.product_id.gross_weight * o.product_qty, bold)

            ######################################################################

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            materials = self.env["product.material.composition"]

            for mater in o.product_id.product_material_composition_ids:
                materials |= mater

            sheet2.write(a, 0, "N/A")  # Internal category/display name
            sheet2.write(
                a, 1, o.product_id.default_code or "", bold
            )  # Internal reference
            sheet2.write(a, 2, o.product_tmpl_id.name, bold)  # Name
            sheet2.write(a, 3, o.product_id.uom_id.name, bold)  # Unit
            sheet2.write(a, 4, o.product_qty, bold)  # Quantity in products

            classes = (
                str(m.product_material_class_id.name)
                for m in materials
                if m.product_material_class_id
            )
            classes = "\n".join(filter(None, classes))

            sheet2.write(a, 5, classes, bold)  # Material class

            names = (str(m.name) for m in materials if m.name)
            names = "\n".join(filter(None, names))

            sheet2.write(a, 6, names, bold)  # Material

            net_weights = (str(m.net_weight) for m in materials if m.net_weight)
            net_weights = "\n".join(filter(None, net_weights))

            sheet2.write(a, 7, net_weights, bold)  # Material weight / per unit
            sheet2.write(a, 8, net_weights, bold)  # Material total weight in product

            recycled_percentage = (
                str(m.recycled_percentage) for m in materials if m.recycled_percentage
            )
            recycled_percentage = "\n".join(filter(None, recycled_percentage))

            sheet2.write(a, 9, recycled_percentage, bold)  # Recycled material %

            waste_component = (
                str(m.product_material_waste_component_id.name)
                for m in materials
                if m.product_material_waste_component_id
            )
            waste_component = "\n".join(filter(None, waste_component))

            sheet2.write(a, 10, waste_component, bold)  # Waste procuts

            waste_endpoint = (
                str(m.product_material_waste_endpoint_id.name)
                for m in materials
                if m.product_material_waste_endpoint_id
            )
            waste_endpoint = "\n".join(filter(None, waste_endpoint))

            sheet2.write(a, 11, waste_endpoint, bold)  # Waste endpoint
            sheet2.write(a, 12, "o.product_id.", bold)  # Vendor
            sheet2.write(a, 13, "o.product_id.", bold)  # Supply address
            sheet2.write(
                a, 14, o.product_id.origin_country_id.name, bold
            )  # Country of origin

            # ---------------------------- -#
            # ---------- Sheet 3 --------- -#
            # ---------------------------- -#

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet3.write(b, 0, "N/A")  # Internal category/display name
            sheet3.write(b, 1, o.product_id.name, bold)  # Name
            sheet3.write(b, 2, o.product_id.default_code, bold)  # Internal reference

            operations = self.env["mrp.routing.workcenter"]

            for oper in o.operation_ids:
                operations |= oper

            operation_ids = str(o.id for o in o.operation_ids)
            operation_ids = "\n".join(filter(None, operation_ids))

            sheet3.write(b, 3, operation_ids or "", bold)  # Operation ID

            operation_names = str(o.name for o in o.operation_ids)
            operation_names = "\n".join(filter(None, operation_names))

            sheet3.write(b, 4, operation_names or "", bold)  # Operation name

            electric_consumption = str(
                o.workcenter_id.electric_consumption
                for o in o.operation_ids
                if o.workcenter_id
            )
            electric_consumption = "\n".join(filter(None, electric_consumption))

            sheet3.write(
                b, 5, electric_consumption, bold
            )  # Energy consumption during an operation / Total/(kWh)

            materials = self.env["product.material.composition"]

            for mater in o.product_id.product_material_composition_ids:
                materials |= mater

            sheet3.write(b, 6, waste_component, bold)  # Waste product name
            sheet3.write(b, 7, "materials", bold)  # Waste amount
            sheet3.write(b, 8, "materials", bold)  # Waste unit

            # Sheet 4

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet4.write(
                c, 0, o.product_tmpl_id.categ_id.name
            )  # Internal category/display name
            sheet4.write(
                c, 1, o.product_id.default_code, bold
            )  # Product internal reference
            sheet4.write(c, 2, o.product_id.name, bold)  # Name
            sheet4.write(c, 3, operation_ids or "", bold)  # Operation ID
            sheet4.write(c, 4, operation_names or "", bold)  # Operation name

            bom_consu_prod_id = str(
                o.bom_consu.product_id.default_code
                for o in o.operation_ids
                if o.bom_consu
            )
            bom_consu_prod_id = "\n".join(filter(None, bom_consu_prod_id))

            sheet4.write(
                c, 5, bom_consu_prod_id or "", bold
            )  # Operation consumptions product ID

            bom_consu_prod_name = str(
                o.bom_consu.product_id.name for o in o.operation_ids if o.bom_consu
            )
            bom_consu_prod_name = "\n".join(filter(None, bom_consu_prod_name))

            sheet4.write(
                c, 6, bom_consu_prod_name or "", bold
            )  # Name of the product consumed in an operation

            bom_consu_qty = str(
                o.bom_consu.product_qty for o in o.operation_ids if o.bom_consu
            )
            bom_consu_qty = "\n".join(filter(None, bom_consu_qty))
            # Operaatiossa kuluva määrä vuodessa
            # Teknisissä asetuksissa voi vaihtaa minuuttimäärää

            sheet4.write(
                c, 7, bom_consu_qty or "", bold
            )  # Consumed amount / produced 1 product
            sheet4.write(c, 8, o.product_uom_id.name or "", bold)  # Unit

            # Sheet 5

            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet5.write(
                d, 0, o.product_tmpl_id.categ_id.name, bold
            )  # Internal category/display name
            sheet5.write(d, 1, o.product_id.default_code, bold)  # Internal reference
            sheet5.write(d, 2, o.product_id.name, bold)  # Name
            sheet5.write(d, 3, o.product_uom_id.name or "", bold)  # Unit

            materials = self.env["product.material.composition"]

            for mater in o.product_id.product_material_composition_ids:
                materials |= mater

            classes = (
                str(m.product_material_class_id.name)
                for m in materials
                if m.product_material_class_id
            )
            classes = "\n".join(filter(None, classes))

            sheet5.write(d, 4, classes, bold)  # Material class

            names = (str(m.name) for m in materials if m.name)
            names = "\n".join(filter(None, names))

            sheet5.write(d, 5, names, bold)  # Material
            sheet5.write(d, 6, "", bold)  # Net weight in a product

            bom_consu_prod_name = str(
                o.bom_consu.product_id.name for o in o.operation_ids if o.bom_consu
            )
            bom_consu_prod_name = "\n".join(filter(None, bom_consu_prod_name))

            sheet5.write(d, 7, bom_consu_prod_name or "", bold)  # Net weight Unit

            chemicals_compliant = (
                str(m.chemicals_compliant) for m in materials if m.chemicals_compliant
            )
            chemicals_compliant = "\n".join(filter(None, chemicals_compliant))

            sheet5.write(
                d, 8, chemicals_compliant or "", bold
            )  # Dangerous materials / Chemicals Compliant

            rohs_compliant = (
                str(m.rohs_compliant.name) for m in materials if m.rohs_compliant
            )
            rohs_compliant = "\n".join(filter(None, rohs_compliant))

            sheet5.write(d, 9, rohs_compliant or "", bold)  # RoHS

            reach_compliant = (
                str(m.reach_compliant.name) for m in materials if m.reach_compliant
            )
            reach_compliant = "\n".join(filter(None, reach_compliant))

            sheet5.write(d, 10, reach_compliant or "", bold)  # REACH

            scip_compliant = (
                str(m.scip_compliant.name) for m in materials if m.scip_compliant
            )
            scip_compliant = "\n".join(filter(None, scip_compliant))

            sheet5.write(d, 11, scip_compliant or "", bold)  # SCIP

            pop_compliant = (
                str(m.pop_compliant.name) for m in materials if m.pop_compliant
            )
            pop_compliant = "\n".join(filter(None, pop_compliant))

            sheet5.write(
                d, 12, pop_compliant or "", bold
            )  # POP (Persistant Organic Pollutants)

            halogen_compliant = (
                str(m.halogen_compliant.name) for m in materials if m.halogen_compliant
            )
            halogen_compliant = "\n".join(filter(None, halogen_compliant))

            sheet5.write(d, 13, halogen_compliant or "", bold)  # Halogens

            conflict_area_minerals_compliant = (
                str(m.conflict_area_minerals_compliant.name)
                for m in materials
                if m.conflict_area_minerals_compliant
            )
            conflict_area_minerals_compliant = "\n".join(
                filter(None, conflict_area_minerals_compliant)
            )

            sheet5.write(
                d, 14, conflict_area_minerals_compliant or "", bold
            )  # Conflict Area Minerals

            recycled_percentage = (
                str(m.recycled_percentage) for m in materials if m.recycled_percentage
            )
            recycled_percentage = "\n".join(filter(None, recycled_percentage))

            sheet5.write(d, 15, recycled_percentage or "", bold)  # Recycle material %

            product_material_waste_component_id = (
                str(m.product_material_waste_component_id.name)
                for m in materials
                if m.product_material_waste_component_id
            )
            product_material_waste_component_id = "\n".join(
                filter(None, product_material_waste_component_id)
            )

            sheet5.write(
                d, 16, product_material_waste_component_id or "", bold
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
                d, 17, product_material_waste_endpoint_id or "", bold
            )  # Waste endpoint

            parent_level = i - 1
            parent_level_2 = a - 1
            parent_level_3 = b - 1
            parent_level_4 = c - 1
            parent_level_5 = d - 1

            i += 1
            a += 1
            b += 1
            d += 1

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
                c = self.print_bom_children_4(
                    ch,
                    sheet4,
                    c,
                    j,
                    parent=o.product_tmpl_id,
                    parent_level=parent_level_4,
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
