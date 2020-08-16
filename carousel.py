from linebot.models import (
    CarouselTemplate, CarouselColumn,URITemplateAction)
import requests

def create_carousel(rest_colum):
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                text=rest["name"],
                actions=[
                    URITemplateAction(
                        label="開く",
                        uri=rest["url_mobile"]
                        )]
                    )
                for rest in rest_colum
                ])
    return carousel_template

def rest_search(lat,lon):
    URL = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
    api_params = {
                "keyid":"45747be45373a6faec585372092743d9",
                # "category_s":"RSFST18008,RSFST18009,RSFST18010,RSFST18011,RSFST18012",
                "latitude":lat,
                "longitude":lon,
                "range":3,
                "hit_per_page":5
                }

    rest = requests.get(URL, params = api_params).json()["rest"]
    json_datas = [data for data in rest]
    return json_datas
