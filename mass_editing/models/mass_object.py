# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MassObject(models.Model):
    _name = "mass.object"
    _inherit = "mass.operation.mixin"
    _description = "Mass Editing Object"

    _wizard_model_name = 'mass.editing.wizard'

    field_ids = fields.Many2many(
        comodel_name='ir.model.fields', string='Fields', copy=False,
        relation='mass_field_rel', column1='mass_id', column2='field_id',
        domain="["
        "('name', '!=', '__last_update'),"
        "('readonly', '=', False),"
        "('ttype', 'not in', ['reference', 'function']),"
        "('model_id', '=', model_id)"
        "]",
    )
