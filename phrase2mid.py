"""

"""


import sys
import struct
import binascii

from midiutil import MIDIFile



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


def time_adj(x):
  # Translate from Casio timing (96 ticks per crotchet) to midiutils timing (1.0
  # ticks per crotchet)
  return float(x)/96.0



def process_phr_trak(b, m, track=0, channel=4):
  
  # Interprets b as a phrase, and writes the related MIDI data to a track of the
  # MIDIFile m.
  
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
        bank = struct.unpack('>H', b[i+2:i+4])[0]
        patch = b[i+4]
        bank_msb = bank//128
        bank_lsb = 0   # Or bank%128
        m.addControllerEvent(track, channel, time_adj(time), 0x00, bank_msb)
        m.addControllerEvent(track, channel, time_adj(time), 0x20, bank_lsb)
        m.addProgramChange(track, channel, time_adj(time), patch)
        ev_len = 5
      elif note == 0x89:
        # Sustain pedal. 01 00 00 = released, 01 00 FF = pressed.
        x = b[i+2]
        m.addControllerEvent(track, channel, time_adj(time), 0x40, x)
      elif note == 0x97:
        # Sustain button. 01 00 80 = released, 01 00 E0 = pressed.
        x = 0
        if b[i+2] > 0x80:
          x = 0xFF
        m.addControllerEvent(track, channel, time_adj(time), 0x40, x)
      elif note == 0x8B:
        # Soft pedal
        x = b[i+2]
        m.addControllerEvent(track, channel, time_adj(time), 0x43, x)
      elif note == 0x92:
        # Pitch bend. 0x8000 is "no bend", 0xFFFC is maximum upwards bend.
        pitch_bend = struct.unpack('>H', b[i+4:i+6])[0]
        m.addPitchWheelEvent(track, channel, time_adj(time), (pitch_bend - 0x8000)//4)
        ev_len = 4
      elif note == 0x8A:
        # Sostenuto pedal. 01 00 00 = released, 01 00 FE = pressed.
        x = b[i+2]
        if b[i+2] >= 0xFE:
          x = 0xFF
        m.addControllerEvent(track, channel, time_adj(time), 0x42, x)
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
        m.makeRPNCall(track, channel, time_adj(time), 0x00, 0x00, b[i+2], 0)
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
      
      m.addNote(track, channel, note, time_adj(time), duration, velocity)
      
      note_count += 1


    
  #print("TOTAL TIME = {0}".format(time))
  #print("NUMBER OF NOTES = {0}".format(note_count))
  
  
  return m



def process_phr(b):
  #Process the CPFF wrapper of a phrase definition
  #
  if b[0:4] != b'CPFF':
    raise Exception("Expecting CPFF")
    
  trk_name = b[0xC:0x18].decode('ascii')
  trk_count = 1
  
  j = 8 + struct.unpack('<I', b[4:8])[0] # Jump forward length of the header portion
  
  if b[j:j+4] != b'TRAK':
    raise Exception("Expecting TRAK")
    
  j += 8  # Skip 'TRAK' and a word containing the length of the phrase in ticks (96 ticks per crotchet)
  
  k = struct.unpack('<I', b[j:j+4])[0] # Length of actual data
  if j + k > len(b):
    raise Exception("Corrupt CPFF")
  
  j += 4
  
  m = MIDIFile(trk_count, ticks_per_quarternote=480)  # 480 TPQN is what CT-X uses in its SMF conversions
  
  m.addTimeSignature(0, 0, 4, 2, 24) # 4/4 time. It seems CT-X doesn't allow any other option here. 24 clocks-per-tick is what CT-X uses in its SMF conversions
  m.addTempo(0, 0, 120) # Helpful to have something defined here
  m.addTrackName(0, 0, trk_name)

  
  process_phr_trak(b[j:j+k], m)
  return m


def process_phr_multiple(d):
  #Process multiple CPFF wrappers of multiple phrase definitions
  #
  
  trk_count = len(d)
  if trk_count < 4:
    trk_count = 4   # Pad to 4 tracks
  
  if trk_count > 10:
    # Not sure what the upper limit is. Probably can't go past 16 because midiutils
    # can't handle that.
    
    raise Exception("Too many tracks ({0})".format(trk_count))
  
  m = MIDIFile(trk_count, ticks_per_quarternote=480)  # 480 TPQN is what CT-X uses in its SMF conversions
  
  m.addTimeSignature(0, 0, 4, 2, 24) # 4/4 time. It seems CT-X doesn't allow any other option here. 24 clocks-per-tick is what CT-X uses in its SMF conversions
  m.addTempo(0, 0, 120) # Helpful to have something defined here
  
  
  for i in range(trk_count):
    
    if i < len(d):
      
      b = d[i]
  
      if b[0:4] != b'CPFF':
        raise Exception("Expecting CPFF")
      
      trk_name = b[0xC:0x18].decode('ascii')
      
      j = 8 + struct.unpack('<I', b[4:8])[0] # Jump forward length of the header portion
      
      if b[j:j+4] != b'TRAK':
        raise Exception("Expecting TRAK")
        
      j += 8
      
      k = struct.unpack('<I', b[j:j+4])[0] # Length of actual data
      if j + k > len(b):
        raise Exception("Corrupt CPFF")
      
      j += 4
      
      m.addTrackName(i, 0, trk_name)


      process_phr_trak(b[j:j+k], m, track=i, channel=4+i)
  return m
  
  



def extract_from_phrase_set(b):
  # Extracts 4 individual phrases from a .PHS file contents
  
  a = []
  
  # Skip first 16 bytes -- it will be "CT-X3000" or similar
  i = 16
  
  if b[i:i+4] != b'PHSH':
    raise Exception("Expected PHSH")
  i += 8
  
  while i < len(b):
  
    if b[i:i+4] != b'PHRH':
      raise Exception("Expected PHRH")
    i += 8
    
    crc = struct.unpack('<I', b[i:i+4])[0]
    i += 4
    length = struct.unpack('<I', b[i:i+4])[0]
    i += 4
    
    crc_2 = binascii.crc32(b[i:i+length])
    
    if crc_2 != crc:
      raise Exception("CRC mismatch")
    
    a.append(b[i:i+length])
    i += length
    if b[i:i+4] != b'EODA':
      raise Exception("Expected EODA")
      
    i += 4
    
  return a



if __name__=="__main__":
  if len(sys.argv) >= 2:
    with open(sys.argv[1], 'rb') as f:
      b = f.read()
    # Extracts the data from a .PHS file, then writes the resulting MIDI to
    # standard output
    d = extract_from_phrase_set(b)
    m = process_phr_multiple(d[:])
    m.writeFile(sys.stdout.buffer)

