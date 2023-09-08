# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': 'Transliterate Widget for baidu api and google api',
    'version': '16.0.1.0.1',
    'summary': 'Widget for translation',
    'description': 'Widget for translation',
    'category': 'Tools',
    'author': 'Cybrosys Techno Solutions,odooChain',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.odoochain.cn',
    'depends': ['base_setup'],
    'excludes': ['transliterate_widget'],
    'data': [
        'view/res_config_settings_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'transliterate_widget/static/src/js/jsapi.js',
            'transliterate_widget/static/src/js/transliterate_widget.js',
            '/transliterate_widget/static/src/xml/transliterate_widget.xml',

        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
