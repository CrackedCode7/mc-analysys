import struct
import math
import time
import zlib

# First 8192 bytes are the header of the mca file.
# After this, the first 4 bytes are a Big-Endian length field which is the REMAINING length of the chunk data.
# Then there is a 1 byte character that represents the compression scheme, 2 is zlib. The remaining length-1 bytes is the chunk data (compressed)

# -22, 79 is "home base"

def get_region(chunk_x: int, chunk_z: int):
    """Calculates the region index given chunk coordinates"""
    return (math.floor(chunk_x/32), math.floor(chunk_z/32))

def get_offset(chunk_x: int, chunk_z: int):
    return 4*((chunk_x%32)+(chunk_z%32)*32)

print(get_region(-22, 79))
print(get_offset(-22, 79))

with open('r.-1.2.mca', 'rb') as f:
    """
    f.read(1960)

    chunk_offset = f.read(3)
    print(int.from_bytes(chunk_offset, 'big'), 'is the beginning of the chunk (in 4kB sectors)')

    length = f.read(1)
    print(int.from_bytes(length, 'big'), 'is the number of 4kB sectors in the chunk')

    f.read(4096)

    timestamp = f.read(4)
    print(time.time()-struct.unpack('>i', timestamp)[0], 'seconds since chunk was last updated.')"""

    f.read(4096*1779)

    rem_length = struct.unpack('>i', f.read(4))
    print(rem_length)

    compression_scheme = int.from_bytes(f.read(1), 'big')
    print(compression_scheme)

    compressed_data = f.read(rem_length[0]-1)
    decompressed_data = zlib.decompress(compressed_data)
    print(decompressed_data[:16])