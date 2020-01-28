# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return

    # Rename table for consistency reason
    cr.execute("""
        INSERT INTO mass_editing_line (mass_editing_id, field_id)
            SELECT
                mass_id as mass_editing_id,
                field_id
            FROM mass_field_rel;
    """)
