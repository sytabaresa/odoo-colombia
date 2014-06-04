# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
import re
import codecs
from openerp.osv import fields, osv
from openerp.tools.translate import _


class CountryStateCity(osv.osv):
    '''
    Model added to manipulate separately the cities on Partner address.
    '''
    _description='Model to manipulate Cities'
    _name ='res.country.state.city'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State', required=True),
        'name': fields.char('City Name', size=64, required=True),
        'code': fields.char('City Code', size=5, help='Código DANE -5 dígitos-', required=True),
    }

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if not context:
            context = {}
        ids = self.search(cr, user, [('code', '=', name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    _order = 'code'

CountryStateCity()

#~ Creación de campos
#~ Creating Fields

class res_partner_co(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'tdoc': fields.selection((('11','Registro civil'), ('12','Tarjeta de identidad'),
                                  ('13','Cédula de ciudadanía'), ('21','Tarjeta de extranjería'),
                                  ('22','Cédula de extranjería'), ('31','NIT'),
                                  ('41','Pasaporte'), ('42','Tipo de documento extranjero'),
                                  ('43','Para uso definido por la DIAN'), ('NU','Número único de identificación'),
                                  ('AS','Adulto sin identificaciómn'), ('MS','Menor sin identificación')),
                                  'Tipo de Documento'),
        'dv': fields.char('dv', size=1, help='Digito de verificación'),
        'lastname': fields.char('lastname', size=25),
        'surname': fields.char('surname', size=25),
        'firtsname': fields.char('firtsname', size=25),
        'middlename': fields.char('middlename', size=25),
        'city_id':fields.many2one('res.country.state.city', 'Ciudad', required=False, domain="[('state_id','=',state_id)]"),
    }

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        ids = []
        if name:
            ids = self.search(cr, uid, [('ref', 'ilike', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    _defaults = {
        'tdoc' : '13',
        'country_id': lambda self, cr, uid, context: self.pool.get('res.country').browse(cr, uid, self.pool.get('res.country').search(cr, uid, [('code','=','CO')]))[0].id,
        'state_id': lambda self, cr, uid, context: self.pool.get('res.country.state').browse(cr, uid, self.pool.get('res.country.state').search(cr, uid, [('code','=','63')]))[0].id,
        }

# Función para concatenar los apellidos y nombres y almacenarlos en el campo name
# Function to concatenate the names and surnames and store them in the name field

    def onchange_name(self, cr, uid, ids, lastname, surname, firtsname, middlename, context=None):
        res = {'value':{}}
        res['value']['name'] =  "%s %s %s %s" % (lastname , surname or '' , firtsname , middlename or '')
        return res

    def onchange_tdoc(self, cr, uid, ids, is_company, tdoc, context=None):
        values = {}
        is_company = is_company
        tdoc = tdoc
        if is_company:
            values.update({
            'tdoc' : "31",
            })
        return {'value' : values}

    def _check_name(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            is_company = record.is_company
            name = record.name
            lastname = record.lastname
            surname = record.surname
            firtsname = record.firtsname
            middlename = record.middlename
            newname = "%s %s %s %s" % (lastname , surname or '' , firtsname , middlename or '')
            if not (lastname or surname or firtsname or middlename):
                return True
            elif not is_company and name != newname:
                return False
            elif is_company and (lastname or surname or firtsname or middlename):
                return self.write(cr, uid, ids, {'lastname': '', 'surname': '', 'firtsname': '', 'middlename':  ''}, context=context)
        return True

# Función para validar que la identificación sea sólo numerica
# Function to validate the numerical identification is only

    def _check_ident_num(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            ref = record.ref
            if ref != False:
                if re.match("^[0-9]+$", ref) == None:
                    return False
        return True

# Función para validar que la identificación tenga más de 6 y dígitos y menos de 11
# Function to validate that the identification is more than 6 and less than 11 digits

    def _check_ident(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            # Si utiliza la direccion de la Empresa el ref viene vacio.
            # Evitar esto con break al for.
            if record.use_parent_address:
                break
            else:
                ref = record.ref
                if not ref:
                    return True
                elif len(str(ref)) <6:
                    return False
                elif len(str(ref)) >11:
                    return False
        return True

# Función para evitar número de documento duplicado

    def _check_unique_ident(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            ref = record.ref
            ref_ids = self.search(cr, uid, [('ref', '=', record.ref), ('id', '<>', record.id)])
            if not ref:
                return True
            elif ref_ids:
                return False
        return True

# Función para validar el dígito de verificación
# Function to validate the check digit

    def _check_dv(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            ref = record.ref
            dv = record.dv
            tdoc = record.tdoc
            dvcal = 'dvcal',
            if tdoc == '31':
                if ref != False:
                    if ref.isdigit():
                        b= '0'*(15-len(ref)) + ref
                        vl=list(b)
                        op=(int(vl[0])*71+int(vl[1])*67+int(vl[2])*59+int(vl[3])*53+int(vl[4])*47+int(vl[5])*43+int(vl[6])*41+int(vl[7])*37+int(vl[8])*29+int(vl[9])*23+int(vl[10])*19
                            +int(vl[11])*17+int(vl[12])*13+int(vl[13])*7+int(vl[14])*3)%11

                        if op in (0,1):
                            dvcal = str(op)
                        else:
                            dvcal = str(11-op)
                        if  dv != dvcal:
                            return False
        return True

# Mensajes de error
# Error Messages

    _constraints = [
        (_check_name, '¡Error! - El nombre no ha sido actualizado, escriba nuevamente el primer apellido', ['name']),
        (_check_ident, '¡Error! Número de identificación debe tener entre 6 y 11 dígitos', ['ref']),
        (_check_unique_ident, '¡Error! Número de identificación ya existe en el sistema', ['ref']),
        (_check_dv, '¡Error! El digito de verificación es incorrecto',['dv']),
        (_check_ident_num, 'Error !''El número de identificación sólo permite números', ['ref']),
        ]

res_partner_co()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
