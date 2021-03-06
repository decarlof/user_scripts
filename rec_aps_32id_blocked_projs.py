# -*- coding: utf-8 -*-

"""
TomoPy example to reconstruct a micro-CT data set containing a series 
of dark projections becuase of the presence of an environment cell blocking
some of the sample views.
"""

import tomopy
import numpy as np
import matplotlib.pylab as pl

# set the path to the micro-CT data set ro reconstruct
#fname = 'data_dir/sample.h5'
fname = '/local/dataraid/2014_11/haozhe/Ce6Al4_3kbar_.h5'

# Set the start/end index of the blocked projections 
miss_angles = [141,226]

# Select the sinogram range to reconstruct
start = 740; end = 1700

print '\n#### Processing '+ fname

chunks = 10 # number of data chunks for the reconstruction
nSino_per_chunk = (end - start)/chunks

print "Reconstructing [%d] slices from slice [%d] to [%d] in [%d] chunks of [%d] slices each" % ((end - start), start, end, chunks, nSino_per_chunk)

for iChunk in range(0,chunks):
    print '\n  -- chunk # %i' % (iChunk+1)
    sino_chunk_start = start + nSino_per_chunk*iChunk 
    sino_chunk_end = start + nSino_per_chunk*(iChunk+1)
    print '\n  --------> [%i, %i]' % (sino_chunk_start, sino_chunk_end)

    if sino_chunk_end > end: 
        break

    # Read the APS 32-ID or 2-BM raw data
    prj, flat, dark = tomopy.io.exchange.read_aps_32id(fname, sino=(sino_chunk_start, sino_chunk_end))

    # Manage the missing angles:
    theta  = tomopy.angles(prj.shape[0])
    prj = np.concatenate((prj[0:miss_angles[0],:,:], prj[miss_angles[1]+1:-1,:,:]), axis=0)
    theta = np.concatenate((theta[0:miss_angles[0]], theta[miss_angles[1]+1:-1]))

    # Normalize the raw projection data
    prj = tomopy.normalize(prj, flat, dark)

    # Reconstruct using gridrec
    best_center = 1232
    rec = tomopy.recon(prj, theta, center=best_center, algorithm='gridrec', emission=False)

    # Set reconstructed images name
    rec_name = 'rec/sample'
    print rec_name

    # Write data as stack of TIFs.
    tomopy.io.writer.write_tiff_stack(rec, fname=rec_name, start=sino_chunk_start)


