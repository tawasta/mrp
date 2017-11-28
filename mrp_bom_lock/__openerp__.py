# -*- coding: utf-8 -*-
{
    'name': 'BOM lock',
    'author': 'Vizucom Oy',
    'website': '',
    # Categories can be used to filter modules in module listing
    'category': 'mrp',
    'version': '0.1',
    # Any module necessary for this one to work correctly
    'depends': ['mrp'],
    'data': [
        # security/ir.model.access.csv,
        'views/product.xml',
        'data/group.xml',
    ],
    'description': """
* adds bom locked feature on product template.
""",
}
