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
  
  f += event(0x81, 0, '            '.encode('ascii'))
  
  
  # Set up each of the "Song System" parts
  
  
  
  f += event(0x82, 0, struct.pack('BB', 4, 4))
  f += event(0x83, 0, struct.pack('BB', 0x3c, 0))
  f += event(0xCB, 0, struct.pack('BB', 0, 23))
  f += event(0xD1, 0, struct.pack('BB', 0, 16))
  f += event(0xDA, 0, struct.pack('BB', 0, 20))
  f += event(0xB2, 0, struct.pack('B', 0x6e))

  f += struct.pack('4B', 0, 0xA5, 2, 0)
  f += struct.pack('4B', 0, 0xA7, 2, 0)
  f += struct.pack('4B', 0, 0xA6, 2, 0)
  f += struct.pack('4B', 0, 0xB3, 1, 255)
  f += struct.pack('4B', 0, 0xAB, 2, 0)



  CHANNELS = [{'N': 0, 'BankPatch': (1,  0), 'Vol': 127, 'Pan': 0, 'Rev': 30, 'Cho': 0, 'Del': 0},
              {'N': 1, 'BankPatch': (1, 49), 'Vol': 127, 'Pan': 0, 'Rev': 36, 'Cho': 0, 'Del': 0},
              {'N': 2, 'BankPatch': (1, 32), 'Vol': 127, 'Pan': 0, 'Rev': 7, 'Cho': 0, 'Del': 0},
              {'N': 3, 'BankPatch': (1, 50), 'Vol': 127, 'Pan': 0, 'Rev': 32, 'Cho': 72, 'Del': 0},
              {'N': 4, 'BankPatch': (0,  0), 'Vol': 100, 'Pan': 0, 'Rev': 40, 'Cho': 0, 'Del': 0},
              {'N': 0x1D,                    'Vol': 75, 'Pan': 0, 'Rev': 0x50, 'Cho': 0, 'Del': 0},
              {'N': 0x1E,                    'Vol': 50, 'Pan': 0, 'Rev': 0x1e, 'Cho': 0x7f, 'Del': 0},
              {'N': 0x1F,                    'Vol': 120, 'Pan': 0, 'Rev': 0, 'Cho': 0, 'Del': 0},
              {'N': 0x20,                    'Vol': 90, 'Pan': 0, 'Rev': 50, 'Cho': 20, 'Del': 0}]


  for CC in CHANNELS:

      if CC['N'] < 16:
          f += struct.pack('>BBBBHB', 0, 0x84, 1, CC['N'], 0x80*CC['BankPatch'][0], CC['BankPatch'][1])
          f += struct.pack('5B', 0, 0x93, 1, CC['N'], 2)
          f += struct.pack('5B', 0, 0x8C, 1, CC['N'], 0x80)
          f += struct.pack('6B', 0, 0x8D, 1, CC['N'], 0x80, 0)
          f += struct.pack('5B', 0, 0x94, 1, CC['N'], 0)
          f += struct.pack('5B', 0, 0x95, 1, CC['N'], 0)
          f += struct.pack('5B', 0, 0x97, 1, CC['N'], 0x80)
      f += struct.pack('5B', 0, 0xAC, 2, CC['N'], 1)
      f += struct.pack('5B', 0, 0x91, 1, CC['N'], 2*CC['Vol'])
      f += struct.pack('5B', 0, 0x87, 1, CC['N'], 2*(64+CC['Pan']))
      f += struct.pack('5B', 0, 0x8E, 1, CC['N'], 2*CC['Rev'])
      f += struct.pack('5B', 0, 0x8F, 1, CC['N'], 2*CC['Cho'])
      f += struct.pack('5B', 0, 0x90, 1, CC['N'], 2*CC['Del'])



  # Set up the Rhythm as "001 E DANCE POP"

  f += b'\x00\xAF\x01\x04\x1F'
  f += b'\x00\xB0\x01\x02\x00'
  
  

  if False:
    
    # This creates a song which plays each of the chord types in turn. Was used
    # for doing experiments into rhythms, is not really useful for anything else.
    
    time = 0
    
    # Step through each chord type.
    for i in range(37):   
    
      time_d = 768
      f += event(0xAE, encode_time(time_d), b'\x02' + struct.pack('B', i) + struct.pack('3B', 15, 0, 0x74))
      time += time_d
    
    
    time_d = 768
    f += event(0xB0, encode_time(time_d), b'\x00\x00')
    time += time_d
    
    last_time_int = time
    
    f += event(0x80, 0, b'')  # End of track
    
    
  else:
  
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

    if len(c)==0:
      last_time_int = 4*24
    else:
      last_time = max(evt['absolute_time'] for evt in c)
      # Round up to nearest bar. Phrases can only be in 4/4 time, so don't need to
      # worry too much.
    
      last_time_int = ceil(float(last_time)/(4.0*24.0)) * (4*24)
    
    # Finish off
    f += encode_time(round((last_time_int - latest_absolute_time)*4.0)) + b'\x80\x01'

  
  e = b'TRAK'
  e += struct.pack('<I', 4*last_time_int)
  e += struct.pack('<I', len(f))
  e += f
  
  return e


def empty_track():
  # Returns an empty track
  x = b'\x00\x80\x01'  # "End of Track"
  return b'TRAK' + struct.pack('<2I', 0, len(x)) + x


def combine_to_song(b):
  # Takes a Song and wraps it into the format of a .MRF file

  e = b'CT-X3000\x00\x00\x00\x00\x00\x00\x00\x00'
  e += b'MRFH' + struct.pack('<3I', 1, binascii.crc32(b), len(b)) + b + b'EODA'
    
  return e  


def combine_tracks_to_song(d):
  # Combines multiple (up to 17) tracks into a Song format. Each track should already
  # commence with the "TRAK" designator.
  
  h = b'\x03\x04\x00\x01\x05'
  h += '            '.encode('ascii')  # Name
  h += b'\x06\x11\x09\x00\x0a\x03\x0b\x03\x0c\x00\x0f\x00\x00\x10\x00\x00'   # Don't know what any of this stuff is!
  
  e = b'CMFF' + struct.pack('<I', len(h)) + h
  for i in range(17):
    try:
      b = d[i]
    except IndexError:
      b = b''
    if len(b) < 4 or b[0:4] != b'TRAK':
      # not a track. Substitute an empty track
      b = empty_track()
    e += b
  return e


def process_midi(b):
  # Takes the contents of a standard MIDI file as input. Returns a song as output.
  if b == b'':
    m = [b'', b'']
  else:
    m = midifile_read(b)
  p = process_mid(m[1])
  return combine_tracks_to_song([p])



if __name__=="__main__":
  if len(sys.argv) >= 2:
    with open(sys.argv[1], 'rb') as f:
      b = f.read()
      # Extracts the data from a .MID file, then writes the resulting Song
      # data to standard output
      m = midifile_read(b)
  else:
      m = [b'', b'']

  p = process_mid(m[1])
  sys.stdout.buffer.write(combine_to_song(p))

