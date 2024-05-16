from odoo import models, fields, api
import requests
from odoo.http import request as req
from odoo.exceptions import ValidationError


def get_credentials():
    url = "https://api-hermes.pathao.com/aladdin/api/v1/issue-token"
    user_credentials = req.env['pathao.user.credentials'].sudo().search(
        [], order='id desc', limit=1)
    data = {
        'client_id': 'MYer0ywbOB',
        'client_secret': '4LJkRsHdGf6g0Z0lwIIzS9bi0oP8NkaUoULrGkzz',
        'username': user_credentials.username,
        'password': user_credentials.password,
        'grant_type': 'password'
    }

    headers = {
        'accept': "application/json",
        'content-type': "application/json"
    }

    try:
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            final_response = response.json()
            access_token = final_response.get('access_token')
            refresh_token = final_response.get('refresh_token')
            return access_token, refresh_token
        else:
            print("Error:", response.text)
            raise ValidationError('Authentication Failed!')

    except Exception as e:
        print("Error:", e)
        raise ValidationError('Authentication Failed!')

def create_an_order(data, access_token):
    url = "https://api-hermes.pathao.com/aladdin/api/v1/orders"

    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': "application/json",
        'Accept': "application/json"
    }

    try:
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            final_response = response.json()
            print(final_response)
        else:
            print("Error:", response.text)

    except Exception as e:
        print("Error:", e)


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    store_id = fields.Many2one('pathao.stores', string='Store')
    merchant_order_id = fields.Char(string='Merchant Order ID (optional)')
    recipient_name = fields.Char(string='Recipient Name')
    recipient_phone = fields.Char(string='Recipient Phone')
    recipient_address = fields.Text(string='Recipient Address')
    recipient_city = fields.Many2one('pathao.cities', string='Recipient City')
    recipient_zone = fields.Many2one('pathao.zones', string='Recipient Zone')
    recipient_area = fields.Many2one('pathao.areas', string='Recipient Area')
    special_instruction = fields.Text('Special Instruction (optional)')
    item_quantity = fields.Integer(string='Item Quantity')
    item_weight = fields.Float(string='Item Weight')
    amount_to_collect = fields.Integer(string='Amount to Collect', default=0)
    item_description = fields.Text(string='Item Description (optional)')
    is_pathao = fields.Boolean(string='Is sent', default=False)

    def send_sale_order_to_pathao(self):
        print('pathaw button clicked!!!')
        store_id = self.store_id.store_id
        merchant_order_id = self.merchant_order_id if self.merchant_order_id else self.name
        recipient_name = self.recipient_name
        recipient_phone = self.recipient_phone
        recipient_address = self.recipient_address
        recipient_city = self.recipient_city.city_id
        recipient_zone = self.recipient_zone.zone_id
        recipient_area = self.recipient_area.area_id
        special_instruction = self.special_instruction
        item_quantity = self.item_quantity
        item_weight = self.item_weight
        amount_to_collect = self.amount_to_collect
        item_description = self.item_description

        if not self.store_id:
            raise ValidationError("A store should be there.")

        if not self.recipient_name:
            raise ValidationError("Recipient name should be there.")

        if not self.recipient_phone:
            raise ValidationError("Recipient phone number should be there.")

        if not self.recipient_address or len(self.recipient_address) < 10:
            raise ValidationError(
                "Recipient address should be there and must have length of at least 10 characters.")

        if not self.recipient_city:
            raise ValidationError("Recipient City should be there.")

        if not self.recipient_zone:
            raise ValidationError("Recipient Zone should be there and it should be a valid zone.")

        if (self.recipient_zone and self.recipient_city) and (self.recipient_zone.city_id != self.recipient_city):
            raise ValidationError('Wrong zone in the selected city.')

        if not self.recipient_area:
            raise ValidationError("Recipient Area should be there and it should be a valid area.")

        if (self.recipient_area and self.recipient_zone) and (self.recipient_area.zone_id != self.recipient_zone):
            raise ValidationError('Wrong area in the selected zone.')

        if not self.item_quantity:
            raise ValidationError("Item quantity should be there.")

        if not self.item_weight or not (self.item_weight >= 0.5 and self.item_weight <= 10.0):
            raise ValidationError(
                "Item Weight should be there and it should be 0.5 to 10.0.")

        if not self.amount_to_collect:
            raise ValidationError("Amount to collect should be there.")

        data = {
            'store_id': store_id,
            'merchant_order_id': merchant_order_id,
            'recipient_name': recipient_name,
            'recipient_phone': recipient_phone,
            'recipient_address': recipient_address,
            'recipient_city': recipient_city,
            'recipient_zone': recipient_zone,
            'recipient_area': recipient_area,
            'delivery_type': 48,
            'item_type': 2,
            'special_instruction': special_instruction,
            'item_quantity': item_quantity,
            'item_weight': item_weight,
            'amount_to_collect': amount_to_collect,
            'item_description': item_description
        }

        credentials = self.env['pathao.api.credentials'].sudo().search(
            [], order='id desc', limit=1)
        access_token = credentials.access_token
        if not credentials:
            access_token = get_credentials()[0]

        create_an_order(data, access_token)
        self.is_pathao = True

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Order Created Successfully',
                'type': 'rainbow_man'
            }
        }


class PathaoApiCredentials(models.Model):
    _name = 'pathao.api.credentials'
    _description = 'pathao.api.credentials'

    access_token = fields.Text(string='Access Token')
    refresh_token = fields.Text(string='Refresh Token')


class PathaoUserCredentials(models.Model):
    _name = 'pathao.user.credentials'
    _description = 'pathao.user.credentials'

    username = fields.Char(string='Username')
    password = fields.Char(string='Password')


class PathaoStores(models.Model):
    _name = 'pathao.stores'
    _description = 'pathao.stores'
    _rec_name = 'store_name'

    store_id = fields.Integer(string='Store ID')
    store_name = fields.Char(string='Store Name')


class PathaoCities(models.Model):
    _name = 'pathao.cities'
    _description = 'pathao.cities'
    _rec_name = 'city_name'

    city_id = fields.Integer(string='City ID')
    city_name = fields.Char(string='City Name')


class PathaoZones(models.Model):
    _name = 'pathao.zones'
    _description = 'pathao.zones'
    _rec_name = 'zone_name'

    zone_id = fields.Integer(string='Zone ID')
    zone_name = fields.Char(string='Zone Name')
    city_id = fields.Many2one('pathao.cities', string='City ID')


class PathaoAreas(models.Model):
    _name = 'pathao.areas'
    _description = 'pathao.areas'
    _rec_name = 'area_name'

    area_id = fields.Integer(string='Area ID')
    area_name = fields.Char(string='Area Name')
    zone_id = fields.Many2one('pathao.zones', string='Zone ID')


class AutomatePathaoApiCredentialsRetrieval(models.Model):
    _name = 'pathao.automate.api.credentials.retrieval'
    _description = 'pathao.automate.api.credentials.retrieval'

    @api.model
    def retrieve_credentials(self):
        existing_tokens = self.env['pathao.api.credentials'].sudo().search(
            [], order='id desc', limit=1)

        if existing_tokens:
            existing_tokens.access_token = existing_tokens.access_token
            existing_tokens.refresh_token = existing_tokens.refresh_token
            self.env.cr.commit()
        else:
            self.env['pathao.api.credentials'].sudo().create({
                'access_token': get_credentials()[0],
                'refresh_token': get_credentials()[1]
            })


class AutomatePathaoStoresRetrieval(models.Model):
    _name = 'pathao.stores.retrieval'
    _description = 'pathao.stores.retrieval'

    @api.model
    def retrieve_stores(self):
        url = "https://api-hermes.pathao.com/aladdin/api/v1/stores"

        credentials = self.env['pathao.api.credentials'].sudo().search(
            [], order='id desc', limit=1)
        access_token = credentials.access_token
        if not credentials:
            access_token = get_credentials()[0]

        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': "application/json",
            'Accept': "application/json"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                final_response = response.json()
                all_stores = final_response.get('data').get('data')
                for store in all_stores:
                    existing_store = self.env['pathao.stores'].sudo().search(
                        [('store_id', '=', store.get('store_id'))])
                    if not existing_store:
                        self.env['pathao.stores'].sudo().create({
                            'store_id': store.get('store_id'),
                            'store_name': store.get('store_name')
                        })

            else:
                print("Error:", response.text)

        except Exception as e:
            print("Error:", e)


class AutomatePathaoCitiesRetrieval(models.Model):
    _name = 'pathao.cities.retrieval'
    _description = 'pathao.cities.retrieval'

    @api.model
    def retrieve_cities(self):
        url = "https://api-hermes.pathao.com/aladdin/api/v1/city-list"

        credentials = self.env['pathao.api.credentials'].sudo().search(
            [], order='id desc', limit=1)
        access_token = credentials.access_token
        if not credentials:
            access_token = get_credentials()[0]

        headers = {
            'Authorization': f"Bearer {access_token}",
            'Content-Type': "application/json",
            'Accept': "application/json"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                final_response = response.json()
                all_cities = final_response.get('data').get('data')

                for city in all_cities:
                    existing_city = self.env['pathao.cities'].sudo().search(
                        [('city_id', '=', city.get('city_id'))])
                    if not existing_city:
                        self.env['pathao.cities'].sudo().create({
                            'city_id': city.get('city_id'),
                            'city_name': city.get('city_name')
                        })

            else:
                print("Error:", response.text)

        except Exception as e:
            print("Error:", e)


class AutomatePathaoZonesRetrieval(models.Model):
    _name = 'pathao.zones.retrieval'
    _description = 'pathao.zones.retrieval'

    @api.model
    def retrieve_zones(self):
        all_cities = self.env['pathao.cities'].sudo().search([])
        for city in all_cities:
            url = f"https://api-hermes.pathao.com/aladdin/api/v1/cities/{city.city_id}/zone-list"

            credentials = self.env['pathao.api.credentials'].sudo().search(
                [], order='id desc', limit=1)
            access_token = credentials.access_token
            if not credentials:
                access_token = get_credentials()[0]

            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': "application/json",
                'Accept': "application/json"
            }

            try:
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    final_response = response.json()
                    all_zones = final_response.get('data').get('data')

                    for zone in all_zones:
                        existing_zone = self.env['pathao.zones'].sudo().search(
                            [('zone_id', '=', zone.get('zone_id'))])
                        if not existing_zone:
                            self.env['pathao.zones'].sudo().create({
                                'zone_id': zone.get('zone_id'),
                                'zone_name': zone.get('zone_name'),
                                'city_id': city.id
                            })

                else:
                    print("Error:", response.text)

            except Exception as e:
                print("Error:", e)


class AutomatePathaoAreasRetrieval(models.Model):
    _name = 'pathao.areas.retrieval'
    _description = 'pathao.areas.retrieval'

    @api.model
    def retrieve_areas(self):
        all_zones = self.env['pathao.zones'].sudo().search([])
        for zone in all_zones:
            url = f"https://api-hermes.pathao.com/aladdin/api/v1/zones/{zone.zone_id}/area-list"
            credentials = self.env['pathao.api.credentials'].sudo().search(
                [], order='id desc', limit=1)
            access_token = credentials.access_token
            if not credentials:
                access_token = get_credentials()[0]

            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': "application/json",
                'Accept': "application/json"
            }

            try:
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    final_response = response.json()
                    all_areas = final_response.get('data').get('data')

                    for area in all_areas:
                        existing_area = self.env['pathao.areas'].sudo().search(
                            [('area_id', '=', area.get('area_id'))])
                        if not existing_area:
                            self.env['pathao.areas'].sudo().create({
                                'area_id': area.get('area_id'),
                                'area_name': area.get('area_name'),
                                'zone_id': zone.id
                            })

                else:
                    print("Error:", response.text)

            except Exception as e:
                print("Error:", e)
