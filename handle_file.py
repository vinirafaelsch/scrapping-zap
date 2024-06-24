class HandleFile:
    def __init__(self, data):
        self.extracted_data: list = data
        self.geojson_data: dict = self.create_geojson()

    def create_geojson(self):
        geojson = {
            "type": "FeatureCollection",
            "name": "Modelo_Arquivo_ExtraçãoZAP_recorte",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features": []
        }
        
        return geojson

    def data2geojson(self):
        print(self.extracted_data)