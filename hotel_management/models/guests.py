import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HotelGuests(models.Model):
    _name = "hotel.guests"
    _description = 'Hotel Guest'
    name=fields.Char(required=True ,string='guests name')
    email=fields.Char(required=True ,string='Email')
    phone=fields.Char(required=True ,string='Phone')
    check_in_date=fields.Date(required=True)
    check_out_date = fields.Date(required=True)
    out=fields.Boolean()
    subscription_type=fields.Selection([('normal','Normal'),('vip','VIP')],default='normal',string='Subscription Type')
    room_id=fields.Many2one('rooms', string="room number")
    feedback_ids = fields.One2many('hotel.feedback', 'hotel_guests_id', string='nots')

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if not record.phone.isdigit():
                raise ValidationError("Phone number must contain only digits.")

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if not re.match(r"[^@]+@[^@]+.[^@]+", record.email):
                raise ValidationError("Invalid email format.")



    def check_out_date_daily(self):
           guests_ids=self.search([])
           for rec in guests_ids:
                if rec.check_out_date and rec.check_out_date < fields.Date.today():
                   rec.out=True



