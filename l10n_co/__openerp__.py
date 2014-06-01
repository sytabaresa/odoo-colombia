# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Colombian - Accounting',
    'version': '0.1',
    'category': 'Localization/Account Charts',
    'description': """
This is the base module to manage the accounting chart for Colombian in OpenERP.
==============================================================================
....
""",
    'author': """Juan Pablo Arias - David Arnold B.A. HSG - Hector Ivan Valencia
Odoo Colombia https://plus.google.com/communities/113251920989277948689
""",
    'depends': [
        'account',
        'base_vat',
        'account_chart',
    ],
    'data': [
    	'wizard/account_wizard.xml',
    ],
    'demo': [],
    'installable': True,
    'images': [],
}