import json
import locale

from datetime import datetime

class HandleFile:
    def __init__(self, data):
        self.extracted_data: list = data
        self.geojson_data: dict = {}

        self.translations = {
            "APARTMENT": "APARTAMENTO",
            "HOME": "CASA",
            "COMMERCIAL_BUILDING": "EDIFÍCIO COMERCIAL",
            "PENTHOUSE": "COBERTURA",
            "ALLOTMENT_LAND": "TERRENO DE LOTEAMENTO",
            "RESIDENTIAL_ALLOTMENT_LAND": "TERRENO DE LOTEAMENTO RESIDENCIAL",
            "COMMERCIAL_ALLOTMENT_LAND": "TERRENO DE LOTEAMENTO COMERCIAL",
            "SHED_DEPOSIT_WAREHOUSE": "ARMAZÉM DE DEPÓSITO EM GALPÃO",
            "FARM": "FAZENDA",
            "CONDOMINIUM": "CONDOMÍNIO",
            "COMMERCIAL_PROPERTY": "IMÓVEL COMERCIAL",
            "OFFICE": "ESCRITÓRIO",
            "BUSINESS": "LOJA, SALÃO, PONTO COMERCIAL" 
        }

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
                        "rua": self.format_value(data.get('address', {}).get('street', "")),
                        "numero": self.format_value(data.get('address', {}).get('streetNumber', "")),
                        "bairro": self.format_value(data.get('address', {}).get('neighborhood', "")),
                        "cidade": self.format_value(data.get('address', {}).get('city', "")),
                        "UF": self.format_value(data.get('address', {}).get('stateAcronym', "")),
                        # "lat": data.get('address', {}).get('coordinate', {}).get('lat', ""),
                        # "lng": data.get('address', {}).get('coordinate', {}).get('lng', ""),
                        # "radius": data.get('address', {}).get('coordinate', {}).get('radius', ""),
                        "valor": self.value2real(self.format_value(data.get('prices', {}).get('mainValue', ""))),
                        "valor_num": data.get('prices', {}).get('mainValue', None),
                        "valor_m2": self.handle_value_m2(self.value2real(self.calc_value_m2(
                            data.get('prices', {}).get('mainValue', ""), data.get('amenities', {}).get('usableAreas', "")
                            ))),
                        "valor_m2_num": self.calc_value_m2(data.get('prices', {}).get('mainValue', ""), data.get('amenities', {}).get('usableAreas', "")),
                        "iptu": self.value2real(self.format_value(data.get('prices', {}).get('iptu', ""))),
                        "condominio": self.value2real(self.format_value(data.get('prices', {}).get('condominium', ""))),
                        "descricao": self.format_value(data.get('description', "")),
                        "area": self.format_area(self.format_value(data.get('amenities', {}).get('usableAreas', ""))),
                        "quartos": self.format_value(data.get('amenities', {}).get('bedrooms', "")),
                        "banheiros": self.format_value(data.get('amenities', {}).get('bathrooms', "")),
                        "estacionamentos": self.format_value(data.get('amenities', {}).get('parkingSpaces', "")),
                        "url": self.format_value(data.get('url', "")),
                        "tipo_negocio": self.business2pt(self.format_value(data.get('business', ""))),
                        "tipo_imovel": self.handle_unit_types(data.get('unitTypes', "")),
                        "data_extracao": datetime.today().strftime('%d/%m/%Y')
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

        if isinstance(value, int) or isinstance(value, float):
            return value

        value = value.replace("\n", "").replace("\\", "").replace('\"', "").replace('"\\', "")

        return value

    def value2real(self, value):
        if value != "Não informado" and value != None:
            return locale.currency(float(value), grouping=True)
        return value

    def format_area(self, value):
        if value != "Não informado":
            return (f'{value}m²')
        return value

    def calc_value_m2(self, value, area):
        if isinstance(value, type(None)) or value == "":
            return None

        if isinstance(area, type(None)) or area == "":
            return None

        try:
            value = float(value)
            area = float(area)

            value_m2 = round((value / area), 2)

            return value_m2
        except (ValueError, ZeroDivisionError):
            return None
        
    def handle_value_m2(self, value):
        if isinstance(value, type(None)) or value == "":
            return "Não foi possivel realziar o cálculo"
        return value

    def handle_unit_types(self, data):
        if data == "Não informado":
            return "Não informado"
        
        if len(data) == 1:
            return self.translations.get(data[0], data[0])
        
        string = ""
        for value in data:
            value = self.translations.get(value, value)
                
            string = (f'{string}; {value}') if not string == "" else value
        return string

    def business2pt(self, value):
        if value == "SALE":
            return "VENDA"
        if value == "RENTAL":
            return "ALUGUEL"
        return value

    def create_file(self):
        self.geojson_data = self.data2geojson()

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"imoveis_zap_{timestamp}.geojson"

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.geojson_data, file, ensure_ascii=False, indent=4)

