import json


class OfferRow:
    def __init__(self, ID=None, title="", lat=None, lon=None, location="", url="", slug="", ref="", description="",
                 weekly_low=0, weekly_high=0, sleeps="", bedrooms="", dog=False, child=False, wifi=False, late_offer="",
                 late_nights=0, late_price=0, late_savings_tag=""):
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

    def to_cottage(self):
        var_dic = dict(vars(self))  # cast to dict to make copy, so pop() doesn't remove from main
        var_dic.pop('late_offer')
        var_dic.pop('late_nights')
        var_dic.pop('late_price')
        var_dic.pop('late_savings_tag')
        return CottageJSON(*var_dic.values())


class CottageJSON:
    def __init__(self, title="", lat=None, lon=None, location="", url="", slug="", ref="", description="",
                 weekly_low=0, weekly_high=0, sleeps="", bedrooms="", dog=False, child=False, wifi=False):
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

    def serialize(self):
        _vars = vars(self)
        # Manually serialize non-serializable items
        _vars['late_offers'] = [vars(offer) for offer in self.late_offers]
        _vars['lat'] = str(self.lat)
        _vars['lon'] = str(self.lon)
        return _vars

    def to_json(self):
        return json.dumps(self.serialize())


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