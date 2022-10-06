# Copyright 2020 Agrista GmbH (https://agrista.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Interest Rates",
    "version": "15.0.1.0.1",
    "author": "Yangtze Loong",
    "website": "https://github.com/odoochain/chain-interest-rates",
    "license": "AGPL-3",
    "category": "Financial Management/Configuration",
    "summary": "Update the lending rate / interest rate",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "security/interest.xml",
        "views/interest_views.xml",
    ],
    "installable": True,
}
