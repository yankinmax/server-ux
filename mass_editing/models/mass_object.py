# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MassObject(models.Model):
    _name = "mass.object"
    _inherit = "mass.operation.mixin"
    _description = "Mass Editing Object"

    _wizard_model_name = 'mass.editing.wizard'

    field_ids = fields.Many2many('ir.model.fields', 'mass_field_rel',
                                 'mass_id', 'field_id', 'Fields')
    model_list = fields.Char('Model List')

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_ids = [(6, 0, [])]
        model_list = []
        if self.model_id:
            model_obj = self.env['ir.model']
            model_list = [self.model_id.id]
            active_model_obj = self.env[self.model_id.model]
            # if active_model_obj._inherits:
            #     keys = list(active_model_obj._inherits.keys())
            #     inherits_model_list = model_obj.search([('model', 'in', keys)])
            #     model_list.extend((inherits_model_list and
            #                        inherits_model_list.ids or []))
        self.model_list = model_list

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'name': _("%s (copy)" % self.name), 'field_ids': []})
        return super(MassObject, self).copy(default)
