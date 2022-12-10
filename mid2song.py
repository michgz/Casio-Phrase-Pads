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
  f += b'\x00\x82\x01\x04\x04\x00\x83\x01\x3C\x00\x00\xCB'
  f += b'\x01\x00\x17\x00\xD1\x01\x00\x10\x00\xDA\x01\x00\x14\x00\xB2\x01'
  f += b'\x6E\x00\xA5\x02\x00\x00\xA7\x02\x00\x00\xA6\x02\x00\x00\xB3\x01'
  f += b'\xFF\x00\xAB\x02\x00\x00\x84\x01\x00\x00\x80\x00\x00\x93\x01\x00'
  f += b'\x02\x00\x8C\x01\x00\x80\x00\x8D\x01\x00\x80\x00\x00\x94\x01\x00'
  f += b'\x00\x00\x95\x01\x00\x00\x00\x97\x01\x00\x80\x00\xAC\x02\x00\x01'
  f += b'\x00\x91\x01\x00\xFE\x00\x87\x01\x00\x80\x00\x8E\x01\x00\x3C\x00'
  f += b'\x8F\x01\x00\x00\x00\x90\x01\x00\x00\x00\x84\x01\x01\x00\x80\x31'
  f += b'\x00\x93\x01\x01\x02\x00\x8C\x01\x01\x80\x00\x8D\x01\x01\x80\x00'
  f += b'\x00\x94\x01\x01\x00\x00\x95\x01\x01\x00\x00\x97\x01\x01\x80\x00'
  f += b'\xAC\x02\x01\x01\x00\x91\x01\x01\xFE\x00\x87\x01\x01\x80\x00\x8E'
  f += b'\x01\x01\x48\x00\x8F\x01\x01\x00\x00\x90\x01\x01\x00\x00\x84\x01'
  f += b'\x02\x00\x80\x20\x00\x93\x01\x02\x02\x00\x8C\x01\x02\x80\x00\x8D'
  f += b'\x01\x02\x80\x00\x00\x94\x01\x02\x00\x00\x95\x01\x02\x00\x00\x97'
  f += b'\x01\x02\x80\x00\xAC\x02\x02\x01\x00\x91\x01\x02\xFE\x00\x87\x01'
  f += b'\x02\x80\x00\x8E\x01\x02\x0E\x00\x8F\x01\x02\x00\x00\x90\x01\x02'
  f += b'\x00\x00\x84\x01\x03\x00\x80\x32\x00\x93\x01\x03\x02\x00\x8C\x01'
  f += b'\x03\x80\x00\x8D\x01\x03\x80\x00\x00\x94\x01\x03\x00\x00\x95\x01'
  f += b'\x03\x00\x00\x97\x01\x03\x80\x00\xAC\x02\x03\x01\x00\x91\x01\x03'
  f += b'\xFE\x00\x87\x01\x03\x80\x00\x8E\x01\x03\x40\x00\x8F\x01\x03\x90'
  f += b'\x00\x90\x01\x03\x00\x00\x84\x01\x04\x00\x00\x00\x00\x93\x01\x04'
  f += b'\x02\x00\x8C\x01\x04\x80\x00\x8D\x01\x04\x80\x00\x00\x94\x01\x04'
  f += b'\x00\x00\x95\x01\x04\x00\x00\x97\x01\x04\x80\x00\xAC\x02\x04\x01'
  f += b'\x00\x91\x01\x04\xC8\x00\x87\x01\x04\x80\x00\x8E\x01\x04\x50\x00'
  f += b'\x8F\x01\x04\x00\x00\x90\x01\x04\x00\x00\xAC\x02\x1D\x01\x00\x91'
  f += b'\x01\x1D\x96\x00\x87\x01\x1D\x80\x00\x8E\x01\x1D\xA0\x00\x8F\x01'
  f += b'\x1D\x00\x00\x90\x01\x1D\x00\x00\xAC\x02\x1E\x01\x00\x91\x01\x1E'
  f += b'\x64\x00\x87\x01\x1E\x80\x00\x8E\x01\x1E\x3C\x00\x8F\x01\x1E\xFE'
  f += b'\x00\x90\x01\x1E\x00\x00\xAC\x02\x1F\x01\x00\x91\x01\x1F\xF0\x00'
  f += b'\x87\x01\x1F\x80\x00\x8E\x01\x1F\x00\x00\x8F\x01\x1F\x00\x00\x90'
  f += b'\x01\x1F\x00\x00\xAC\x02\x20\x01\x00\x91\x01\x20\xB4'


  # Set up the Rhythm as "001 E DANCE POP"
  f += b'\x00\x87\x01\x20\x80'
  f += b'\x00\x8E\x01\x20\x64'
  f += b'\x00\x8F\x01\x20\x28'
  f += b'\x00\x90\x01\x20\x00'
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

