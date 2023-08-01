import gzip
import python_nbt
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

    tag_type = ord(fh.read(1))
    print(tag_type)
    if tag_type != 0:
        name = nbt_read_string(fh)
    else:
        name = ''

    tag = 'unimplemented[%s]' % (tag_type)
    value = 'n/a'

    if tag_type == 0:
        #TAG_End
        tag = 'End'
        depth-=1
    elif tag_type == 1:
        tag = 'Integer'
        value = int.from_bytes(fh.read(4), byteorder='little')
    elif tag_type == 2:
        tag = 'Short'
        fh.read(4)
    elif tag_type == 3:
        tag = 'String?'
        length = int.from_bytes(fh.read(2), byteorder='little')
        string = fh.read(length)
        
        value = '(len: %s) "%s"'  % (length, string)
        
    elif tag_type == 4:
        tag = 'Long'
        fh.read(8)
    elif tag_type == 5:
        tag = 'Float'
        fh.read(2)
    elif tag_type == 6:
        tag = 'Double'
        fh.read(8)
    elif tag_type == 7:
        tag = 'Byte_Array'
        length = int.from_bytes(fh.read(4), byteorder='little') 
        value = length
        fh.read(length)
    
    elif tag_type == 8:
        tag = 'String'
    elif tag_type == 9:
        tag = 'List'
        sub_tag_id = int.from_bytes(fh.read(4), byteorder='little')
        length = int.from_bytes(fh.read(4), byteorder='little')
        print('List: %s %s ' % (sub_tag_id, length))
    elif tag_type == 10:
        #TAG_Compound
        tag = "Compound"
        depth+=1
    elif tag_type == 11: # int array?
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*4)
    elif tag_type == 227:
        fh.read(6)
    elif tag_type == 228:
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*16)
        
    elif tag_type == 229:
        fh.read(16)
    elif tag_type == 230:
        fh.read(1)
    elif tag_type == 243:
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*4)
    elif tag_type == 244:
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*8)
    elif tag_type == 247:
        length = int.from_bytes(fh.read(4), byteorder='little')
        value = length
        fh.read(length*2)

    print('%s>[%s] %s - "%s" (%s)' % (depth, tag_type, tag, name, value))
with open('test1.cw4', mode='rb') as fh:
    expected_file_size = int.from_bytes(fh.read(4), byteorder="little")

    gzfh = gzip.GzipFile(fileobj=fh)
    #contents = gzfh.read()
    #measured_file_size = len(contents)
    #gzfh.seek(4)

    while(1):
        nbt_read(gzfh)
        


#if expected_file_size != measured_file_size:
#    print('ERROR: Expected file size error! %s / %s' % (measured_file_size, expected_file_size))
#    exit()


#for i in range(0, 32):
#    print('%s %s %s' % (contents[i:i+1], hex(ord(contents[i:i+1])), ord(contents[i:i+1])))
