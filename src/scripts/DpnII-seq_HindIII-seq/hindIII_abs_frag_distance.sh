#!/bin/bash

#BSUB -q long
#BSUB -W 144:00
#BSUB -R rusage[mem=10000]
#BSUB -J "myarray[1-278]"
#BSUB -oo out_frag.%I
#BSUB -eo err_frag.%I

SAM_FILE=$(printf "bowtie_output_mapped_%03d" $LSB_JOBINDEX)
./hindIII_abs_frag_distance.py -s $SAM_FILE -o True

