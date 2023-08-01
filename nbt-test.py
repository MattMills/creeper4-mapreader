import gzip
import python_nbt
import struct

depth = 0

def nbt_read_string(fh):
    string_size = int.from_bytes(fh.read(2), byteorder="little")
    if(string_size > 255):
        raise(BaseException('Invalid string size?'))
    string = fh.read(string_size)

    return string.decode('utf-8')

def nbt_read(fh):
    global depth
    #it is assumed that the next byte is a tagType

    byte_in = fh.read(1)
    if len(byte_in) == 0:
        return False
    tag_type = ord(byte_in)
    if tag_type != 0:
        name = nbt_read_string(fh)
    else:
        name = ''

    tag = 'unimplemented[%s]' % (tag_type)
    value = 'n/a'

    if tag_type == 0:
        #TAG_End
        tag = 'End'
    elif tag_type == 1:
        tag = 'int32_t'
        value = int.from_bytes(fh.read(4), byteorder='little', signed=True)
    elif tag_type == 2:
        tag = 'float'
        byte_string = fh.read(4)
    
        value = struct.unpack('<f', byte_string)[0]
    elif tag_type == 3:
        tag = 'String'
        length = int.from_bytes(fh.read(2), byteorder='little')
        string = fh.read(length)
        
        value = '(len: %s) "%s"'  % (length, string)
        
    elif tag_type == 4:
        tag = '5 byte unk'
        fh.read(5)
    elif tag_type == 5:
        tag = 'short?'
        value = int.from_bytes(fh.read(2), byteorder='little')
    elif tag_type == 6:
        tag = 'Double?'
        byte_string = fh.read(8)
        value = struct.unpack('<d', byte_string)[0]
    elif tag_type == 7:
        tag = 'Byte_Array?'
        length = int.from_bytes(fh.read(4), byteorder='little') 
        byte_string = fh.read(length)
        is_jfif = byte_string.find(b"JFIF")
        is_gzip = byte_string.find(b"\x1f\x8b")
        value = '(len: %s) jfif %s  gzip %s' % (length, is_jfif, is_gzip)
        
    
    elif tag_type == 8:
        tag = 'byte unk1'
        value = int.from_bytes(fh.read(1), byteorder='little')
    elif tag_type == 9:
        tag = 'List'
        sub_tag_id = int.from_bytes(fh.read(4), byteorder='little')
        length = int.from_bytes(fh.read(4), byteorder='little')
        print('List: %s %s ' % (sub_tag_id, length))
    elif tag_type == 10:
        #TAG_Compound
        tag = "Compound"
    elif tag_type == 11: # int array?
        tag = 'variable length int32_t array'
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = '(len: %s) ' % length
        for i in range(0, length):
            byte_string = fh.read(4)
            value += '%s,' % (int.from_bytes(byte_string, byteorder='little', signed=True),)
    elif tag_type == 227:
        tag = '6 byte something'
        fh.read(6)
    elif tag_type == 228:
        tag = '16 byte variable length array'
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*16)
        
    elif tag_type == 229:
        tag = '16  byte unk'
        fh.read(16)
    elif tag_type == 230:
        tag = 'byte unk2' #bool?
        value = int.from_bytes(fh.read(1), byteorder='little')
    elif tag_type == 231:
        tag = 'variable length string array'
        length = int.from_bytes(fh.read(4), byteorder='little')

        value = '(count: %s) ' % (length, )
        for i in range(0, length):
            value += '"%s",' % (nbt_read_string(fh),)
    elif tag_type == 232:
        tag = 'unk variable length 8 byte array'
        length = int.from_bytes(fh.read(4), byteorder='little')
        fh.read(length*8)
        value  = '(len: %s) ' % length
    elif tag_type == 233:
        tag = 'unk variable length 12 byte array'
        length = int.from_bytes(fh.read(4), byteorder='little')
        fh.read(length*12)
        value  = '(len: %s) ' % length
    elif tag_type == 235:
        tag = '12 byte unk'
        fh.read(12)
    elif tag_type == 243:
        tag = 'variable length float array'
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = '(len: %s) ' % (length, )
        for i in range(0, length):
            byte_string = fh.read(4)
            value += '%s,' % (struct.unpack('<f', byte_string)[0],)

    elif tag_type == 244:
        tag = '8 byte array?'
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*8)
    elif tag_type == 247:
        tag = '2 byte array?'
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*2)
    else:
        print('undefined tag %s' % tag_type)
        exit()
    
    print('%s[%s] %s - "%s" (%s)' % (''.join(['\t'*depth]), tag_type, tag, name, value))
    if tag_type == 10:
        depth += 1
    if tag_type == 0:
        depth -= 1
        if depth < 0:
            print('-----------------------------------------------------------')
            depth = 0

    return True

with open('test1.cw4', mode='rb') as fh:
    expected_file_size = int.from_bytes(fh.read(4), byteorder="little")

    gzfh = gzip.GzipFile(fileobj=fh)
    #contents = gzfh.read()
    #measured_file_size = len(contents)
    #gzfh.seek(4)

    ret = True
    while(ret):
        ret = nbt_read(gzfh)
        


#if expected_file_size != measured_file_size:
#    print('ERROR: Expected file size error! %s / %s' % (measured_file_size, expected_file_size))
#    exit()


#for i in range(0, 32):
#    print('%s %s %s' % (contents[i:i+1], hex(ord(contents[i:i+1])), ord(contents[i:i+1])))
