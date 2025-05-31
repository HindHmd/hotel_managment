import json
from  odoo import  http
from odoo.http import request

class GuestsApi(http.Controller):

    # @http.route('/v1/property' , methods=['POST'] , type='http', auth='none', csrf=False)
    # def post_property(self):
    #     args= request.httprequest.data.decode()
    #     vals= json.loads(args)
    #     if not vals.get('name'):
    #         return request.make_json_response( "name is required",status= 400)
    #
    #     try:
    #         res = request.env['property'].sudo().create(vals)
    #         if res:
    #             return request.make_json_response({
    #                 'massage': 'property created successfully',
    #                 'id': res.id
    #             },status= 200)
    #     except Exception as error :
    #         return request.make_json_response(error, status=400)
    @http.route('/v1/guests', methods=['POST'], type='http', auth='none', csrf=False)
    def post_guest(self):
        try:

            if not request.httprequest.data:
                return request.make_json_response({"error": "No data provided"}, status=400)



            args = request.httprequest.data.decode('utf-8')
            vals = json.loads(args)


            if not vals.get('name'):
                return request.make_json_response({"error": "name is required"}, status=400)

            # تصفية القيم لضمان أنها قيم بسيطة وليست nested dictionaries
            filtered_vals = {}
            for key, value in vals.items():
                if isinstance(value, (dict, list)):
                    return request.make_json_response({
                        "error": f"Invalid data type for field '{key}'. Nested structures are not supported."
                    }, status=400)
                filtered_vals[key] = value

            cr = request.env.cr
            columns = ','.join(filtered_vals.keys())
            placeholders = ','.join(['%s'] * len(filtered_vals))
            query = f"INSERT INTO hotel_registration_request({columns}) VALUES ({placeholders}) RETURNING id, name, email"
            json_ready_vals = [json.dumps(v) for v in filtered_vals.values()]
            try:
                cr.execute(query, json_ready_vals)
                res = cr.fetchone()

                if res:
                    return request.make_json_response({
                        'message': 'hotel request created successfully',
                        'id': res[0],
                        'name': res[1],
                        'email': res[2]
                    }, status=201)

            except Exception as db_error:
                request.env.cr.rollback()
                return request.make_json_response({
                    "error": "An error occurred while creating hotel.registration.request",
                    "details": str(db_error)
                }, status=500)

        except Exception as e:
            return request.make_json_response({"error": str(e)}, status=500)
