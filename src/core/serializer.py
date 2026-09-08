class TelemetrySeralize:
    @staticmethod
    def convert_data(obj):
        ## Checks if its Dictionary
        if isinstance(obj,dict):
            return{
                key:TelemetrySeralize.convert_data(value)
                for key,value in obj.items()
            }
        
        ## Checks if its 'asdict'
        if hasattr(obj,"_asdict"):
            return{
                key:TelemetrySeralize.convert_data(value)
                for key,value in obj._asdict().items()
            }

        ## Checks if its 'list and tuple'
        if isinstance(obj,(list,tuple)):
            return[
                TelemetrySeralize.convert_data(i)
                for i in obj
            ]

        ## Checks if its 'asdict'
        if isinstance(obj,float):
            return round(obj,2)

        else:
            return obj
        
