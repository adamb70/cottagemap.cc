import base64
import json

empty_b64_jpg = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCACWASwDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AJ/4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/Z"


class OfferRow:
    def __init__(self, ID=None, title="", lat=None, lon=None, location="", url="", slug="", ref="", description="",
                 weekly_low=0, weekly_high=0, sleeps="", bedrooms="", dog=False, child=False, wifi=False, late_offer="",
                 late_nights=0, late_price=0, late_savings_tag="", image=None, img_url=""):
        self.title = title
        self.lat = lat
        self.lon = lon
        self.location = location
        self.url = url
        self.slug = slug
        self.ref = ref
        self.description = description
        self.weekly_low = weekly_low
        self.weekly_high = weekly_high
        self.sleeps = sleeps
        self.bedrooms = bedrooms
        self.dog = dog
        self.child = child
        self.wifi = wifi
        self.late_offer = late_offer
        self.late_nights = late_nights
        self.late_price = late_price
        self.late_savings_tag = late_savings_tag
        self.image = image
        self.img_url = img_url

    def to_cottage(self):
        var_dic = dict(vars(self))  # cast to dict to make copy, so pop() doesn't remove from main
        var_dic.pop('late_offer')
        var_dic.pop('late_nights')
        var_dic.pop('late_price')
        var_dic.pop('late_savings_tag')
        return CottageJSON(*var_dic.values())


class CottageJSON:
    def __init__(self, title="", lat=None, lon=None, location="", url="", slug="", ref="", description="",
                 weekly_low=0, weekly_high=0, sleeps="", bedrooms="", dog=False, child=False, wifi=False, image=None, img_url=""):
        self.title = title
        self.lat = lat
        self.lon = lon
        self.location = location
        self.url = url
        self.slug = slug
        self.ref = ref
        self.description = description
        self.weekly_low = weekly_low
        self.weekly_high = weekly_high
        self.sleeps = sleeps
        self.bedrooms = bedrooms
        self.dog = dog
        self.child = child
        self.wifi = wifi
        self.late_offers = []
        self.image = image
        self.img_url = img_url

    def serialize(self, use_b64_image=False):
        # Make copy of vars
        _vars = dict(vars(self))
        # Manually serialize non-serializable items
        _vars['late_offers'] = [vars(offer) for offer in self.late_offers]
        _vars['lat'] = str(self.lat)
        _vars['lon'] = str(self.lon)

        # Delete img_url from vars, will only use either b64 or url interchangeably
        del _vars['img_url']
        if use_b64_image:
            try:
                _vars['image'] = 'data:image/png;base64,{}'.format(base64.b64encode(self.image).decode())
            except TypeError:
                # Image was null
                _vars['image'] = empty_b64_jpg
        else:
            _vars['image'] = self.img_url

        return _vars

    def to_json(self, use_b64_image=False):
        return json.dumps(self.serialize(use_b64_image))


class LateOffer:
    offer = "",
    nights = 0,
    price = 0,
    savings_tag = ""


REGION_TABLES = {
    'north east england': "northeastengland",
    'north west england': "northwestengland",
    'central england': "centralengland",
    'north wales': "northwales",
    'south wales': "southwales",
    'eastern central england': "easterncentralengland",
    'eastern england & east anglia': "eastanglia",
    'south west england': "southwestengland",
    'south and south east england': "southeastengland",
    'south west scotland': "southwestscotland",
    'south east scotland': "southeastscotland",
    'west central scotland': "westcentralscotland",
    'east central scotland': "eastcentralscotland",
    'scottish highlands': "scottishhighlands",
    'northern ireland': "northernireland",
}

INV_REGION_TABLES = {y: x for x, y in REGION_TABLES.items()}

GROUPED_REGIONS = {
    'north west england': [REGION_TABLES['north west england']],
    'north east england': [REGION_TABLES['north east england']],
    'wales': [REGION_TABLES['north wales'], REGION_TABLES['south wales']],
    'northern ireland': [REGION_TABLES['northern ireland']],
    'central england': [REGION_TABLES['central england'], REGION_TABLES['eastern central england']],
    'south east england': [REGION_TABLES['eastern england & east anglia'], REGION_TABLES['south and south east england']],
    'south west england': [REGION_TABLES['south west england']],
    'scotland': [REGION_TABLES['south west scotland'], REGION_TABLES['south east scotland'],
                 REGION_TABLES['west central scotland'], REGION_TABLES['east central scotland'],
                 REGION_TABLES['scottish highlands']]
}
