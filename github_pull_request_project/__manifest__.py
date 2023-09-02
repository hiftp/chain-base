# © 2023 - Today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Github Pull Request Project',
    'version': "14.0.1.0.0",
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Project',
    'summary': 'Create a relation between tasks and github.pull_request models.',
    'depends': ['project', 'github_pull_request'],
    'data': [
        'data/project_tags.xml',
        'views/ir_actions_act_window.xml',
        'views/ir_ui_menu.xml',
        'views/github_pull_request.xml',
        'views/project_task.xml',
    ],
    'auto_install': False,
    'installable': True,
}
