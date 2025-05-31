from httplib2.auth import params

from odoo import http
from odoo.http import request
import json


class GuestGetApi(http.Controller):

    @http.route('/api/guest/<int:guest_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_guest(self, guest_id, **kwargs):
        try:
            guest = request.env['hotel.guests'].sudo().search([('id', '=', guest_id)])

            if not guest:
                return request.make_response(
                    json.dumps({'error': 'Guest not found'}),
                    headers=[('Content-Type', 'application/json')],
                    status=404
                )

            guest_data = {
                'id': guest.id,
                'name': guest.name,
                'check_out_date': guest.check_out_date.strftime('%Y-%m-%d') if guest.check_out_date else None,
                'room_id': guest.room_id.id if guest.room_id else None,
                'out': guest.out
            }

            return request.make_response(
                json.dumps(guest_data),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/guest/info', type='http', auth='none', methods=['POST'], csrf=False)
    def get_guest_info(self):
        try:
            # Check if request has data
            if not request.httprequest.data:
                return request.make_json_response({"error": "No data provided"}, status=400)

            # Parse the JSON data
            try:
                val = json.loads(request.httprequest.data.decode('utf-8'))
            except json.JSONDecodeError:
                return request.make_json_response({"error": "Invalid JSON format"}, status=400)

            # Check if either email or phone is provided
            if not val.get('email') and not val.get('phone'):
                return request.make_json_response(
                    {'error': 'email or phone is required'},
                    status=400
                )

            # Filter and validate input values
            filtered_vals = {}
            for key, value in val.items():
                if isinstance(value, (dict, list)):
                    return request.make_json_response({
                        "error": f"Invalid data type for field '{key}'. Nested structures are not supported."
                    }, status=400)
                if value:
                    filtered_vals[key] = value

            if not filtered_vals:
                return request.make_json_response({"error": "No valid search criteria provided"}, status=400)

            # Build SQL query
            cr = request.env.cr
            conditions = []
            params = []
            for key, value in filtered_vals.items():
                conditions.append(f"{key} = %s")
                params.append(value)

            query = f"SELECT * FROM public.hotel_guests WHERE {' AND '.join(conditions)}"

            try:
                cr.execute(query, params)
                res = cr.fetchone()

                if not res:
                    return request.make_json_response({"error": "Guest not found"}, status=404)

                # Convert result to dictionary (assuming res is a tuple)
                columns = [desc[0] for desc in cr.description]
                res_dict = dict(zip(columns, res))

                response = {
                    "user_name": res_dict.get('name'),
                    "email": res_dict.get('email'),
                    "phone": res_dict.get('phone'),
                    "room_number": res_dict.get('room_id'),  # You might need to join with room table
                    "check_in_date": res_dict.get('check_in_date'),
                    "check_out_date": res_dict.get('check_out_date'),
                }

                return request.make_json_response(response)

            except Exception as db_error:
                request.env.cr.rollback()
                return request.make_json_response({
                    "error": "Database error",
                    "details": str(db_error)
                }, status=500)

        except Exception as e:
            return request.make_json_response({
                "error": "Internal server error",
                "details": str(e)
            }, status=500)
