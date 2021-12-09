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
    """Calculates the byte offset needed to find the chunk at the given coordinates in the header"""
    return 4*((chunk_x%32)+(chunk_z%32)*32)

def read_chunk_data(chunk_x: int, chunk_z: int, data: bytes):

    offset = get_offset(chunk_x, chunk_z)
    chunk_offset = int.from_bytes(data[offset:offset+3], 'big')*4096 # offset for chunk data in bytes
    chunk_length = int.from_bytes(data[offset+3:offset+4], 'big')*4096 # chunk length in bytes
    timestamp = int.from_bytes(data[offset+4100:offset+4104], 'big') # time since epoch of last update
    
    remaining_length = struct.unpack('>i', data[chunk_offset:chunk_offset+4])[0] # exact length in bytes of the remaining chunk data
    
    byte_index = chunk_offset+4
    compression_scheme = int.from_bytes(data[byte_index:byte_index+1], 'big')
    byte_index += 1
    
    last_byte = byte_index+remaining_length-1
    
    if compression_scheme == 2:
        return zlib.decompress(data[byte_index:last_byte])
    else:
        return


class TAG_End:
    id = 0
    
    def __init__(self, buffer):
        self.buffer = buffer
    

class TAG_Byte:
    id = 1
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Short:
    id = 2
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Int:
    id = 3
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Long:
    id = 4
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Float:
    id = 5
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Double:
    id = 6
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Byte_Array:
    id = 7

    def __init__(self, buffer):
        self.buffer = buffer


class TAG_String:
    id = 8

    def __init__(self, buffer):
        self.buffer = buffer


class TAG_List:
    id = 9
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Compound:

    id = 10
    
    def __init__(self, chunk_data):
    
        self.dict = {}
        self.buffer_index = 0
        
        self.type_id = int.from_bytes(chunk_data[0:1], 'big')

        string_length = int.from_bytes(chunk_data[1:3], 'big')
        if string_length != 0:
            self.name = chunk_data[3:3+string_length].decode('utf-8')
        else:
            self.name = ''
        
        self.buffer = chunk_data[3+string_length:]
        
        self.construct_dict()
    
    def construct_dict(self):
        
        while self.buffer_index < len(self.buffer):
            
            # Handle when a tag is encountered
            type_id = int.from_bytes(self.buffer[self.buffer_index:self.buffer_index+1], 'big')
            self.buffer_index += 1
            string_length = int.from_bytes(self.buffer[self.buffer_index:self.buffer_index+2], 'big')
            self.buffer_index += 2
            if string_length != 0:
                name = self.buffer[self.buffer_index:self.buffer_index+string_length].decode('utf-8')
                self.buffer_index += string_length
            else:
                name = ''
                break

            for tag in TAGS.ALL:
                if tag.id == type_id:
                    self.dict[name] = tag(self.buffer)


class TAG_Int_Array:
    id = 11
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAG_Long_Array:
    id = 12
    
    def __init__(self, buffer):
        self.buffer = buffer


class TAGS:
    ALL = [TAG_End, TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float, 
           TAG_Double, TAG_Byte_Array, TAG_String, TAG_List, TAG_Compound, 
           TAG_Int_Array, TAG_Long_Array]

with open('r.-1.2.mca', 'rb') as f:

    data = f.read()
    chunk_data = read_chunk_data(-22, 79, data)
    
    cmpd = TAG_Compound(chunk_data)
    print(len(cmpd.buffer))