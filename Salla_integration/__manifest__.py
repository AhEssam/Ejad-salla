# -*- coding: utf-8 -*-
{
    'name': "Salla Integration",

    'summary': """
       This module allow you to connect odoo with salla """,

    'description': """
        this module allow you to get all salla orders and products and invoices 
        to install this module you need to install our salla connector from salla store 
    """,

    'author': "EJAD Digital Solutions | Ahmed Esam",
    'website': "https://ejad.sa/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/sale.xml'
    ],
    # "external_dependencies": {
    #     "python": [
    #         "Salla",
    #     ]
    # },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/log.png'],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
