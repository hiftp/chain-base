# -*- coding: utf-8 -*-
{
    'name': 'Edit Blog Post in Backend',
    'summary': 'Add an editor into the post form used to edit content directly.',
    'description': 'The easiest way to edit blog content is a direct HTML editor in post form. This module adds an editor to the blog form.',
    'author': 'FL1 sro',
    'website': 'https://fl1.cz',
    'category': 'Website/Website',
    'version': '16.0.1.0.0',
    'depends': [
        'website',
        'website_blog',
    ],
    'data': [
        'views/website_blog.xml',
    ],
    'images': [
        'static/description/images/screenshot-14-0.png',
        'static/description/images/screenshot-14-1.png',
        'static/description/banner.png'
    ],
    'license': 'LGPL-3',
    'auto_install': False,
    'installable': True,
}
