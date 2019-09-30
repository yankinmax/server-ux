# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

import odoo.tools as tools
from odoo import api, models


class MassEditingWizard(models.TransientModel):
    _name = 'mass.editing.wizard'
    _inherit = 'mass.operation.wizard.mixin'
    _description = "Wizard for mass edition"

    @api.model
    def _prepare_fields(self, field, field_info):
        result = {}

        # Add "selection field (set / add / remove / remove_m2m)
        if field.ttype == "many2many":
            selection = [
                ('set', 'Set'),
                ('remove_m2m', 'Remove'),
                ('add', 'Add'),
            ]
        else:
            selection = [
                ('set', 'Set'),
                ('remove', 'Remove'),
            ]
        result["selection__" + field.name] = {
            'type': 'selection',
            'string': field_info['string'],
            'selection': selection,
        }

        # Add field info
        result[field.name] = field_info

        # Patch fields with required extra data
        for item in result.values():
            item.setdefault("views", {})
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        mass_editing = self._get_mass_operation()
        if not mass_editing:
            return result

        all_fields = {}
        xml_form = etree.Element('form', {
            'string': tools.ustr(mass_editing.action_name)
        })
        xml_group = etree.SubElement(xml_form, 'group', {
            'colspan': '6',
            'col': '6',
        })
        TargetModel = self.env[mass_editing.model_id.model]
        fields_info = TargetModel.fields_get()

        for field in mass_editing.field_ids:
            field_info = fields_info[field.name]
            all_fields.update(self._prepare_fields(field, field_info))

            if field.ttype == "many2many":
                xml_group = etree.SubElement(xml_group, 'group', {
                    'colspan': '6',
                    'col': '6',
                })
                etree.SubElement(xml_group, 'separator', {
                    'string': field_info['string'],
                    'colspan': '6',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': "selection__" + field.name,
                    'colspan': '6',
                    'nolabel': '1'
                })
                etree.SubElement(xml_group, 'field', {
                    'name': field.name,
                    'colspan': '6',
                    'nolabel': '1',
                    'attrs': ("{'invisible': [('selection__" +
                              field.name + "', '=', 'remove_m2m')]}"),
                })
            elif field.ttype == "one2many":
                etree.SubElement(xml_group, 'field', {
                    'name': "selection__" + field.name,
                    'colspan': '4',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': field.name,
                    'colspan': '6',
                    'nolabel': '1',
                    'attrs': ("{'invisible':[('selection__" +
                              field.name + "', '=', 'remove_o2m')]}"),
                })
            elif field.ttype == "many2one":
                etree.SubElement(xml_group, 'field', {
                    'name': "selection__" + field.name,
                    'colspan': '2',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': field.name,
                    'nolabel': '1',
                    'colspan': '4',
                    'attrs': ("{'invisible':[('selection__" +
                              field.name + "', '=', 'remove')]}"),
                })
            elif field.ttype == "char":
                etree.SubElement(xml_group, 'field', {
                    'name': "selection__" + field.name,
                    'colspan': '2',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': field.name,
                    'nolabel': '1',
                    'attrs': ("{'invisible':[('selection__" +
                              field.name + "','=','remove')]}"),
                    'colspan': '4',
                })
            elif field.ttype == 'selection':
                etree.SubElement(xml_group, 'field', {
                    'name': "selection__" + field.name,
                    'colspan': '2',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': field.name,
                    'nolabel': '1',
                    'colspan': '4',
                    'attrs': ("{'invisible':[('selection__" +
                              field.name + "', '=', 'remove')]}"),
                })
            elif field.ttype == 'text':
                xml_group = etree.SubElement(xml_group, 'group', {
                    'colspan': '6',
                    'col': '6',
                })
                etree.SubElement(xml_group, 'separator', {
                    'string': all_fields[field.name]['string'],
                    'colspan': '6',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': "selection__" + field.name,
                    'colspan': '6',
                    'nolabel': '1',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': field.name,
                    'colspan': '6',
                    'nolabel': '1',
                    'attrs': ("{'invisible':[('selection__" +
                              field.name + "','=','remove')]}"),
                })
            else:
                etree.SubElement(xml_group, 'field', {
                    'name': "selection__" + field.name,
                    'colspan': '2',
                })
                etree.SubElement(xml_group, 'field', {
                    'name': field.name,
                    'nolabel': '1',
                    'attrs': ("{'invisible':[('selection__" +
                              field.name + "','=','remove')]}"),
                    'colspan': '4',
                })

        etree.SubElement(xml_form, 'separator', {
            'string': '',
            'colspan': '6',
            'col': '6',
        })
        xml_group3 = etree.SubElement(xml_form, 'footer', {})
        etree.SubElement(xml_group3, 'button', {
            'string': 'Apply',
            'class': 'btn-primary',
            'type': 'object',
            'name': 'action_apply',
        })
        etree.SubElement(xml_group3, 'button', {
            'string': 'Close',
            'class': 'btn-default',
            'special': 'cancel',
        })
        root = xml_form.getroottree()
        result['arch'] = etree.tostring(root)
        result['fields'] = all_fields
        return result

    @api.model
    def create(self, vals):
        if (self.env.context.get('active_model') and
                self.env.context.get('active_ids')):
            model_obj = self.env[self.env.context.get('active_model')]
            model_field_obj = self.env['ir.model.fields']
            translation_obj = self.env['ir.translation']

            values = {}
            for key, val in vals.items():
                if key.startswith('selection_'):
                    split_key = key.split('__', 1)[1]
                    if val == 'set':
                        values.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        values.update({split_key: False})

                        # If field to remove is translatable,
                        # its translations have to be removed
                        model_field = model_field_obj.search([
                            ('model', '=',
                             self.env.context.get('active_model')),
                            ('name', '=', split_key)])
                        if model_field and model_field.translate:
                            translation_ids = translation_obj.search([
                                ('res_id', 'in', self.env.context.get(
                                    'active_ids')),
                                ('type', '=', 'model'),
                                ('name', '=', u"{0},{1}".format(
                                    self.env.context.get('active_model'),
                                    split_key))])
                            translation_ids.unlink()

                    elif val == 'remove_m2m':
                        m2m_list = []
                        if vals.get(split_key):
                            for m2m_id in vals.get(split_key)[0][2]:
                                m2m_list.append((3, m2m_id))
                        if m2m_list:
                            values.update({split_key: m2m_list})
                        else:
                            values.update({split_key: [(5, 0, [])]})
                    elif val == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        values.update({split_key: m2m_list})
            if values:
                model_obj.browse(
                    self.env.context.get('active_ids')).write(values)
        return super().create({})

    def action_apply(self):
        return {'type': 'ir.actions.act_window_close'}

    def read(self, fields, load='_classic_read'):
        """ Without this call, dynamic fields build by fields_view_get()
            generate a log warning, i.e.:
            odoo.models:mass.editing.wizard.read() with unknown field 'myfield'
            odoo.models:mass.editing.wizard.read()
                with unknown field 'selection__myfield'
        """
        real_fields = fields
        if fields:
            # We remove fields which are not in _fields
            real_fields = [x for x in fields if x in self._fields]
        result = super().read(real_fields, load=load)
        # adding fields to result
        [result[0].update({x: False}) for x in fields if x not in real_fields]
        return result
