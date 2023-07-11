#!/bin/python

import os
import sys
import time
import argparse
from internal.sysex_comms_internal import upload_ac7_internal, download_ac7_internal, get_single_parameter

from mid2phrase import combine_to_phrase_set

def download_phrase_set(Num, Out_File, Dev="/dev/midi1"):
    
    # Download the 4 phrases from the requested Phrase Set. If the Phrase Set
    # number is N+1, the parameter sets to download are:
    #   4N+0
    #   4N+1
    #   4N+2
    #   4N+3
    #

    Phrases = []
    for I in range(4):
        B = download_ac7_internal(4*(Num-1)+I, memory=1, category=35, fd=Dev)
        Phrases.append( B )
        time.sleep(0.2)
    
    with open(Out_File, "wb") as f2:
        f2.write(combine_to_phrase_set(Phrases))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
      prog="download_phrase_set",
      description="Downloads a phrase set from the CT-X3000/5000"
    )
    parser.add_argument(nargs="?", dest="_num", default = 1, type=int, choices=range(1,25+1), help="Number of the phrase set to download")
    parser.add_argument("-o", "--out", dest="_out", help="File to store the phrase set in. Should end in .PHS")
    
    args = parser.parse_args(sys.argv[1:])
    download_phrase_set(args._num, Out_File=args._out, Dev="/dev/midi2")


