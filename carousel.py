from linebot.models import (
    CarouselTemplate, CarouselColumn,URITemplateAction)
import requests

def create_carousel(rest_colum):
    arr = []
    for rest in rest_colum:
            if rest["image_url"]["shop_image1"]=="":
                rest["image_url"]["shop_image1"] = "http://illustrain.com/img/work/2016/illustrain01-okashi08.png"
            arr.append(rest)
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnailImageUrl=rest["image_url"]["shop_image1"],
                text=rest["name"],
                actions=[
                    URITemplateAction(
                        label="開く",
                        uri=rest["url_mobile"]
                        )]
            )
            for rest in arr
        ]
    )
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
    

