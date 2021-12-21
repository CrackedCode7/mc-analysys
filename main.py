import struct
import math
import time
import zlib
import pprint

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
        self.data = None
        self.payload_size = 0
    

class TAG_Byte:
    id = 1
    
    def __init__(self, buffer):
        self.data = buffer[0]
        self.payload_size = 1


class TAG_Short:
    id = 2
    
    def __init__(self, buffer):
        self.data = int.from_bytes(buffer[0:2], 'big')
        self.payload_size = 2


class TAG_Int:
    id = 3
    
    def __init__(self, buffer):
        self.data = int.from_bytes(buffer[0:4], 'big')
        self.payload_size = 4


class TAG_Long:
    id = 4
    
    def __init__(self, buffer):
        self.data = struct.unpack('>q', buffer[0:8])
        self.payload_size = 8


class TAG_Float:
    id = 5
    
    def __init__(self, buffer):
        self.data = struct.unpack('>f', buffer[0:4])
        self.payload_size = 4


class TAG_Double:
    id = 6
    
    def __init__(self, buffer):
        self.data = struct.unpack('>d', buffer[0:8])
        self.payload_size = 8


class TAG_Byte_Array:
    id = 7

    def __init__(self, buffer):   
        self.size = int.from_bytes(buffer[:4], 'big')
        self.payload_size = 4 + self.size

        self.data = buffer[4:4+self.size] # THIS NEEDS TO BE CHECKED


class TAG_String:
    id = 8

    def __init__(self, buffer):
        self.size = int.from_bytes(buffer[:2], 'big')
        self.payload_size = 2 + self.size
        
        self.data = buffer[2:2+self.size].decode('utf-8')


class TAG_List:
    id = 9
    
    def __init__(self, buffer):
        self.list_type = buffer[0]
        self.size = int.from_bytes(buffer[1:5], 'big')

        self.data = None

        self.payload_size = 1 + 4

        # Test which type the list is, then determine payload size based on that
        for tag in TAGS.ALL:
            if tag.id == self.list_type:
                pass
        
        print("SET UP DATA FOR LIST TAG")


class TAG_Compound:

    id = 10
    
    def __init__(self, buffer):
    
        self.data = {}
        self.buffer = buffer

        self.payload_size = 0
        
        self.construct_dict()
    
    def construct_dict(self):
    
        type_id = 10 # Initialize to compound tag, this can be anything but 0
        while type_id != 0:
            print(len(self.buffer))
            
            type_id = self.buffer[0]
            self.buffer = self.buffer[1:] # should remove a byte
            self.payload_size += 1
            if type_id != 0:
                string_length = int.from_bytes(self.buffer[0:2], 'big')
                self.buffer = self.buffer[2:]
                self.payload_size += 2
            else:
                string_length = 0
            
            if string_length != 0:
                name = self.buffer[0:string_length].decode('utf-8')
                self.buffer = self.buffer[string_length:]
                self.payload_size += string_length
            else:
                name = ''

            for tag in TAGS.ALL:
                if tag.id == type_id:
                    new_tag = tag(self.buffer)
                    self.data[name] = new_tag
                    self.buffer = self.buffer[new_tag.payload_size:]
                    self.payload_size += new_tag.payload_size


class TAG_Int_Array:
    id = 11
    
    def __init__(self, buffer):
        self.size = int.from_bytes(buffer[:4], 'big')

        self.data = None

        self.payload_size = 4 + 4*self.size

        print("SET UP DATA FOR INT ARRAY")


class TAG_Long_Array:
    id = 12
    
    def __init__(self, buffer):
        self.size = int.from_bytes(buffer[:4], 'big')

        self.data = None

        self.payload_size = 4 + 8*self.size


class TAGS:
    ALL = [TAG_End, TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float, 
           TAG_Double, TAG_Byte_Array, TAG_String, TAG_List, TAG_Compound, 
           TAG_Int_Array, TAG_Long_Array]


if __name__ == '__main__':

    with open('r.0.0.mca', 'rb') as f:

        data = f.read()
        buffer = read_chunk_data(0, 0, data)
        
        cmpd = TAG_Compound(buffer)
        pprint.pprint(cmpd.data)