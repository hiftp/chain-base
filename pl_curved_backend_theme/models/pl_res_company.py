from odoo import models, fields


class PlResCompany(models.Model):
    _inherit = 'res.company'
    # ToDo: Add Default Values and strings

    pl_website_title = fields.Char(string="Website Backend Title", default='odoo')
    pl_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    pl_website_title_enable = fields.Boolean(string="Enable Website Backend Title")
    pl_favicon = fields.Binary(string="Favicon")
    pl_company_logo_enable = fields.Boolean(string="Enable Company Logo")
    pl_company_logo = fields.Binary(string="Main Company Logo")
    pl_small_company_logo = fields.Binary(string="Small Logo")
    pl_header = fields.Boolean(string="Show Header", default=False)
    pl_footer = fields.Boolean(string="Show Footer", default=False)
    pl_header_content = fields.Char(string="Header Content", default="Any Message you want to display on top.")
    pl_footer_content = fields.Char(string="Footer Content", default="Any Message you want to display on bottom.")
    pl_menu_bar = fields.Selection(string="Menu Bar Position",
                                   selection=[('Horizontal', 'Horizontal'), ('Vertical', 'Vertical')],
                                   default='Horizontal')
    pl_theme_style = fields.Selection(string="Theme Style", selection=[('curved_theme_style', 'Curved'),
                                                                       ('boxed_theme_style', 'Boxed')],
                                      default='curved_theme_style')
    pl_font_style = fields.Selection(string="Font Style", selection=[('pl_font_poppins', 'Poppins'),
                                                                     ('pl_font_lato', 'Lato'),
                                                                     ('pl_font_raleway', 'Raleway'),
                                                                     ('pl_font_arial', 'Arial'),
                                                                     ('pl_font_times_new', 'Times new'),
                                                                     ('pl_font_open_san', 'Open San'),
                                                                     ('pl_font_roboto', 'Roboto'),
                                                                     ('pl_font_ubuntu', 'Ubuntu'),
                                                                     ], default='pl_font_poppins')

    pl_font_size = fields.Selection(string="Font Size", selection=[('pl_font_size_small', 'Small'),
                                                                   ('pl_font_size_medium', 'Medium'),
                                                                   ('pl_font_size_large', 'Larger'),
                                                                   ('pl_font_size_extra_large', 'Extra Large')
                                                                   ], default='pl_font_size_medium')

    pl_button_style = fields.Selection(string="Button style", selection=[('pl_button_style_1', 'Style 1'),
                                                                         ('pl_button_style_2', 'Style 2'),
                                                                         ('pl_button_style_3', 'Style 3'),
                                                                         ('pl_button_style_4', 'Style 4'),
                                                                         ('pl_button_style_5', 'Style 5'),
                                                                         ], default='pl_button_style_1')

    pl_separator_style = fields.Selection(string="Separator style", selection=[('pl_separator_1', 'Separator 1'),
                                                                               ('pl_separator_2', 'Separator 2'),
                                                                               ('pl_separator_3', 'Separator 3'),
                                                                               ('pl_separator_4', 'Separator 4'),
                                                                               ('pl_separator_5', 'Separator 5')],
                                          default='pl_separator_1')

    pl_tab_style = fields.Selection(string="Tab style", selection=[('pl_tab_style1', 'Style 1'),
                                                                   ('pl_tab_style2', 'Style 2'),
                                                                   ('pl_tab_style3', 'Style 3'),
                                                                   ('pl_tab_style4', 'Style 4'),
                                                                   ('pl_tab_style5', 'Style 5'),
                                                                   ], default='pl_tab_style1')

    pl_checkbox_style = fields.Selection(string="Checkbox style",
                                         selection=[('pl_checkbox_1', 'Style 1'), ('pl_checkbox_2', 'Style 2'),
                                                    ('pl_checkbox_3', 'Style 3'),
                                                    ('pl_checkbox_4', 'Style 4'), ('pl_checkbox_5', 'Style 5')],
                                         default='pl_checkbox_1')

    pl_radio_button_style = fields.Selection(string="Radio Button Style",
                                             selection=[('pl_radio_button_1', 'Style 1'),
                                                        ('pl_radio_button_2', 'Style 2'),
                                                        ('pl_radio_button_3', 'Style 3'),
                                                        ('pl_radio_button_4', 'Style 4'),
                                                        ('pl_radio_button_5', 'Style 5')], default='pl_radio_button_1')

    pl_popup_animation_style = fields.Selection(string="Popup Animation style",
                                                selection=[('pl_popup_style1', 'Style 1'),
                                                           ('pl_popup_style2', 'Style 2'),
                                                           ('pl_popup_style3', 'Style 3'),
                                                           ('pl_popup_style4', 'Style 4'),
                                                           ('pl_popup_style5', 'Style 5'),
                                                           ('pl_popup_style6', 'Style 6'),
                                                           ('pl_popup_style7', 'Style 7'),
                                                           ('pl_popup_style8', 'Style 8'),
                                                           ('pl_popup_style9', 'Style 9'),
                                                           ('pl_popup_style10', 'Style 10'),
                                                           ], default='pl_popup_style1')

    pl_loaders = fields.Selection(string="Loading Bar", selection=[('pl_loader_1', 'Loader 1'),
                                                                   ('pl_loader_2', 'Loader 2'),
                                                                   ('pl_loader_3', 'Loader 3'),
                                                                   ('pl_loader_4', 'Loader 4'),
                                                                   ('pl_loader_5', 'Loader 5'),
                                                                   ('pl_loader_6', 'Loader 6'),
                                                                   ('pl_loader_7', 'Loader 7'),
                                                                   ('pl_loader_default', 'Default Loader'),
                                                                   ], default='pl_loader_default')

    pl_body_background = fields.Char(string="Body background", default=False)
    pl_body_background_opacity = fields.Float(string="Body Background Image Opacity", default=0.5)
    pl_app_drawer_background = fields.Char(string="App Drawer background", default=False)
    pl_app_drawer_background_opacity = fields.Float(string="App Drawer background Opacity", default=0.5)

    pl_chatter = fields.Selection(string="Chatter Position",
                                  selection=[('pl_chatter_bottom', 'Bottom'), ('pl_chatter_right', 'Right')],
                                  default='pl_chatter_bottom')

    pl_theme_color = fields.Many2one(comodel_name='pl.color.theme', string='Current color theme')

    pl_body_background_image_enable = fields.Boolean(string="Enable body background images", default=False)
