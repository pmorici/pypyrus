"""Helpful functions and classes for packing bits
"""
import struct

class Packer(object):
    """Pack bit fields into a stream of bytes.
    
    >>> import array
    >>> p = Packer(9)
    >>> bit_fields = [256, 45, 258, 258, 65, 259, 66, 257]
    >>> for v in bit_fields: p.pack(v)
    >>> array.array("B", p).tostring().encode('hex')
    '800b6050220c0c8501'
    
    >>> p = Packer(8, out_wbits=9)
    >>> bit_fields = array.array("B", '800b6050220c0c8501'.decode('hex'))
    >>> for v in bit_fields: p.pack(v)
    >>> for v in p: print v,
    256 45 258 258 65 259 66 257
    
    >>> p = Packer(1)
    >>> bit_fields = [1,1,1,1,1,1,1,1,1,1,1,1]
    >>> for v in bit_fields: p.pack(v)
    >>> array.array("B", p).tostring().encode('hex')
    'fff0'
    
    >>> p = Packer(1, out_wbits=2)
    >>> bit_fields = [1,0,1,1,1,1,1,1,1,1,1,1,1,1]
    >>> for v in bit_fields: p.pack(v)
    >>> print p.next(),
    2
    >>> p.set_output_field_width(8)
    >>> array.array("B", p).tostring().encode('hex')
    'fff0'
    
    >>> p = Packer(8, out_wbits=17)
    >>> bit_fields = [255, 255, 255, 255]
    >>> for v in bit_fields: p.pack(v)
    >>> print p.next()
    131071
    >>> p.set_output_field_width(1)
    >>> for b in p: print b, 
    1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
    """
    def __init__(self, in_wbits, out_wbits=8):
        """Initialize a new packer to pack a stream of input fields in_wbits
        wide into a stream of output values out_wbits wide.
        """
        self.default_wbits = in_wbits
        self.fields = []
        self.r = 0
        self.out_wbits = out_wbits
        self.max_wbits = in_wbits
        self.r_wbits = self.out_wbits + self.max_wbits
        self.bit_count = 0
        self._update_masks()
        
    def __iter__(self):
        return self
        
    def __next__(self):
        return self.next()
        
    def next(self):
        if len(self.fields) == 0 and self.bit_count <= 0:
            raise StopIteration()
            
        while(self.bit_count < self.out_wbits and len(self.fields) != 0):
            v, wbits = self.fields.pop(0)
            self.r = self.r | (v << (self.r_wbits - self.bit_count - wbits))
            self.bit_count += wbits
        
        pv = self.r >> self.max_wbits & self.pack_mask
        self.r = (self.r & self.clear_mask) << self.out_wbits
        self.bit_count = max(0, self.bit_count - self.out_wbits)
        return pv
    
    def set_input_field_width(self, in_wbits):
        """Change the default field width"""
        self._update_max_wbits(in_wbits)
        self.defualt_wbits = in_wbits
        
    def set_output_field_width(self, out_wbits):
        """Change the default field width for output values"""
        saved_bits = self.r >> (self.r_wbits - self.bit_count)
        self.out_wbits = out_wbits
        self.max_wbits = max(self.max_wbits, self.bit_count - out_wbits)
        self.r_wbits = self.out_wbits + self.max_wbits
        self.r = saved_bits << (self.r_wbits - self.bit_count)
        self._update_masks()
        
        
    def pack(self, field, wbits=None):
        """Append a bit field to the packed bit stream.  If wbits is given then
        use that as the input bit field width other wise use the default.
        """
        if wbits is None:
            wbits = self.default_wbits
        else:
            self._update_max_wbits(wbits)
        self.fields.append((field, wbits if wbits is not None 
                                   else self.default_wbits))
    
    def _update_masks(self):
        self.pack_mask = 0
        for i in range(self.out_wbits):
            self.pack_mask |= (1 << i)
        self.clear_mask = ~(self.pack_mask << self.max_wbits)
        
    def _update_max_wbits(self, new_max):
        if new_max > self.max_wbits:
            diff = new_max - self.max_wbits
            self.max_wbits = new_max
            self.r << diff
            self.r_wbits = self.out_wbits + self.max_wbits
            self._update_masks()

if __name__ == '__main__':
    pass
            
            
    
