from collections import defaultdict

from odoo import _, models


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

        parent_with_code = "[{}] {}".format(parent.default_code, parent.name)

        sheet.write(i, 0, ch.product_id.default_code)
        sheet.write(i, 1, level)
        sheet.write(i, 2, ch.product_id.name)
        sheet.write(i, 3, parent_with_code)
        sheet.write(i, 4, ch.product_id.manufacturer.name or "")
        sheet.write(i, 5, ch.product_id.manufacturer_pref or "")
        sheet.write(i, 6, quantities[ident][1])
        sheet.write(i, 7, ch.product_uom_id.name)
        sheet.write(i, 8, ", ".join([route.name for route in ch.product_id.route_ids]))
        sheet.write(i, 9, ch.product_id.categ_id.name)

        material_info = ""

        for mater in ch.product_id.material:
            if not material_info:
                material_info += mater.material_info
            else:
                material_info += "{}{}".format("\n\n", mater.material_info)

        sheet.write(i, 10, material_info or "")
        sheet.write(i, 11, ch.product_id.origin_country_id.name or "")
        sheet.write(
            i, 12, ", ".join([seller.name.name for seller in ch.product_id.seller_ids])
        )
        sheet.write(
            i,
            13,
            ch.product_id.seller_ids and ch.product_id.seller_ids[0].product_code or "",
        )
        sheet.write(i, 14, ch.product_id.weight)
        sheet.write(i, 15, ch.product_id.weight * quantities[ident][1])
        sheet.write(i, 16, ch.product_id.gross_weight)
        sheet.write(i, 17, ch.product_id.gross_weight * quantities[ident][1])
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

    def generate_xlsx_report(self, workbook, data, objects):

        workbook.set_properties(
            {"comments": "Created with Python and XlsxWriter from Odoo 14.0"}
        )
        sheet = workbook.add_worksheet(_("BOM Structure"))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(80)

        # Some column sizes changed to match their title
        sheet.set_column(0, 0, 18)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 56)
        sheet.set_column(3, 3, 56)
        sheet.set_column(4, 4, 27)
        sheet.set_column(5, 5, 29)
        sheet.set_column(6, 6, 11)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 20)
        sheet.set_column(9, 9, 17)
        sheet.set_column(10, 10, 42)
        sheet.set_column(11, 11, 20)
        sheet.set_column(12, 12, 52)
        sheet.set_column(13, 13, 22)
        sheet.set_column(14, 14, 17)
        sheet.set_column(15, 15, 20)
        sheet.set_column(16, 16, 16)
        sheet.set_column(17, 17, 20)

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
        sheet.write_row(1, 4, sheet_title, title_style)
        sheet.write_row(1, 12, sheet_title_vendor, title_style_vendor)
        sheet.write_row(1, 14, sheet_title_weight, title_style_weight)
        sheet.freeze_panes(2, 0)
        i = 2

        for o in objects:
            ident = "{}".format(o.id)

            quantities = self.get_bom_quantities(o)

            sheet.write(i, 0, o.product_id.default_code or "", bold)
            sheet.write(i, 1, "1", bold)
            sheet.write(i, 2, o.product_tmpl_id.name, bold)
            sheet.write(i, 3, "N/A")  # No parent, since it's the top level
            sheet.write(i, 4, o.product_tmpl_id.manufacturer.name or "")
            sheet.write(i, 5, o.product_tmpl_id.manufacturer_pref or "")
            sheet.write(i, 6, o.product_qty, bold)
            sheet.write(i, 7, o.product_uom_id.name, bold)
            sheet.write(
                i, 8, ", ".join([route.name for route in o.product_tmpl_id.route_ids])
            )
            sheet.write(i, 9, o.product_tmpl_id.categ_id.name)

            material_info = ""

            for mater in o.product_id.material:
                if not material_info:
                    material_info += mater.material_info
                else:
                    material_info += "{}{}".format("\n\n", mater.material_info)

            sheet.write(i, 10, material_info or "", bold)
            sheet.write(i, 11, o.product_id.origin_country_id.name or "", bold)
            sheet.write(
                i,
                12,
                ", ".join(
                    [seller.name.name for seller in o.product_tmpl_id.seller_ids]
                ),
            )
            sheet.write(
                i,
                13,
                o.product_tmpl_id.seller_ids
                and o.product_tmpl_id.seller_ids[0].product_code
                or "",
            )
            sheet.write(i, 14, o.product_id.weight, bold)
            sheet.write(i, 15, o.product_id.weight * o.product_qty, bold)
            sheet.write(i, 16, o.product_id.gross_weight, bold)
            sheet.write(i, 17, o.product_id.gross_weight * o.product_qty, bold)

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
