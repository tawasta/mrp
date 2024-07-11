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
    "name": "Life Cycle Analysis report",
    "summary": "Export an excel for LCA report of a BoM",
    "version": "14.0.2.19.44",
    "category": "Manufacturing",
    "website": "https://gitlab.com/tawasta/odoo/mrp",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp_bom_structure_xlsx",
        "product_compliant",
        "product_harmonized_system",
        "product_manufacturer",
        "product_materials",
        "product_materials_compliant",
        "product_materials_relative_weight",
        "product_materials_upper_category",
        "res_partner_addresses_simple",
        "web_ir_actions_act_multi",
    ],
    "data": [
        "report/bom_structure_xlsx.xml",
        "security/ir.model.access.csv",
        "security/lca_manager_group.xml",
        "views/product_view.xml",
        "views/res_config_settings.xml",
        "wizard/bom_structure_xlsx_wizard.xml",
    ],
}
