"""

"""


import sys
import struct


def read_time(b, i):
  
  x = 0x80
  y = 1
  t = 0
  while (x&0x80) != 0:
    x = b[i]
    i += 1
    t += (0x7F&x)*y
    y *= 128
    
  return t, i




def process_phr_trak(b):
  
  i = 0
  time = 0

  note_count = 0
  
  
  while True:
  
    t_delta, i = read_time(b, i)
    time += t_delta
    
    note = b[i]
    i += 1
    
    if note == 0x80:
      if b[i] != 0x01:
        raise Exception("Expected a 01 here")
      # End of data
      break
    elif note > 0x80:
      ev_len = 3
      if note == 0x84:
        # Set patch/bank
        bank = struct.unpack('>H', b[i+4:i+6])[0]
        patch = b[i+6]
        bank_msb = bank//128
        ev_len = 5
      elif note == 0x89:
        # Sustain pedal. 01 00 00 = released, 01 00 FF = pressed.
        pass
      elif note == 0x97:
        # Sustain button. 01 00 80 = released, 01 00 E0 = pressed.
        pass
      elif note == 0x8B:
        # Soft pedal
        pass
      elif note == 0x92:
        # Pitch bend
        pitch_bend = struct.unpack('>H', b[i+4:i+6])[0]
        ev_len = 4
      elif note == 0x8A:
        # Sostenuto pedal. 01 00 00 = released, 01 00 FE = pressed.
        pass
      elif note == 0x95:
        #Portamento (time/onoff?)
        pass
      elif note == 0x94:
        #Portamento (time/onoff?)
        pass
      elif note == 0x8D:
        # unknown?
        ev_len = 4
      elif note == 0x87:
        # unknown
        pass
      elif note == 0x88:
        # unknown
        pass
      elif note == 0x91:
        # unknown
        pass
      elif note == 0x8E:
        # unknown
        pass
      elif note == 0x8F:
        # unknown
        pass
      elif note == 0x90:
        # unknown
        pass
      elif note == 0x92:
        # unknown
        pass
      elif note == 0x93:
        # Pitch bend range. 01 00 xx .
        pass
      elif note == 0x94:
        # unknown
        pass
      elif note == 0x95:
        # unknown
        pass
      elif note == 0x96:
        # unknown
        pass
      elif note == 0x97:
        # unknown
        pass
      elif note == 0x98:
        # unknown
        pass
      elif note == 0x99:
        # unknown
        pass
      elif note == 0x82:
        # unknown
        pass
      else:
        print("{0:02X} {1:02X} {2:02X} {3:02X} {4:02X} {5:02X} {6:02X} {7:02X} {8:02X} {9:02X}".format(b[i-4], b[i-3], b[i-2], b[i-1], b[i], b[i+1], b[i+2], b[i+3], b[i+4], b[i+5]))
        raise Exception("Unknown event type {0:02X}".format(note))
        
      i += ev_len
    elif note == 0:
      raise Exception("Should not have a 00 here")
    else:
    
      if b[i] != 0x00 and b[i] != 0x85:
        print("{0:02X} {1:02X} {2:02X} {3:02X} {4:02X} {5:02X} {6:02X} {7:02X} {8:02X} {9:02X}".format(b[i-4], b[i-3], b[i-2], b[i-1], b[i], b[i+1], b[i+2], b[i+3], b[i+4], b[i+5]))
        print("NOTE = {0:02X}".format(note))
        raise Exception("Expect either a 00 or a 85 here")
      i += 1
      
      velocity = b[i]
      i += 1
      
      duration = 256*(0x7F&b[i]) + 1*(0xFF&b[i+1])
      i += 2
      
      note_count += 1


    
  print("TOTAL TIME = {0}".format(time))
  print("NUMBER OF NOTES = {0}".format(note_count))




def process_phr(b):
  #Process the CPFF wrapper of a phrase definition
  #
  if b[0:4] != b'CPFF':
    raise Exception("Expecting CPFF")
  j = 8 + struct.unpack('<I', b[4:8])[0] # Jump forward length of the header portion
  
  if b[j:j+4] != b'TRAK':
    raise Exception("Expecting TRAK")
    
  j += 8
  
  k = struct.unpack('<I', b[j:j+4])[0] # Length of actual data
  if j + k > len(b):
    raise Exception("Corrupt CPFF")
  
  j += 4
  
  return process_phr_trak(b[j:j+k])



if __name__=="__main__":
  if len(sys.argv) >= 2:
    with open(sys.argv[1], 'rb') as f:
      b = f.read()
    process_phr(b)

