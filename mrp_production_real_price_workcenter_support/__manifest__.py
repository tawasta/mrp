##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2018 Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
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
    "name": "Add workcenter cost to FIFO real price manufactured products",
    "summary": "Add workcenter cost to FIFO real price manufactured products",
    "version": "12.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/Tawasta/mrp",
    "author": "Oy Tawasta Technologies Ltd.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": [],},
    "depends": ["mrp_production_real_price", "mrp_workcenter_cost",],
    "data": [],
    "demo": [],
}
