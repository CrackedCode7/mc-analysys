import struct
import math
import time
import zlib
import pprint
import os
import json

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
    
    def __init__(self):
        self.data = None
    

class TAG_Byte:
    id = 1
    
    def __init__(self):
        self.data = f.read(1)


class TAG_Short:
    id = 2
    
    def __init__(self):
        self.data = int.from_bytes(f.read(2), 'big')


class TAG_Int:
    id = 3
    
    def __init__(self):
        self.data = int.from_bytes(f.read(4), 'big')


class TAG_Long:
    id = 4
    
    def __init__(self):
        self.data = struct.unpack('>q', f.read(8))


class TAG_Float:
    id = 5
    
    def __init__(self):
        self.data = struct.unpack('>f', f.read(4))


class TAG_Double:
    id = 6
    
    def __init__(self):
        self.data = struct.unpack('>d', f.read(8))


class TAG_Byte_Array:
    id = 7

    def __init__(self):   
        self.size = int.from_bytes(f.read(4), 'big')
        self.data = f.read(self.size)


class TAG_String:
    id = 8

    def __init__(self):
        self.size = int.from_bytes(f.read(2), 'big')
        self.data = f.read(self.size).decode('utf-8')


class TAG_List:
    id = 9
    
    def __init__(self):
        self.list_type = int.from_bytes(f.read(1), 'big')
        self.size = int.from_bytes(f.read(4), 'big')

        self.data = []
        for tag in TAGS.ALL:
            if tag.id == self.list_type:
                for _ in range(self.size):
                    self.data.append(tag().data)
        
        #print("SET UP DATA FOR LIST TAG")


class TAG_Compound:

    id = 10
    
    def __init__(self):
    
        self.data = {}
        self.construct_dict()
    
    def construct_dict(self):
    
        type_id = 10 # Initialize to compound tag, this can be anything but 0
        while type_id != 0:
            
            type_id = int.from_bytes(f.read(1), 'big')

            if type_id != 0:
                string_length = int.from_bytes(f.read(2), 'big')

            else:
                string_length = 0
            
            if string_length != 0:
                name = f.read(string_length).decode('utf-8')

            else:
                name = ''

            for tag in TAGS.ALL:
                if tag.id == type_id:
                    if type_id != 0:
                        self.data[name] = tag().data


class TAG_Int_Array:
    id = 11
    
    def __init__(self):
        self.size = int.from_bytes(f.read(4), 'big')
        
        self.data = []
        for _ in range(self.size):
            self.data.append(TAG_Int().data)


class TAG_Long_Array:
    id = 12
    
    def __init__(self):
        self.size = int.from_bytes(f.read(4), 'big')
        
        self.data = []
        for _ in range(self.size):
            self.data.append(TAG_Long().data)


class TAGS:
    ALL = [TAG_End, TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float, 
           TAG_Double, TAG_Byte_Array, TAG_String, TAG_List, TAG_Compound, 
           TAG_Int_Array, TAG_Long_Array]


if __name__ == '__main__':

    with open('r.0.0.mca', 'rb') as f:

        data = f.read()
        buffer = read_chunk_data(0, 0, data)
        
        output_file = open('temp', 'wb')
        output_file.write(buffer)
        output_file.close()
        
    with open('temp' , 'rb') as f:
        
        chunk = {}
        while True:
        
            tag_id = int.from_bytes(f.read(1), 'big')
            if not tag_id:
                break
            
            # Interpret tag id
            if tag_id != 0:
            
                string_length = int.from_bytes(f.read(2), 'big')
                name = f.read(string_length).decode('utf-8')

                for tag in TAGS.ALL:
                    if tag.id == tag_id:
                        chunk[name] = tag().data
        
        with open("log.log", "w") as log_file:
            #json.dump(chunk, log_file)
            pprint.pprint(chunk, log_file)
    
    os.remove('temp')
    pprint.pprint(chunk)