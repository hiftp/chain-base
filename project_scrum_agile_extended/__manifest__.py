# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    # Module information
    "name": "Project Scrum Management Extended",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "category": "Project Scrum Management",
    "summary": """
        This application is used to manage total planned hours, progress,
        weightage of sprint, sprint release, product backlog.
        This application used to manage logs in of sprint release from sprint.
        This application used to calculate meeting duration.
        """,
    "sequence": 1,
    # Author
    "author": "Serpent Consulting Services Pvt. Ltd.,David DRAPEAU",
    "website": "https://www.serpentcs.com/",
    # Dependancies
    "depends": ["project_scrum_agile"],
    # Views
    "data": [
        "security/ir_rules.xml",
        "security/ir.model.access.csv",
        "views/project_scrum_release_view.xml",
        "views/project_scrum_view.xml",
        "views/account_analytic_line_view.xml",
        "views/project_view.xml",
        "views/project_task_view.xml",
    ],
    # Technical
    "installable": True,
    "application": True,
}
