##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2022- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:
from datetime import date

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import _, api, fields, models, exceptions

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class MultiLevelMrp(models.TransientModel):
    _inherit = "mrp.multi.level"

    @api.model
    def _prepare_mrp_move_data_from_purchase_order(self, poline, product_mrp_area):
        on_hand_qty = product_mrp_area.product_id.with_context(
            location=product_mrp_area.mrp_area_id.location_id.id
        )._product_available()[product_mrp_area.product_id.id]["qty_available"]
        forecasted_qty = on_hand_qty
        mrp_date = date.today()
        if fields.Date.from_string(poline.date_planned) > date.today():
            mrp_date = fields.Date.from_string(poline.date_planned)
        prev_mrp_qty = 0
        for move_id in product_mrp_area.mrp_move_ids:
            prev_mrp_qty += move_id.mrp_qty
        forecasted_qty += poline.product_qty + prev_mrp_qty
        return {
            "product_id": poline.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": None,
            "purchase_order_id": poline.order_id.id,
            "purchase_line_id": poline.id,
            "stock_move_id": None,
            "mrp_qty": poline.product_qty,
            "current_qty": poline.product_qty,
            "forecasted_qty": forecasted_qty,
            "mrp_date": mrp_date,
            "current_date": poline.date_planned,
            "mrp_type": "s",
            "mrp_origin": "po",
            "mrp_order_number": poline.order_id.name,
            "parent_product_id": None,
            "name": poline.order_id.name,
            "state": poline.order_id.state,
        }

    @api.model
    def _prepare_mrp_move_data_from_stock_move(
        self, product_mrp_area, move, direction="in"
    ):
        on_hand_qty = product_mrp_area.product_id.with_context(
            location=product_mrp_area.mrp_area_id.location_id.id
        )._product_available()[product_mrp_area.product_id.id]["qty_available"]
        forecasted_qty = on_hand_qty
        prev_mrp_qty = 0
        for move_id in product_mrp_area.mrp_move_ids:
            prev_mrp_qty += move_id.mrp_qty
        area = product_mrp_area.mrp_area_id
        if direction == "out":
            mrp_type = "d"
            product_qty = -move.product_qty
        else:
            mrp_type = "s"
            product_qty = move.product_qty
        po = po_line = None
        mo = origin = order_number = parent_product_id = None
        if move.purchase_line_id:
            order_number = move.purchase_line_id.order_id.name
            origin = "po"
            po = move.purchase_line_id.order_id.id
            po_line = move.purchase_line_id.id
        elif move.production_id:
            order_number = move.production_id.name
            origin = "mo"
            mo = move.production_id.id
        elif move.move_dest_ids:
            for move_dest_id in move.move_dest_ids.filtered("production_id"):
                order_number = move_dest_id.production_id.name
                origin = "mo"
                mo = move_dest_id.production_id.id
                parent_product_id = (
                    move_dest_id.production_id.product_id or move_dest_id.product_id
                ).id
        else:
            order_number = (move.picking_id or move).name
            origin = "mv"
        forecasted_qty += prev_mrp_qty + product_qty
        # The date to display is based on the timezone of the warehouse.
        today_tz = area._datetime_to_date_tz()
        move_date_tz = area._datetime_to_date_tz(move.date_expected)
        if move_date_tz > today_tz:
            mrp_date = move_date_tz
        else:
            mrp_date = today_tz
        return {
            "product_id": move.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": mo,
            "purchase_order_id": po,
            "purchase_line_id": po_line,
            "stock_move_id": move.id,
            "mrp_qty": product_qty,
            "current_qty": product_qty,
            "mrp_date": mrp_date,
            "current_date": move.date_expected,
            "mrp_type": mrp_type,
            "mrp_origin": origin,
            "mrp_order_number": order_number,
            "parent_product_id": parent_product_id,
            "name": order_number,
            "state": move.state,
            "forecasted_qty": forecasted_qty,
        }

    @api.model
    def _prepare_mrp_move_data_bom_explosion(
        self, product, bomline, qty, mrp_date_demand_2, bom, name
    ):
        product_mrp_area = self._get_product_mrp_area_from_product_and_area(
            bomline.product_id, product.mrp_area_id
        )
        if not product_mrp_area:
            raise exceptions.Warning(_("No MRP product found"))

        on_hand_qty = product_mrp_area.product_id.with_context(
            location=product_mrp_area.mrp_area_id.location_id.id
        )._product_available()[product_mrp_area.product_id.id]["qty_available"]
        forecasted_qty = on_hand_qty

        prev_mrp_qty = 0
        for move_id in product_mrp_area.mrp_move_ids:
            prev_mrp_qty += move_id.mrp_qty

        mrp_qty = -(qty * bomline.product_qty)
        forecasted_qty += prev_mrp_qty + mrp_qty

        return {
            "mrp_area_id": product.mrp_area_id.id,
            "product_id": bomline.product_id.id,
            "product_mrp_area_id": product_mrp_area.id,
            "production_id": None,
            "purchase_order_id": None,
            "purchase_line_id": None,
            "stock_move_id": None,
            "mrp_qty": mrp_qty,
            "forecasted_qty": forecasted_qty,
            "current_qty": None,
            "mrp_date": mrp_date_demand_2,
            "current_date": None,
            "mrp_type": "d",
            "mrp_origin": "mrp",
            "mrp_order_number": None,
            "parent_product_id": bom.product_id.id,
            "name": (
                "Demand Bom Explosion: %s"
                % (name or product.product_id.default_code or product.product_id.name)
            ).replace(
                "Demand Bom Explosion: Demand Bom Explosion: ", "Demand Bom Explosion: "
            ),
        }
