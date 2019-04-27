# -*- coding: utf-8 -*-
{
	'name': "SLife Backend Theme",
	'summary': """Accordion Menu, Font Awesome Icon""",
	'description': """Accordion Menu, Font Awesome Icon""",
	'author': "SLife Organization, Amichia Fréjus Arnaud AKA",
	'category': 'Themes/Backend',
	'version': '1.0',
	'license': 'AGPL-3',
	'depends': ['web', 'mail'],
    'data': [
        'views/webclient_templates.xml',
        'views/slife_menu_view.xml',
        'views/res_config_settings_views.xml',
    ],
	'qweb': [
		'static/src/xml/slife_icon_template.xml'
	],
	'images': [
        'static/description/slife_screenshot.png',
    ],
	'application': True,
}
