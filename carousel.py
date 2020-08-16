from linebot.models import (
    CarouselTemplate, CarouselColumn,URITemplateAction)
import requests

def create_carousel(rest_colum):
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url=rest["image_url"],
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
                # "category_s":"RSFST09004",
                "latitude":lat,
                "longitude":lon,
                "range":5,
                "hit_per_page":10
                }


    rest = requests.get(URL, params = api_params).json()["rest"]
    json_datas = [data for data in rest]
    return json_datas

