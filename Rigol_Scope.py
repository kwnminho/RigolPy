import visa
import numpy as np
import matplotlib.pyplot as plot
import time
import datetime
rm = visa.ResourceManager()
rm.list_resources()
scope = rm.open_resource('TCPIP0::169.254.1.5::INSTR',read_termination='\n')
print(scope.query('*IDN?'))