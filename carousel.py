from linebot.models import (
    CarouselTemplate, CarouselColumn,URITemplateAction)
import requests

def create_carousel(rest_colum):
    arr = []
    for rest in rest_colum:
            if rest["image_url"]["shop_image1"]=="":
                if "jpeg" not in rest["image_url"]["shop_image1"] and "png" not in rest["image_url"]["shop_image1"]:
                    rest["image_url"]["shop_image1"] = "http://illustrain.com/img/work/2016/illustrain01-okashi08.png"
            
            if rest["opentime"] == "":
                rest["opentime"] = "情報なし"
            
            if rest["holiday"] == "":
                rest["holiday"] = "情報なし"

            arr.append(rest)
    carousel_template = CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnailImageUrl=rest["image_url"]["shop_image1"],
                text=rest["name"] + "\n【営業時間】" + rest["opentime"] + "\n【休業日】" + rest["holiday"],
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
                "category_s":"RSFST18002",
                "latitude":lat,
                "longitude":lon,
                "range":5,
                "hit_per_page":10
                }

    try:
        rest = requests.get(URL, params = api_params).json()["rest"]
        json_datas = [data for data in rest]
        return json_datas
    except KeyError:
        return 0


def izakaya_search(lat,lon):
    URL = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
    api_params = {
                "keyid":"45747be45373a6faec585372092743d9",
                "category_l":"RSFST09000",
                "latitude":lat,
                "longitude":lon,
                "range":5,
                "hit_per_page":10
                }

    try:
        rest = requests.get(URL, params = api_params).json()["rest"]
        json_datas = [data for data in rest]
        return json_datas
    except KeyError:
        return 0

