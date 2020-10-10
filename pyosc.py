from pyo import PyoObject
import pyo
import numpy as np

# Utilities

def normalize(x):
    return x / (x.max() + 0.0001)

def sin_gen(size=2048, order=1, phase=0):
    x = np.linspace(0, (2 * np.pi) * order, size)
    return np.sin(x + (2 * np.pi) * phase)

# Bandlimited generators

def sine_gen(size=2048, order=1):
    return sin_gen(size, 1)

def square_gen(size=2048, order=1):
    harmonics = np.zeros((order, size))
    for i in range(0, order, 2):
        harmonics[i] = (1 / (i + 1)) * sin_gen(size, i + 1)
    return normalize(harmonics.sum(0))

def saw_gen(size=2048, order=1):
    harmonics = np.zeros((order, size))
    for i in range(0, order):
        harmonics[i] = (1 / (i + 1)) * sin_gen(size, i + 1)
    return normalize(harmonics.sum(0))

def tri_gen(size=2048, order=1):
    harmonics = np.zeros((order, size))
    for i in range(0, order, 2):
        if not (((i + 1) % 4) - 3):
            harmonics[i] = sin_gen(size, i + 1, 0.5) / ((i + 1) ** 2)
        else:
            harmonics[i] = sin_gen(size, i + 1, 0) / ((i + 1) ** 2)
    return normalize(harmonics.sum(0))

def tables_gen(wave_gen, size=2048, col_size=100, base_freq=55, max_freq=11025):
    return [list(wave_gen(size=size, order=int(max_freq / (base_freq * ((i * 2) + 1))))) for i in range(0, col_size)]

# Wavetable bandlimited thru zero oscillators

class WSine(PyoObject):
    def __init__(self, freq=440, base_freq=55, samplerate=44100, phase=0, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._freq = freq
        self._phase = phase
        self._base_freq = base_freq
        self._samplerate = samplerate
        self._max_freq = int(samplerate / 4)
        self._table_size = int((self._max_freq / self._base_freq) * 4)
        self._col_size = 1
        #freq,mul,add,lmax = convertArgsToLists(freq,mul,add)
        
        tables = tables_gen(sine_gen, self._table_size, self._col_size, self._base_freq, self._max_freq)
        self._matrix = pyo.NewMatrix(self._table_size, self._col_size, tables)
        self._ramp = pyo.Phasor(freq, phase)
        self._wave = pyo.MatrixPointer(self._matrix, self._ramp, pyo.Sig(0))
        self._base_objs = self._wave.getBaseObjects()
    
    def setFreq(self, x):
        self._freq = x
        self._ramp.freq = x
    
    def setPhase(self, x):
        self._phase = x
        self._ramp.phase = x

    def play(self, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.play(self, dur, delay)
    
    def stop(self, wait=0):
        self._wave.stop(wait)
        return PyoObject.stop(self, wait)
    
    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)
    
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [pyo.SLMap(10, 4000, "log", "freq", self._freq),
                          pyo.SLMap(0, 1, "lin", "phase", self._phase),
                          pyo.SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)
    
    @property
    def freq(self):
        return self._freq
    @freq.setter
    def freq(self, x):
        self.setFreq(x)
    
    @property
    def phase(self):
        return self._phase
    @phase.setter
    def phase(self, x):
        self.setPhase(x)

class WSaw(PyoObject):
    def __init__(self, freq=440, base_freq=55, samplerate=44100, phase=0, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._freq = freq
        self._phase = phase
        self._base_freq = base_freq
        self._samplerate = samplerate
        self._max_freq = int(samplerate / 4)
        self._table_size = int((self._max_freq / self._base_freq) * 4)
        self._col_size = int((self._max_freq / self._base_freq) / 2)
        #freq,mul,add,lmax = convertArgsToLists(freq,mul,add)
        
        tables = tables_gen(saw_gen, self._table_size, self._col_size, self._base_freq, self._max_freq)
        self._matrix = pyo.NewMatrix(self._table_size, self._col_size, tables)
        self._ramp = pyo.Phasor(freq, phase)
        self._table_selector_freq = pyo.Sig(freq)
        self._table_selector = pyo.Min(pyo.Max(((pyo.Abs(self._table_selector_freq) / (self._base_freq * 2)) - 0.5) / self._col_size, 0), (self._col_size - 1) / self._col_size)
        self._wave = pyo.MatrixPointer(self._matrix, self._ramp, self._table_selector)
        self._base_objs = self._wave.getBaseObjects()
    
    def setFreq(self, x):
        self._freq = x
        self._ramp.freq = x
        self._table_selector_freq.value = x
    
    def setPhase(self, x):
        self._phase = x
        self._ramp.phase = x

    def play(self, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.play(self, dur, delay)
    
    def stop(self, wait=0):
        self._wave.stop(wait)
        return PyoObject.stop(self, wait)
    
    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)
    
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [pyo.SLMap(10, 4000, "log", "freq", self._freq),
                          pyo.SLMap(0, 1, "lin", "phase", self._phase),
                          pyo.SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)
    
    @property
    def freq(self):
        return self._freq
    @freq.setter
    def freq(self, x):
        self.setFreq(x)
    
    @property
    def phase(self):
        return self._phase
    @phase.setter
    def phase(self, x):
        self.setPhase(x)

class WSquare(PyoObject):
    def __init__(self, freq=440, base_freq=55, samplerate=44100, phase=0, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._freq = freq
        self._phase = phase
        self._base_freq = base_freq
        self._samplerate = samplerate
        self._max_freq = int(samplerate / 4)
        self._table_size = int((self._max_freq / self._base_freq) * 4)
        self._col_size = int((self._max_freq / self._base_freq) / 2)
        #freq,mul,add,lmax = convertArgsToLists(freq,mul,add)
        
        tables = tables_gen(square_gen, self._table_size, self._col_size, self._base_freq, self._max_freq)
        self._matrix = pyo.NewMatrix(self._table_size, self._col_size, tables)
        self._ramp = pyo.Phasor(freq, phase)
        self._table_selector_freq = pyo.Sig(freq)
        self._table_selector = pyo.Min(pyo.Max(((pyo.Abs(self._table_selector_freq) / (self._base_freq * 2)) - 0.5) / self._col_size, 0), (self._col_size - 1) / self._col_size)
        self._wave = pyo.MatrixPointer(self._matrix, self._ramp, self._table_selector)
        self._base_objs = self._wave.getBaseObjects()
    
    def setFreq(self, x):
        self._freq = x
        self._ramp.freq = x
        self._table_selector_freq.value = x
    
    def setPhase(self, x):
        self._phase = x
        self._ramp.phase = x

    def play(self, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.play(self, dur, delay)
    
    def stop(self, wait=0):
        self._wave.stop(wait)
        return PyoObject.stop(self, wait)
    
    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)
    
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [pyo.SLMap(10, 4000, "log", "freq", self._freq),
                          pyo.SLMap(0, 1, "lin", "phase", self._phase),
                          pyo.SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)
    
    @property
    def freq(self):
        return self._freq
    @freq.setter
    def freq(self, x):
        self.setFreq(x)
    
    @property
    def phase(self):
        return self._phase
    @phase.setter
    def phase(self, x):
        self.setPhase(x)

class WTri(PyoObject):
    def __init__(self, freq=440, base_freq=55, samplerate=44100, phase=0, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._freq = freq
        self._phase = phase
        self._base_freq = base_freq
        self._samplerate = samplerate
        self._max_freq = int(samplerate / 4)
        self._table_size = int((self._max_freq / self._base_freq) * 4)
        self._col_size = int((self._max_freq / self._base_freq) / 2)
        #freq,mul,add,lmax = convertArgsToLists(freq,mul,add)
        
        tables = tables_gen(tri_gen, self._table_size, self._col_size, self._base_freq, self._max_freq)
        self._matrix = pyo.NewMatrix(self._table_size, self._col_size, tables)
        self._ramp = pyo.Phasor(freq, phase)
        self._table_selector_freq = pyo.Sig(freq)
        self._table_selector = pyo.Min(pyo.Max(((pyo.Abs(self._table_selector_freq) / (self._base_freq * 2)) - 0.5) / self._col_size, 0), (self._col_size - 1) / self._col_size)
        self._wave = pyo.MatrixPointer(self._matrix, self._ramp, self._table_selector)
        self._base_objs = self._wave.getBaseObjects()
    
    def setFreq(self, x):
        self._freq = x
        self._ramp.freq = x
        self._table_selector_freq.value = x
    
    def setPhase(self, x):
        self._phase = x
        self._ramp.phase = x

    def play(self, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.play(self, dur, delay)
    
    def stop(self, wait=0):
        self._wave.stop(wait)
        return PyoObject.stop(self, wait)
    
    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._wave.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)
    
    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [pyo.SLMap(10, 4000, "log", "freq", self._freq),
                          pyo.SLMap(0, 1, "lin", "phase", self._phase),
                          pyo.SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)
    
    @property
    def freq(self):
        return self._freq
    @freq.setter
    def freq(self, x):
        self.setFreq(x)
    
    @property
    def phase(self):
        return self._phase
    @phase.setter
    def phase(self, x):
        self.setPhase(x)