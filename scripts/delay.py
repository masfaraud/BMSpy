from bms.blocks import Delay
from bms.core import DynamicSystem
from bms.signals.functions import Ramp
from bms.core import Variable


""" test that we can delay a signal by 2 seconds
Output samples corresponding to time < 2 seconds should be all np.nan
There is a bug somewhere and first sample is set to 0 (i'm not testing first sample)
"""
delay = 2.3   # time
end_time = 10
time_step = 200
input_ = Ramp()
output_ = Variable(('output', 'o'))
delay = Delay(input_, output_, delay)
ds = DynamicSystem(end_time, time_step, blocks=[delay])
ds.Simulate()
ds.PlotVariables()