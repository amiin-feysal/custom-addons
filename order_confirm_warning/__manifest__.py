{
    'name': 'Order Confirmation Warning',
    'version': '19.0.1.0.0',
    'summary': 'Warning popup before confirming Purchase and Sales Orders',
    'category': 'Tools',
    'depends': ['sale', 'purchase'],
    'data': [
        'views/order_confirm_warning_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
