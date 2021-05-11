import os, json
from flask import Flask, render_template, request
import requests

# carregando a chave do Azure Maps
MAP_KEY = os.environ["MAP_KEY"]

# carregando a chave dos dados da AQI
WAQI_API_KEY = os.environ["WAQI_API_KEY"]
WAQI_API_URL = "https://api.waqi.info/map/bounds/?latlng={},{},{},{}&token={}"

# inicializando o app Flask
app = Flask(__name__)

# lidando com solicitações do site e retornando para a homepage
@app.route("/")
def home():
    # indo da homepage para a chave do mapa
    data = { "map_key" : MAP_KEY }
    # retornando para a homepage
    return render_template("home.html", data = data)

def get_color(aqi):
    # convertendo os valores da AQI em cor
    if aqi <= 50: return "#009966"
    if aqi <= 100: return "#ffde33"
    if aqi <= 150: return "#ff9933"
    if aqi <= 200: return "#cc0033"
    if aqi <= 300: return "#660099"
    return "#7e0023"

def load_aqi_data(lon1, lat1, lon2, lat2):
    # carregando os dados de qualidade de ar
    url = WAQI_API_URL.format(lat1, lon1, lat2, lon2, WAQI_API_KEY)
    aqi_data = requests.get(url)

    # criando uma coleção de recursos a partir dos dados do GeoJSON
    feature_collection = {
        "type" : "FeatureCollection",
        "features" : []
    }

    for value in aqi_data.json()["data"]:
        # filtrando valores vazios
        if value["aqi"] != "-":
            feature_collection["features"].append({
                "type" : "Feature",
                "properties" : {
                    "color" : get_color(int(value["aqi"]))
                },
                "geometry" : {
                    "type":"Point",
                    "coordinates":[value['lon'], value['lat']]
                }
                })

    return feature_collection

@app.route("/aqi", methods = ["GET"])
def get_aqi():
    # solicitações
    bounds = request.args["bounds"].split(",")

    # carregando os dados da AQI e criando o GeoJSON para os limites especificados
    return json.dumps(load_aqi_data(bounds[0], bounds[1], bounds[2], bounds[3]))
