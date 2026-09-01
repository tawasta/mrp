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
    "name": "Quality Control OCA: Inspection & Sale Order Link",
    "summary": "Link quality inspections to SOs and show them on the SO form",
    "version": "19.0.1.0.0",
    "category": "Manufacturing/Quality",
    "website": "https://github.com/tawasta/mrp",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "quality_control_oca",
        "sale",
    ],
    "data": [
        "views/qc_inspection_views.xml",
        "views/sale_order_views.xml",
    ],
}
