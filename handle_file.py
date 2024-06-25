import json

from datetime import datetime

class HandleFile:
    def __init__(self, data):
        self.extracted_data: list = data
        self.geojson_data: dict = {}

    def data2geojson(self):
        geojson = {
            "type": "FeatureCollection",
            "name": "Modelo_Arquivo_ExtraçãoZAP_recorte",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "id": data.get('id', ""),
                        "cidade": data.get('address', {}).get('city', ""),
                        "rua": data.get('address', {}).get('street', ""),
                        "bairro": data.get('address', {}).get('neighborhood', ""),
                        "numero": data.get('address', {}).get('streetNumber', ""),
                        # "lat": data.get('address', {}).get('coordinate', {}).get('lat', ""),
                        # "lng": data.get('address', {}).get('coordinate', {}).get('lng', ""),
                        # "radius": data.get('address', {}).get('coordinate', {}).get('radius', ""),
                        "valor": data.get('prices', {}).get('mainValue', ""),
                        "iptu": data.get('prices', {}).get('iptu', ""),
                        "condominium": data.get('prices', {}).get('condominium', ""),
                        "descricao": data.get('description', ""),
                        "area": data.get('amenities', {}).get('usableAreas', ""),
                        "quartos": data.get('amenities', {}).get('bedrooms', ""),
                        "banheiros": data.get('amenities', {}).get('bathrooms', ""),
                        "estacionamentos": data.get('amenities', {}).get('parkingSpaces', ""),
                        "url": data.get('url', ""),
                        "tipo": data.get('business', "")
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            data.get('address', {}).get('coordinate', {}).get('lng', ""),
                            data.get('address', {}).get('coordinate', {}).get('lat', "")
                        ]
                    }
                } for data in self.extracted_data
            ]
        }

        return geojson

    def create_file(self):
        self.geojson_data = self.data2geojson()

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"imoveis_zap_{timestamp}.geojson"

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.geojson_data, file, ensure_ascii=False, indent=4)

