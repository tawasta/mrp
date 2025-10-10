##############################################################################
#
#    Author: Futural Oy
#    Copyright 2025 Futural Oy (https://futural.fi)
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
    "name": "MRP Multi Level – Ignore certain orders in MRP moves",
    "summary": "Ignore certain orders in MRP moves",
    "version": "14.0.1.1.0",
    "category": "MRP",
    "website": "https://github.com/tawasta/mrp",
    "author": "Futural",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp_multi_level",
    ],
    "data": ["views/mrp_area_view.xml"],
}
