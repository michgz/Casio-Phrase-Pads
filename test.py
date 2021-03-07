"""
Test the phrase processing by reading all phrase sets from the keyboard and running
them through the translation. Needs the 'internal' directory from ac7maker.
"""

import os
from phrase2mid import process_phr

from internal.sysex_comms_internal import download_ac7_internal

for VAL in range(100):
  y = download_ac7_internal(VAL, category=35, memory=1)
  
  with open("10.bin", "wb") as f:
    f.write(y)
  
  print("Phrase: {0}".format(VAL))
  
  if len(y)> 0:
    process_phr(y)
