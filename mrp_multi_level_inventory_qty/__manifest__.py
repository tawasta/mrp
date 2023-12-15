##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2023 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
    "name": "Inventory product circulation report",
    "summary": "Inventory product circulation report",
    "version": "14.0.1.0.6",
    "category": "Reporting",
    "website": "https://gitlab.com/tawasta/odoo/mrp",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "mrp",
        "mrp_multi_level",
        "product_abc_classification",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/product_report.xml",
        "wizard/open_product_report_wizard.xml",
        "views/report_view.xml",
        "security/ir.model.access.csv",
    ],
}
