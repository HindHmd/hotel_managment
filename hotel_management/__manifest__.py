{
    'name': "hotel_management",
    'author': "hind",
    'version': "16.0.0.4.0",
    'category': "",
    'depends': ['base' ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/guests_view.xml',
        'views/room_view.xml',
        'wizard/hotel_guest_registar_wizard_view.xml' ,
        'views/view_registration_request_view.xml' ,

    ],
    'application': True,
}