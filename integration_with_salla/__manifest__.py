# -*- coding: utf-8 -*-
{
    'name': "Salla Integration",

    'summary': """
       This module allow you to connect odoo with salla """,

    'description': """
       By using this package you will get all your orders , products , customers  from salla
And get real time update from salla such as updating product price , order total ,etc..
Please Note:
You will have to to subscribe to salla app to get a full dashboard between salla and your odoo system
    """,

    'author': "EJAD Digital Solutions ",
    'website': "https://ejad.sa/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    
    'version': '15.0',
    'category': 'Sales',
    'sequence': 14,
    'price': 400,
    'currency': "USD",

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account'],

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
