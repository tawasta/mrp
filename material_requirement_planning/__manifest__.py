# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
    'name': 'Material Requirement',
    'summary': 'Material Requirement',
    'version': '10.0.0.1.0',
    'category': 'Uncategorized',
    'website': 'https://tawasta.fi',
    'author': 'Oy Tawasta Technologies Ltd.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'mrp',
        'base',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'views/menuitem.xml',
        'views/material_requirement.xml',
        'views/material_requirement_line.xml',
    ],
    'demo': [
    ],
}

##############################################################################
#
#    AVAILABLE CATEGORIES - PLEASE REMOVE THIS AFTER SELECTING CATEGORY
#
#    Account Charts
#    Accounting & Finance
#    Association
#    Administration
#    CRM
#    Events
#    Extra Rights
#    Human Resources
#    Inventory
#    Invoicing & Payments
#    Lead Automation
#    Localization
#    Manufacturing
#    Mass Mailing
#    Other Extra Rights
#    Point of Sale
#    Project
#    Purchases
#    Sales
#    Specific Industry Applications
#    Survey
#    Technical Settings
#    Theme
#    Website
#
##############################################################################