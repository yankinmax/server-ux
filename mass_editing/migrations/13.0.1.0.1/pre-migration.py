# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        ALTER TABLE mass_object
        RENAME TO mass_editing;
    """)
    cr.execute("""
        ALTER TABLE mass_editing
        ADD COLUMN action_name varchar;
    """)
    cr.execute("""
        UPDATE mass_editing
        SET action_name = name;
    """)
