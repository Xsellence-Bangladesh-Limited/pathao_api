{
    'name': 'Pathao API',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': "Module for PATHAO API integration",
    'sequence': 11,
    'author': 'Xsellence Bangladesh Limited',
    'maintainer': 'Xsellence Bangladesh Limited',
    'website': 'https://www.xsellencebdltd.com/',
    'depends': ['product', 'sale', 'website_sale'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/views_menu.xml',
        'data/cron_schedulers.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
