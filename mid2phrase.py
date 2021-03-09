"""

"""


import sys
import struct
import binascii
from internal.midifiles import midifile_read


# 1 = as recorded by the CT-X keyboard as user phrases
# 2 = as used in the preset phrases
# It's not yet clear why there are two different formats
FORMAT_SPEC = 1



def event(event_type, time, data):
  if type(time) is int:
    time = struct.pack('B', time)
  return time + struct.pack('B', event_type) + (b'' if event_type < 0x80 else b'\x01') + data

def encode_duration(z):
  if FORMAT_SPEC == 2:
    if z >= 128:
      raise Exception("Duration too long for format spec 2")
    return struct.pack('B', z)
  else:
    return struct.pack('>H', 0x8000 + z)

def encode_time(z):
  # Similar to MIDI time encoding, but with bytes in opposite order.
  if z<0x80:
    return struct.pack('B', z)
  elif z<0x4000:
    return struct.pack('2B', 128+(z%128), z//128)
  else:
    raise Exception("Time out of range")

def ceil(x):
  return -((-x)//1)
 
def process_mid(c):
  
  f = b''
  
  # Start off with some boilerplate. Most of these event are not yet identified.
  # To be refined later.
  
  # Set to GM PIANO 1
  bank = 0
  patch = 0
  f += event(0x84, 0, b'\x00' + struct.pack('>H', 128*bank) + struct.pack('B', patch))  # patch/bank
  f += event(0x91, 0, b'\x00' + struct.pack('B', 255)) # Volume/expression. Values 0-255
  f += event(0x87, 0, b'\x00' + struct.pack('B', 128)) # Pan. Values 0-255.
  f += event(0x8E, 0, b'\x00' + struct.pack('B', 0))   # Reverb send
  f += event(0x8F, 0, b'\x00' + struct.pack('B', 0))   # Chorus send
  f += event(0x90, 0, b'\x00' + struct.pack('B', 0))   # Delay send
  f += event(0x93, 0, b'\x00\x02')  # pitch bend range
  f += event(0x94, 0, b'\x00' + struct.pack('B', 0))  # Portamento
  f += event(0x95, 0, b'\x00' + struct.pack('B', 0))  # Portamento
  f += event(0x97, 0, b'\x00' + struct.pack('B', 128))  # Release time. Values 0-255, 2x those used in keyboard GUI?
  
  
  # Some other values tried with Bank 34 Patch 96 ("EDM THEME SYNTH 2"):
  # 0x92 - v. strange effect!
  # 0x96 - whistling sound
  # 0x98 - whirling sound
  # 0x99 - filter (default 0x80)
  # 0x9A - filter (default 0x80)
  #  .. etc
  # 0x83 - tempo (bpm)
  

  
  latest_absolute_time = 0.
  
  
  for i, evt in enumerate(c):
    
    time = round((evt['absolute_time'] - latest_absolute_time)*4.0)
    evt_to_add = b''
    
    if evt['event'] == 'note_on':
      # To find duration, we need to match this NoteOn with a NoteOff following.
      duration = 0
      for j in range(i+1, len(c)):
        if c[j]['event'] == 'note_off' and c[j]['note'] == evt['note']:
          duration = round((c[j]['absolute_time'] - evt['absolute_time'])*4.0)
          break
      if duration > 0:
        if FORMAT_SPEC == 2:
          evt_to_add = event(evt['note'], encode_time(time), struct.pack('2B', 0x85, evt['velocity']) + encode_duration(duration)) + struct.pack('B', 0x40)
        else:
          evt_to_add = event(evt['note'], encode_time(time), struct.pack('2B', 0, evt['velocity']) + encode_duration(duration))
      else:
        # Not found a NoteOff event. Not sure what's gone wrong? For now just ignore
        pass
    elif evt['event'] == 'pitch_bend':
      pass
    elif evt['event'] == 'control_change':
      if evt['controller'] == 0x40:
        # Sustain pedal
        evt_to_add = event(0x89, encode_time(time), struct.pack('2B', 0, evt['value']))
      elif evt['controller'] == 0x43:
        # Soft pedal
        evt_to_add = event(0x8B, encode_time(time), b'\x00\xE0' if evt['value'] >= 0x80 else b'\x00\x80')
      elif evt['controller'] == 0x43:
        # Sostenuto pedal
        evt_to_add = event(0x8A, encode_time(time), struct.pack('2B', 0, max(0xFE, evt['value'])))
        
    if evt_to_add != b'':
      # Only update the time if there's something to add
      f += evt_to_add
      latest_absolute_time = evt['absolute_time']
  
  last_time = max(evt['absolute_time'] for evt in c)
  # Round up to nearest bar. Phrases can only be in 4/4 time, so don't need to
  # worry too much.
  
  last_time_int = ceil(float(last_time)/(4.0*24.0)) * (4*24)
  
  # Finish off
  f += encode_time(round((last_time_int - latest_absolute_time)*4.0)) + b'\x80\x01'

  
  e = b'CPFF'
  e += struct.pack('<I', 17)   # Length of the "header" portion
  e += b'\x04\x00\x01\x05'   # Not sure what this is?
  e += '            '.encode('ascii')   # Name -- for now, leave empty
  e += b'\x00'   # Possibly null-terminator for the name
  e += b'TRAK'
  #e += b'\x00\x03\x00\x00'
  e += b'\x80\x01\x00\x00'
  e += struct.pack('<I', len(f))
  e += f
  
  return e




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



def process_midi(b):
  # Takes the contents of a standard MIDI file as input. Returns a list of
  # phrase data as output.
  m = midifile_read(b)
  p = process_mid(m[1])
  return [p]




if __name__=="__main__":
  if len(sys.argv) >= 2:
    with open(sys.argv[1], 'rb') as f:
      b = f.read()
    # Extracts the data from a .MID file, then writes the resulting Phrase Set
    # data to standard output
    m = midifile_read(b)
    p = process_mid(m[1])
    sys.stdout.buffer.write(combine_to_phrase_set([p]))

