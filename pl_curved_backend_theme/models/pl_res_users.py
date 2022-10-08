from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class PlResUsers(models.Model):
    _inherit = 'res.users'

    pl_frequency_menu = fields.One2many(string="Frequency Menu", inverse_name='pl_user_id',
                                        comodel_name="pl.frequency.counter",
                                        help="To count frequency")
    pl_ir_ui_view = fields.Many2one(string="View", comodel_name="ir.ui.view")
    pl_favt_app_ids = fields.Many2many(string="Favorite Apps", comodel_name="ir.ui.menu",
                                       relation="pl_users_favt_ir_menu",
                                       column1="pl_user", column2="pl_favt_menu",
                                       help="To store all user favorite apps")
    pl_bookmark_ids = fields.One2many(string="Bookmarpl", comodel_name="pl.bookmark", inverse_name="pl_user_id",
                                      help="To acess bookmark")
    # ---------- Theme Config Fields 👇 ---------- #
    pl_dark_mode = fields.Boolean(string="Dark Mode", default=False)
    pl_auto_dark_mode = fields.Boolean(string="Auto-Dark Mode", default=False)
    pl_click_edit = fields.Boolean(string="Double-click Edit", default=False)
    pl_menu_bar = fields.Selection(string="Menu Bar Position",
                                   selection=[('Horizontal', 'Horizontal'), ('Vertical', 'Vertical')],
                                   default='Horizontal')
    pl_chatter = fields.Selection(string="Chatter Position",
                                  selection=[('pl_chatter_bottom', 'Bottom'), ('pl_chatter_right', 'Right')],
                                  default='pl_chatter_bottom')
    pl_favorite_bar = fields.Boolean(string="Show Favorite Apps", default=True)
    pl_favtbar_autohide = fields.Boolean(string="Auto-hide Favorite Bar", default=False)
    pl_menubar_autohide = fields.Boolean(string="Auto-hide Menu Bar", default=False)
    pl_favtbar_position = fields.Selection(string="Favoritebar Position",
                                           selection=[('Bottom', 'Bottom'), ('Left', 'Left')], default='Left')
    pl_list_density = fields.Selection(string="List View Style",
                                       selection=[('Default', 'Default'), ('Comfortable', 'Comfortable'),
                                                  ('Attachment', 'Attachment')],
                                       default='Default')
    pl_show_app_name = fields.Boolean(string="Display App Names", default=True)
    pl_user_menu_placement = fields.Selection(string="User Menu Placement",
                                              selection=[('Bottom', 'Bottom'), ('Top', 'Top')], default='Bottom')
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

    pl_button_style = fields.Selection(string="Button style", selection=[('pl_button_style_1', 'Style 1'),
                                                                         ('pl_button_style_2', 'Style 2'),
                                                                         ('pl_button_style_3', 'Style 3'),
                                                                         ('pl_button_style_4', 'Style 4'),
                                                                         ('pl_button_style_5', 'Style 5'),
                                                                         ], default='pl_button_style_1')

    pl_loaders = fields.Selection(string="Loading Bar", selection=[('pl_loader_1', 'Loader 1'),
                                                                   ('pl_loader_2', 'Loader 2'),
                                                                   ('pl_loader_3', 'Loader 3'),
                                                                   ('pl_loader_4', 'Loader 4'),
                                                                   ('pl_loader_5', 'Loader 5'),
                                                                   ('pl_loader_6', 'Loader 6'),
                                                                   ('pl_loader_7', 'Loader 7'),
                                                                   ('pl_loader_default', 'Default Loader'),
                                                                   ], default='pl_loader_default')

    pl_separator_style = fields.Selection(string="Separator style", selection=[('pl_separator_1', 'Separator 1'),
                                                                               ('pl_separator_2', 'Separator 2'),
                                                                               ('pl_separator_3', 'Separator 3'),
                                                                               ('pl_separator_4', 'Separator 4'),
                                                                               ('pl_separator_5', 'Separator 5')],
                                          default='pl_separator_1')

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

    pl_tab_style = fields.Selection(string="Tab style", selection=[('pl_tab_style1', 'Style 1'),
                                                                   ('pl_tab_style2', 'Style 2'),
                                                                   ('pl_tab_style3', 'Style 3'),
                                                                   ('pl_tab_style4', 'Style 4'),
                                                                   ('pl_tab_style5', 'Style 5'),
                                                                   ], default='pl_tab_style1')

    pl_body_background = fields.Char(string="Body background", default=False)
    pl_body_background_opacity = fields.Float(string="Body Background Image Opacity", default=0.5)
    pl_app_drawer_background = fields.Char(string="App Drawer background", default=False)
    pl_app_drawer_background_opacity = fields.Float(string="App Drawer background Opacity", default=0.5)

    pl_body_background_color = fields.Selection(selection=[('body_back_color_1', 'Body Background Color 1'),
                                                           ('body_back_color_2', 'Body Background Color 2'),
                                                           ('body_back_color_3', 'Body Background Color 3'),
                                                           ('body_back_color_4', 'Body Background Color 4'),
                                                           ('body_back_color_5', 'Body Background Color 5'),
                                                           ('body_back_color_6', 'Body Background Color 6'),
                                                           ('body_back_color_7', 'Body Background Color 7'),
                                                           ('body_back_color_8', 'Body Background Color 8')],
                                                default='body_back_color_1',
                                                string="Body Background Color")

    pl_sunrise_hour = fields.Integer(string="Sunrise Time", default="8", help="Sunrise time HH:MM format")
    pl_sunrise_min = fields.Integer(string="Sunrise Min", default="0")
    pl_sunset_hour = fields.Integer(string="Sunset Time", default="18", help="Sunset time HH:MM format")
    pl_sunset_min = fields.Integer(string="Sunset Min", default="0")

    pl_theme_color = fields.Many2one(comodel_name='pl.color.theme', string='Current color theme')
    pl_body_background_image_enable = fields.Boolean(string="Enable body background images", default=False)
    pl_form_page_width = fields.Float('Form Page Width')
    pl_split_view = fields.Selection(
        selection=[('no_split', 'No split'), ('vertical', 'Vertical'), ('horizontal', 'Horizontal')],
        string='Split View', default='no_split')
    pl_split_vertical_list_width = fields.Float('Vertical list view width')
    pl_split_horizontal_list_height = fields.Float('horizontal list view height')

    def __init__(self, pool, cr):
        init_res = super().__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = self.SELF_WRITEABLE_FIELDS + ['pl_sunrise_hour', 'pl_sunrise_min',
                                                                         'pl_sunset_hour', 'pl_sunset_min']
        return init_res

    @api.constrains('pl_sunrise_hour', 'pl_sunrise_min', 'pl_sunset_hour', 'pl_sunset_min')
    def pl_check_suntime(self):
        if self.pl_sunrise_hour > self.pl_sunset_hour or (
                self.pl_sunrise_hour == self.pl_sunset_hour and self.pl_sunrise_min > self.pl_sunset_min):
            raise ValidationError(_("sunrise happens before sunset."))
        if self.pl_sunrise_hour < 0 or self.pl_sunset_hour < 0 or self.pl_sunrise_min < 0 or self.pl_sunset_min < 0:
            raise ValidationError(_("Time can't be negative."))
        if self.pl_sunrise_hour > 23 or self.pl_sunset_hour > 23 or self.pl_sunrise_min > 59 or self.pl_sunset_min > 59:
            raise ValidationError(_("Please enter values in correct time."))
