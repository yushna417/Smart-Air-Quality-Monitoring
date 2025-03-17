from machine import ADC, Pin

#MQ135 sensor class
class MQ135:
    def __init__(self, adc_pin, rload=10.0, ro_clean_air=3.6):
        self.adc = ADC(Pin(adc_pin))
        self.adc.width(ADC.WIDTH_12BIT)  
        self.adc.atten(ADC.ATTN_11DB)    

        self.RLOAD = rload
        self.RO_CLEAN_AIR = ro_clean_air

        self.GAS_CURVES = {
            "CO2": lambda rs_ro: (1 / rs_ro) * 500,    
            "CO": lambda rs_ro: (1 / rs_ro) * 100,     
            "NH3": lambda rs_ro: (1 / rs_ro) * 300,    
            "NOx": lambda rs_ro: (1 / rs_ro) * 50,     
            "Benzene": lambda rs_ro: (1 / rs_ro) * 10,
        }
    
    def read_sensor(self):
        """Reads the analog value from the MQ-135 sensor."""
        return self.adc.read()
    
    def calculate_rs(self, analog_value):
        """Calculates the sensor resistance (RS) from the analog value."""
        voltage = analog_value * (3.3 / 4095)  
        return self.RLOAD * ((3.3 - voltage) / voltage)
    
    def get_gas_concentration(self, gas, rs):
        """Calculates a specific gas concentration based on RS."""
        if gas not in self.GAS_CURVES:
            raise ValueError(f"Gas {gas} not supported")
        rs_ro = rs / self.RO_CLEAN_AIR  
        return self.GAS_CURVES[gas](rs_ro)
