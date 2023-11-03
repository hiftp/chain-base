# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    # Module information
    "name": "Agreement Extended",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "category": "Contract",
    "summary": """
        Add the option to select projects,states and
        description in the agreement.
        """,
    "sequence": 1,
    # Author
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "https://www.serpentcs.com/",
    # Dependancies
    "depends": ["agreement", "project_team_leave_management"],
    # Views
    "data": ["views/agreement_view.xml", "views/res_partner_view.xml"],
    # Technical
    "installable": True,
    "application": True,
}
