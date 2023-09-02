# © 2023 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Github Pull Request',
    'version': "14.0.1.0.0",
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Connector',
    'summary': 'Define what is a github Pull Request as an odoo object.',
    'depends': [
        'github_event',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/github_event.xml',
        'views/github_pull_request.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
