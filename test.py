from main import read_chunk_data

with open('r.0.0.mca', 'rb') as f:

    data = f.read()
    chunk_data = read_chunk_data(0, 0, data)
    
    # Initial tag id
    print('Outer tag is type', int.from_bytes(chunk_data[0:1], 'big'))
    
    # Initial string length
    string_length = int.from_bytes(chunk_data[1:3], 'big')
    
    # Buffer to be passed down
    buffer = chunk_data[3+string_length:]
    
    lst = []
    while len(buffer) != 0:
        
        # Next tag id
        tag_id = buffer[0]
        print('tag is type', tag_id)
        buffer = buffer[1:]
        
        # Next name length
        name_length = int.from_bytes(buffer[0:2], 'big')
        print('tag name length is', name_length)
        buffer = buffer[2:]
        
        # name itself
        name = buffer[0:name_length].decode('utf-8')
        print('tag name is', name)
        buffer = buffer[name_length:]
        
        if tag_id == 10:
            # Read tags until tag 0 reached.
            print(buffer[0])
        
        break
        
        
        
        '''
        # Payload start
        # tag id
        print(buffer[8])
        
        # name length
        print(int.from_bytes(buffer[9:11], 'big'))
        
        # name itself
        print(buffer[11:11+6].decode('utf-8'))
        
        # string tag length of payload
        print(int.from_bytes(buffer[17:19], 'big'))
        
        # string tag data (payload interpreted)
        print(buffer[19:19+4].decode('utf-8'))
        
        # next tag id
        print(buffer[23])
        
        # next name length
        print(int.from_bytes(buffer[24:26], 'big'))
        
        # next name itself
        print(buffer[26:30].decode('utf-8'))
        
        # integer payload
        print(int.from_bytes(buffer[30:34], 'big'))
        
        # next next tag id
        print(buffer[34])
        
        # next next name length
        print(int.from_bytes(buffer[35:37], 'big'))
        
        # next next name itself
        print(buffer[37:47].decode('utf-8'))'''