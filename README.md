# Casio Phrase Pads
[WORK IN PROGRESS] Tools to translate between CPFF (Casio Phrase File Format) and Standard MIDI. CPFF is used as the format for Phrase Sets and Phrase Pads on the CT-X range of keyboards.

## Phrase to MIDI
A file with extension .PHS saved by the CT-X keyboard can be converted to a standard MIDI file by calling (for example):

```
python phrase2mid.py PHRSET01.PHS > 01.MID
```

It also handles phrase sets read directly from the keyboard. The following snippet of Python code will do that (note that the downloading portion of this will only work under Linux - the processing from phrase to MIDI is agnostic to Linux/Windows):

```python
from internal.sysex_comms_internal import download_ac7_internal
from phrase2mid import process_phr

PHR_NUM=4 # 0-3 are Phrase Set 01, 4-7 are Phrase Set 02, ... 96-99 are Phrase Set 25.
y = download_ac7_internal(PHR_NUM, category=35, memory=1)
with open('MyPhrase.MID', 'wb') as f:
  f.write(process_phr(y))
```

## Prerequisites
Writing MIDI uses the `midiutils` library (<https://pypi.org/project/MIDIUtil/>), which must be installed before doing phrase-to-MIDI conversions. Reading
MIDI uses home-grown code which doesn't need anything to be installed.
