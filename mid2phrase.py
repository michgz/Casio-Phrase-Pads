"""

"""


import sys
import struct
import binascii
from internal.midifiles import midifile_read


def process_mid(b):
  return b''



def combine_to_phrase_set(d):
  # Takes multiple (up to 4) phrases and combines them into the format of a .PHS
  # file
  
  if len(d) > 4:
    raise Exception("Limit of 4 phrases per set; given {0}".format(len(d)))
  
  e = b'CT-X3000\x00\x00\x00\x00\x00\x00\x00\x00'
  e += b'PHSH' + struct.pack('<I', 0)
  
  for i in range(4):
    if i < len(d):
      b = d[i]
    else:
      b = b''
      
    e += b'PHRH' + struct.pack('<3I', 0, binascii.crc32(b), len(b)) + b + b'EODA'
    
  return e  




if __name__=="__main__":
  if len(sys.argv) >= 2:
    with open(sys.argv[1], 'rb') as f:
      b = f.read()
    # Extracts the data from a .MID file, then writes the resulting Phrase Set
    # data to standard output
    m = midifile_read(b)
    p = process_mid(m)
    sys.stdout.buffer.write(combine_to_phrase_set([p]))

