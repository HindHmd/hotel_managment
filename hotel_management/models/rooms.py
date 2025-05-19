from datetime import timedelta

from odoo import models,fields,api

class Rooms(models.Model):
    _name = "rooms"
    _description = 'Hotel Room'
    name=fields.Char(required=True)
    ref = fields.Char(string="ref", readonly=True, default='New')
    floor=fields.Integer()
    available_rooms=fields.Integer(compute='_compute_available_rooms')
    occupied_rooms=fields.Integer(compute='_compute_occupied_rooms')
    state=fields.Selection([('ready','Ready'),
                            ('cleaning','Cleaning'),('repair','Repair'),
                            ],string='Room state' , default="ready"),

    rental_count=fields.Integer()

    guests_ids=fields.One2many('hotel.guests','room_id', string="Guests")
    @api.depends('guests_ids')
    def _compute_available_rooms(self):
            for room in self:
                room.available_rooms=room.occupied_rooms-len(room.guests_ids)

    @api.depends('guests_ids')
    def _compute_occupied_rooms(self):
        for room in self:
            room.occupied_rooms=len(room.guests_ids)
    @api.model
    def update_room_state (self):
        guests=self.env["hotel.guests"].search(['check_out_date','<=',fields.Date.today()])
        for rec in guests :
           if rec.check_out_date & rec.check_out_date <= fields.Date.today():
               room = rec.room_id
               if room.rental_count=="0":
                   room.state = "ready"
               else:
                   rental_time=rec.check_out_date+timedelta(days=1)
                   if fields.Date.today() >= rental_time:
                       room.state = "cleaning"
                   else:
                       room.state="repair"
               rec.room_id.rental_count += 1
    @api.model
    def create(self, vals):
       res= super(Rooms,self).create(vals)
       if res.ref == 'New':
           res.ref = self.env['ir.sequence'].next_by_code('rooms_sequence')
       return res