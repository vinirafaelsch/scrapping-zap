import json
import locale

from datetime import datetime

class HandleFile:
    def __init__(self, data):
        self.extracted_data: list = data
        self.geojson_data: dict = {}

        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    def data2geojson(self):
        geojson = {
            "type": "FeatureCollection",
            "name": "Modelo_Arquivo_ExtraçãoZAP_recorte",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "id": self.format_value(data.get('id', "")),
                        "cidade": self.format_value(data.get('address', {}).get('city', "")),
                        "rua": self.format_value(data.get('address', {}).get('street', "")),
                        "bairro": self.format_value(data.get('address', {}).get('neighborhood', "")),
                        "numero": self.format_value(data.get('address', {}).get('streetNumber', "")),
                        # "lat": data.get('address', {}).get('coordinate', {}).get('lat', ""),
                        # "lng": data.get('address', {}).get('coordinate', {}).get('lng', ""),
                        # "radius": data.get('address', {}).get('coordinate', {}).get('radius', ""),
                        "valor": self.value2real(self.format_value(data.get('prices', {}).get('mainValue', ""))),
                        "iptu": self.value2real(self.format_value(data.get('prices', {}).get('iptu', ""))),
                        "condominium": self.value2real(self.format_value(data.get('prices', {}).get('condominium', ""))),
                        "descricao": self.format_value(data.get('description', "")),
                        "area": self.format_value(data.get('amenities', {}).get('usableAreas', "")),
                        "quartos": self.format_value(data.get('amenities', {}).get('bedrooms', "")),
                        "banheiros": self.format_value(data.get('amenities', {}).get('bathrooms', "")),
                        "estacionamentos": self.format_value(data.get('amenities', {}).get('parkingSpaces', "")),
                        "url": self.format_value(data.get('url', "")),
                        "tipo_negocio": self.format_value(data.get('business', "")),
                        "tipo_imovel": self.handle_unit_types(data.get('unitTypes', "")),
                        "data_extracao": datetime.today().strftime('%d-%m-%Y')
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
    
    def format_value(self, value):
        if isinstance(value, type(None)) or value == "":
            return "Não informado"
        return value

    def value2real(self, value):
        if value != "Não informado":
            return locale.currency(float(value), grouping=True)
        return value
    
    def handle_unit_types(self, data):
        if data == "Não informado":
            return "Não informado"
        
        if len(data) == 1:
            return data[0]
        
        string = ""
        for value in data:
            string = (f'{string}; {value}') if not string == "" else value
        return string

    def create_file(self):
        self.geojson_data = self.data2geojson()

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"imoveis_zap_{timestamp}.geojson"

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.geojson_data, file, ensure_ascii=False, indent=4)

