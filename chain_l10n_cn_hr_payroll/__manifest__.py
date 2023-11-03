# -*- coding: utf-8 -*-
# © 2016-2018 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Chinese - Payroll',
    'category': 'Human Resources/Payroll',
    'version': '16.0.0.0.1',
    'website': 'https://www.odoochain.cn',
    'author': "Odoo Community Association (OCA)",
    'depends': [
        'hr_payroll',
        'hr_contract_reports',
        'hr_work_entry_holidays'],
    'demo': [
    ],
    'data':
    [
        # 'security/ir.model.access.csv',
        # 'security/l10n_cn_hr_payroll_security.xml',
        'data/report_paperformat.xml',
        'data/base_cn.xml',
        'data/integration_rules_cn.xml',
        'views/l10n_cn_hr_payroll_view.xml',
        'views/report_payslip.xml',
        'views/report_payslip_template.xml',
        'views/reports.xml',
        # 'data/salary_rule_category.xml',
        # 'data/salary_rule_basic.xml',
        # 'data/city/salary_rule_sz1.xml',
        # 'data/city/salary_rule_sz2.xml',
        # 'data/city/salary_rule_sz3.xml',
        # 'data/city/salary_rule_sz4.xml',
        # 'data/salary_rule_sh1.xml',
        # 'data/salary_rule_sh2.xml',
        # 'data/salary_rule_sh3.xml',
        # 'data/salary_rule_sh4.xml',
        # 'data/salary_rule_nj1.xml',
        'views/hr_contract_views.xml',
        'views/cn_payroll_config_views.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
