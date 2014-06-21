"""Filters

Defined in ISO 32000-1:2008 7.4
"""
from array import array
from collections import defaultdict
import itertools
import struct
import zlib

import charset
import bits

def ascii_hex_encode(s):
    """Return s encoded in hex and terminated with a '>'.

    >>> ascii_hex_encode('abc')
    '616263>'
    """
    return s.encode('hex') + '>'

def ascii_hex_decode(s):
    """Return the hex decoded representation of s.

    >>> ascii_hex_decode('616263>')
    'abc'
    >>> ascii_hex_decode('61 62 7>')
    'abp'
    >>> ascii_hex_decode('61\\n626\\n3>')
    'abc'
    """
    s = s.strip().rstrip('>')
    s = s.translate(None, charset.WHITESPACE)
    if len(s) % 2 is not 0:
        s += '0'
    return s.decode('hex')

def ascii85_encode(s):
    """Return s encoded in ascii85 and terminated by the sequence '~>'
    see also: http://en.wikipedia.org/wiki/Ascii85#Adobe_version

    >>> ascii85_encode('Man sure')
    '9jqo^F*2M7~>'
    >>> ascii85_encode('Man s')
    '9jqo^Er~>'
    >>> ascii85_encode('\\x00\\x00\\x00\\x00')
    'z~>'
    >>> ascii85_encode('Man \\x00\\x00')
    '9jqo^!!!~>'
    >>> ascii85_encode('')
    '~>'
    """
    ascii85 = []
    padding = (4 - len(s) % 4) % 4
    # pad with 0x00 bytes to multiple of 4
    s += '\x00' * padding
    # split into a list of 4 char strings
    s = [''.join(l) for l in zip(*(iter(s),) * 4)]
    for grp in s:
        value = struct.unpack('>I', grp)[0]
        if value is 0:
            ascii85.append('z')
            continue
        for i in range(4, -1, -1):
            ascii85.append(chr(value / pow(85, i) + 33))
            value %= pow(85, i)

    if padding > 0 and ascii85[-1:][0] == 'z':
        ascii85 = ascii85[:-1] + ['!'] * 5
    return ''.join(ascii85[:len(ascii85)-padding]) + '~>'

def ascii85_decode(s):
    """Decode the ascii85 encoded input s and return it's decoded value
    see also: http://en.wikipedia.org/wiki/Ascii85#Adobe_version

    >>> ascii85_decode('9jqo^F*2M7~>')
    'Man sure'
    >>> ascii85_decode('9jqo^Er~>')
    'Man s'
    >>> ascii85_decode('z~>')
    '\\x00\\x00\\x00\\x00'
    >>> ascii85_decode('9jqo^!!!~>')
    'Man \\x00\\x00'
    >>> ascii85_decode('~>')
    ''
    """
    plain = []
    s = s.strip()
    if not s.endswith('~>'):
        raise ValueError("ascii85 is not terminated by '~>'")
    else:
        s = s[:-2]
    s = s.replace('z', '!!!!!')
    padding = (5 - len(s) % 5) % 5
    # pad to multiple of 5 with 'u'
    s += 'u' * padding
    # split into list of 5 char strings
    s = list(zip(*(iter(s),) * 5))
    for grp in s:
        value = 0
        for i, c in zip(range(4, -1, -1), grp):
            value += (ord(c)-33) * pow(85, i)
        if value > pow(2,32)-1 or value < 0:
            raise ValueError('invalid ascii85 input')
        plain.append(struct.pack('>I', value))
    plain = ''.join(plain)
    return plain[:len(plain)-padding]

class LZW(object):
    CLEAR_TABLE = 256
    EOD = 257
    
    @staticmethod
    def default_table():
        return defaultdict(itertools.count(258).next, 
                           ((struct.pack("B", i), i) for i in range(255)))
    
def lzw_encode(s):
    """Encode input into LZW compressed output
    
    >>> uncompressed = array("B", [45,45,45,45,45,65,45,45,45,66]).tostring()
    >>> lzw_encode(uncompressed).encode('hex')
    '800b6050220c0c8501'
    """
    lzw_table = LZW.default_table()
    codes = bits.Packer(9)
    codes.pack(LZW.CLEAR_TABLE)
    
    seq = ""
    for v in s:
        _seq = seq + v
        if _seq in lzw_table:
            seq = _seq
        else:
            codes.pack(lzw_table[seq])
            # TODO: how do we reset the table? 
            codes.set_input_field_width(lzw_table[_seq].bit_length())
            seq = v
            
    if seq != "":
        codes.pack(lzw_table[seq])
    codes.pack(LZW.EOD)
        
    return array("B", codes).tostring()
    

def lzw_decode(s):
    raise NotImplementedError

def flate_encode(s):
    """Encode input s and return flate aka: zlib encoded data
    """
    return zlib.compress(s)

def flate_decode(s):
    """Decode s using flate / zlib
    """
    return zlib.decompress(s)

def run_length_encode(s):
    raise NotImplementedError

def run_length_decode(s):
    raise NotImplementedError

def ccitt_fax_encode(s):
    raise NotImplementedError

def ccitt_fax_decode(s):
    raise NotImplementedError

def jbig2_encode(s):
    raise NotImplementedError

def jbig2_decode(s):
    raise NotImplementedError

def dct_encode(s):
    raise NotImplementedError

def dct_decode(s):
    raise NotImplementedError

def jpx_encode(s):
    raise NotImplementedError

def jpx_decode(s):
    raise NotImplementedError

def crypt_encode(s):
    raise NotImplementedError

def crypt_decode(s):
    raise NotImplementedError

if __name__ == '__main__':
    pass
