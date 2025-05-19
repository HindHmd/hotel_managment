

from odoo import models,fields


class HotelFeedback(models.Model):
    _name = "hotel.feedback"
    _description = 'Hotel Feedback'
    hotel_guests_id = fields.Many2one('hotel.guests','Guest')
    description=fields.Char(required=True ,string='guests name')


