##############################################################################
#
#    Author: Futural Oy
#    Copyright 2026- Futural Oy (https://futural.fi)
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

{
    "name": "Quality Control OCA: Inspection E-mail - Default Recipient "
    "from Sale Order",
    "summary": "If QC Inspection was originated from a picking and the picking from "
    "a Sale order, suggest the related SO's partner as an inspection "
    "e-mail recipient",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Quality",
    "website": "https://github.com/tawasta/mrp",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    # Deprecated: its behaviour is now covered by
    # quality_control_oca_inspection_partner (partner_id) +
    # quality_control_oca_inspection_partner_picking_partner_from_sale.
    "installable": False,
    "depends": [
        "quality_control_oca_inspection_email",
        "quality_control_stock_oca",
        "sale_stock",
    ],
}
