#!/usr/bin/env python
import argparse
import matrix_functions as mf 
import numpy as np 
import h5py
import shutil
import sys

def main():

	parser=argparse.ArgumentParser(description='Get cis percent for window range of bin of Hi-C hdf5 file' +
		' for each row of Hi-C matrix')
	parser.add_argument('-i', help='input hdf5 Hi-C file', type=str, required=True)
	parser.add_argument('-r', help='window range', type=int, default=6000000)
	parser.add_argument('-m', help='create hdf5 with NAs in out of range loci', type=bool, default=False)
	parser.add_argument('-n', help='maximum percent of NAs allowed in window', type=float, default=10.0)
	args=parser.parse_args()
	
	# percent of NAs allowed
	p = args.n/100

	if args.m: 
		# Get hdf file
		f = h5py.File(args.i, 'r')

		# Make test hdf5
		if args.i[-5:] == '.hdf5':
			filename_prefix = args.i[:-5]
			rangeCis_file = filename_prefix + '_RangeCis.hdf5'
			shutil.copy(args.i, rangeCis_file)
			f = h5py.File(rangeCis_file, 'r+')
			obs = f['interactions'][:]
			blocksize = f['interactions'].chunks

			bin_positions = f['bin_positions'][:]
			resolution =  mf.get_resolution(f)
			max_NAs = (args.r/resolution) * p
			dist = (args.r/resolution)/2
			num_bins = len(obs)
			for i in range(num_bins):
				# Check if row is all nan
				if np.all(np.isnan(obs[i])) or np.nansum(obs[i]) == 0:
					obs[i] = np.nan
				# Check if at start of genome
				elif i - dist < 0:
					obs[i] = np.nan
				# Check if at end of genome
				elif i + (dist -1) > num_bins -1:
					obs[i] = np.nan
				# Check if at start of chromosome (upstream range reaches trans)
				elif bin_positions[i,0] != bin_positions[i-dist,0]:
					obs[i] = np.nan
				# Check if at end of chromosome (downstream range reaches trans) 
				elif bin_positions[i,0] != bin_positions[i+(dist-1),0]:
					obs[i] = np.nan
				else:
					store = np.copy(obs[i, i-dist:i+dist])
					# Check if too many NAs in range window
					if np.sum(np.isnan(store)) > max_NAs:
						obs[i] = np.nan
					else:
						obs[i] = np.nan
						obs[i, i-dist:i+dist] = store
			del f['interactions']	
			f.create_dataset("interactions",  data=obs, dtype='float64', 
				compression='gzip', chunks=blocksize)
			f.close()
		
		else:
			print 'ERROR: wrong file extension'
			sys.exit()

	# Get cis percent
	f = h5py.File(args.i, 'r')
	cp = mf.get_cis_percent_range(f, args.r, p) 
	# Write output
	OUT = open(args.i[:-5] + '_range' + str(args.r/1000000) + 'Mb_cispercent.bedGraph', 'w')
	# Only using 22 autosomes and X
	y_chrom_bin_start =  f['chr_bin_range'][:][23][0]
	for i, b in enumerate(f['bin_positions'][:][:y_chrom_bin_start]):
		if b[0] == 22:
			chrom = 'chrX'
		else:
			chrom = 'chr' + str(b[0]+1)
		OUT.write(chrom+'\t'+str(b[1])+'\t'+str(b[2])+
		'\t'+ str(cp[i])+'\n')
	OUT.close()


if __name__ == '__main__':
	main()