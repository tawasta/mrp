##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Open Solutions Finland / Vizucom 2013-.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "BSM Importer",
    "summary": "Import data from local file system to database",
    "version": "14.0.1.0.0",
    "category": "General",
    "website": "https://gitlab.com/tawasta/odoo/mrp",
    "author": "Open Solutions Finland, Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/bsm_data.xml",
        "views/res_config_settings.xml",
    ],
}
