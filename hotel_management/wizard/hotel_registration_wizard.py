import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HotelRegistrationWizard(models.TransientModel):
    _name = "hotel.registration.wizard"
    _description = 'Hotel Registration Wizard'

    # المرحلة الأولى: المعلومات الشخصية
    name = fields.Char(string='Guest Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    subscription_type = fields.Selection([
        ('normal', 'Normal'),
        ('vip', 'VIP')
    ], string='Subscription Type', default='normal')

    # المرحلة الثانية: معلومات الغرفة
    room_id = fields.Many2one('rooms', string='Room Number', domain="[('state', '=', 'ready')]")
    check_in_date = fields.Date(string='Check-in Date')
    check_out_date = fields.Date(string='Check-out Date')
    note = fields.Text(string='Notes')

    # مراحل العملية
    stage = fields.Selection([
        ('stage1', 'Personal Information'),
        ('stage2', 'Room Selection')
    ], string='Stage', default='stage1')

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if not record.phone.isdigit():
                raise ValidationError("Phone number must contain only digits.")

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError("Invalid email format.")

    @api.constrains('check_out_date')
    def _check_dates(self):
        for record in self:
            if record.check_out_date and record.check_in_date:
                if record.check_out_date <= record.check_in_date:
                    raise ValidationError("Check-out date must be after check-in date.")

    def action_next_stage(self):
        self.ensure_one()
        # التحقق من صحة البيانات قبل الانتقال
        if not all([self.name, self.phone, self.email]):
            raise ValidationError("Please fill in all required fields.")

        self._check_phone()
        self._check_email()

        self.stage = 'stage2'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_submit_request(self):
        self.ensure_one()
        # التحقق من صحة البيانات قبل الإرسال
        if not all([self.room_id, self.check_in_date, self.check_out_date]):
            raise ValidationError("Please fill in all room information fields.")

        self._check_dates()

        # إنشاء طلب جديد في نموذج الطلبات
        request = self.env['hotel.registration.request'].create({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subscription_type': self.subscription_type,
            'room_id': self.room_id.id,
            'check_in_date': self.check_in_date,
            'check_out_date': self.check_out_date,
            'note': self.note,
            'state': 'pending'
        })

        # إغلاق الويزارد
        return {
            'type': 'ir.actions.act_window_close',
            'effect': {
                'type': 'rainbow_man',
                'message': 'Your request has been submitted successfully!'
            }
        }