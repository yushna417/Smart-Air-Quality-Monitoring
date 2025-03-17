from machine import ADC, Pin

class MQ135:
    def __init__(self, adc_pin, rload=10.0, ro_clean_air=3.6):
        self.adc = ADC(Pin(adc_pin))
        self.adc.width(ADC.WIDTH_12BIT)  
        self.adc.atten(ADC.ATTN_11DB)    
        
        self.RLOAD = rload  
        self.RO_CLEAN_AIR = ro_clean_air  

        # Define gas concentration curves
        self.GAS_CURVES = {
            "CO2": lambda rs_ro: (1 / rs_ro) * 500,    # for CO2
            "CO": lambda rs_ro: (1 / rs_ro) * 100,     # for CO
            "NH3": lambda rs_ro: (1 / rs_ro) * 300,    # for NH3
            "NOx": lambda rs_ro: (1 / rs_ro) * 50,     # for NOx
            "Benzene": lambda rs_ro: (1 / rs_ro) * 10,  # for Benzene
        }
    
    def read_sensor(self):
        """Reads the analog value from the MQ-135 sensor."""
        analog_value = self.adc.read()
        return analog_value
    
    def calculate_rs(self, analog_value):
        """Calculates the sensor resistance (RS) from the analog value."""
        voltage = analog_value * (3.3 / 4095)  
        rs = self.RLOAD * ((3.3 - voltage) / voltage)  
        return rs
    
    def get_gas_concentration(self, gas, rs):
        """Calculates a specific gas concentration based on RS."""
        if gas not in self.GAS_CURVES:
            raise ValueError(f"Gas {gas} not supported")
        rs_ro = rs / self.RO_CLEAN_AIR  
        return self.GAS_CURVES[gas](rs_ro)

# Example usage
def read_co(adc_pin):
    mq135 = MQ135(adc_pin)
    analog_value = mq135.read_sensor()
    rs = mq135.calculate_rs(analog_value)
    return mq135.get_gas_concentration("CO", rs)

def read_co2(adc_pin):
    mq135 = MQ135(adc_pin)
    analog_value = mq135.read_sensor()
    rs = mq135.calculate_rs(analog_value)
    return mq135.get_gas_concentration("CO2", rs)

def read_nh3(adc_pin):
    mq135 = MQ135(adc_pin)
    analog_value = mq135.read_sensor()
    rs = mq135.calculate_rs(analog_value)
    return mq135.get_gas_concentration("NH3", rs)

def read_nox(adc_pin):
    mq135 = MQ135(adc_pin)
    analog_value = mq135.read_sensor()
    rs = mq135.calculate_rs(analog_value)
    return mq135.get_gas_concentration("NOx", rs)

def read_benzene(adc_pin):
    mq135 = MQ135(adc_pin)
    analog_value = mq135.read_sensor()
    rs = mq135.calculate_rs(analog_value)
    return mq135.get_gas_concentration("Benzene", rs)
