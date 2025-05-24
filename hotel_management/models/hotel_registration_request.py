from odoo import models, fields, api


class HotelRegistrationRequest(models.Model):
    _name = 'hotel.registration.request'
    _description = 'Hotel Registration Requests'
    _order = 'create_date desc'

    name = fields.Char(string='Guest Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    subscription_type = fields.Selection([
        ('normal', 'Normal'),
        ('vip', 'VIP')
    ], string='Subscription Type')
    room_id = fields.Many2one('rooms', string='Room', required=True)
    check_in_date = fields.Date(string='Check-in Date', required=True)
    check_out_date = fields.Date(string='Check-out Date', required=True)
    note = fields.Text(string='Notes')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')

    def action_approve(self):
        for request in self:

            guest = self.env['hotel.guests'].create({
                'name': request.name,
                'email': request.email,
                'phone': request.phone,
                'subscription_type': request.subscription_type,
                'room_id': request.room_id.id,
                'check_in_date': request.check_in_date,
                'check_out_date': request.check_out_date,
            })


            request.room_id.write({
                'state': 'cleaning',
                'rental_count': request.room_id.rental_count + 1
            })

            request.state = 'approved'

        return True

    def action_reject(self):
        self.write({'state': 'rejected'})
        return True