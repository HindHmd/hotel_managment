import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelRegistration(models.Model):
    _name = "hotel.registration"
    _description = 'Hotel Registration'
    _inherit = 'hotel.guests'

    note = fields.Text()
    stage = fields.Selection([
        ('stage1', 'personal_info'),
        ('stage2', 'room_selection')
    ], string='Stage', default='stage1')

    @api.constrains('check_out_date')
    def _check_dates(self):
        for record in self:
            if record.check_out_date <= record.check_in_date:
                raise ValidationError("Check-out date must be after check-in date.")

    def action_next_stage(self):
        for rec in self:
            # تحقق من صحة البيانات قبل الانتقال
            if not rec.name or not rec.phone or not rec.email:
                raise ValidationError("Please fill in all required personal info fields.")
            if not re.match(r'^\d+$', rec.phone):
                raise ValidationError("Phone number should contain digits only.")
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', rec.email):
                raise ValidationError("Invalid email format.")
            rec.stage = 'stage2'

    def action_approve_request(self):
        if self.stage == 'stage2':
            if all([self.room_id, self.check_in_date, self.check_out_date]):

                self.room_id.rental_count += 1
                if self.room_id.rental_count >= 1:
                    self.room_id.state = 'cleaning'

                guest = self.env['hotel.guests'].create({
                    'name': self.name,
                    'phone': self.phone,
                    'email': self.email,
                    'subscription_type': self.subscription_type,
                    'room_id': self.room_id.id,
                    'check_in_date': self.check_in_date,
                    'check_out_date': self.check_out_date,
                    'notes': self.note
                })

                self.unlink()
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'hotel.guests',
                    'view_mode': 'form',
                    'res_id': guest.id,
                    'target': 'current',
                }
            else:
                raise ValidationError("Please complete all fields before submitting.")
