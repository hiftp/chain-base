# © 2020 Jérôme Guerriat, Tobias Zehntner
# © 2020 Niboo SRL (<https://www.niboo.com/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Phonecode",
    "category": "CRM",
    "summary": "Split phone and mobilephone in two fields: phonecode and phone",
    "website": "https://www.niboo.com",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "description": """Split phone and mobilephone in two fields: phonecode and phone""",
    "author": "Niboo",
    "external_dependencies": {"python": ["phonenumbers"]},
    "data": ["views/res_partner.xml"],
    "installable": True,
    "application": False,
}
