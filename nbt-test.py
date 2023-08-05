import gzip
import python_nbt
import struct

depth = 0

tag_value_to_name = {
    0: 'End',
    1: 'Int',
    2: 'Float',
    3: 'String',
    4: 'List',
    5: 'Short',
    6: 'Double',
    7: 'ByteArray',
    8: 'Byte',
    9: 'Long',
    10: 'Compound',
    11: 'IntArray',
    227: 'BoolArray',
    228: 'Vector4Array',
    229: 'Vector4',
    230: 'Bool',
    231: 'StringArray',
    232: 'Vector2Array',
    233: 'Vector3Array',
    234: 'Vector2',
    235: 'Vector3',
    236: 'Quaternion',
    238: 'ULongArray',
    239: 'UIntArray',
    240: 'UShortArray',
    241: 'SByteArray',
    242: 'DoubleArray',
    243: 'FloatArray',
    244: 'LongArray',
    245: 'Timestamp',
    246: 'DateTime',
    247: 'ShortArray',
    248: 'ULong',
    249: 'UInt', 
    250: 'UShort',
    251: 'SByte',
    253: 'IP',
    254: 'MAC',
}

type_bytes = {
    'End': 0,
    'Int': 4,
    'Float': 4,
    'Short': 2,
    'Double': 8,
    'ByteArray': 1,
    'Byte': 1,
    'Long': 8,
    'IntArray': 4,
    'BoolArray': 1,
    'Vector4Array': 16,
    'Vector4': 16,
    'Bool': 1,
    'StringArray': 1,
    'Vector2Array': 8,
    'Vector3Array': 12,
    'Vector2': 8,
    'Vector3': 12,
    #'Quaternion': unk,
    'ULongArray': 8,
    'UIntArray': 4,
    'UShortArray': 2,
    'SByteArray': 1,
    'DoubleArray': 8,
    'FloatArray': 4,
    'LongArray': 8,
    'Timestamp': 8,
    'DateTime': 8,
    'ShortArray': 2,
    'ULong': 8,
    'UInt': 4,
    'UShort': 2,
    'SByte': 1,
    #'IP': unk,
    #'MAC': unk,
}

type_formats = {
    'Int': '<i',
    'Float': '<f',
    'Short': '<h',
    'Double': '<d',
    'ByteArray': '<B',
    'Byte': '<B',
    'Long': '<q',
    'IntArray': '<i',
    'BoolArray': '<?',
    'Vector4Array': '<ffff',
    'Vector4': '<ffff',
    'Bool': '<?',
    'Vector2Array': '<ff',
    'Vector3Array': '<fff',
    'Vector2': '<ff',
    'Vector3': '<fff',
    #'Quaternion': unk,
    'ULongArray': '<Q',
    'UIntArray': '<I',
    'UShortArray': '<H',
    'SByteArray': '<b',
    'DoubleArray': '<d',
    'FloatArray': '<f',
    'LongArray': '<q',
    #'Timestamp': '<q', #TODO: wrong
    #'DateTime': '<q', #TODO: wrong
    'ShortArray': '<h',
    'ULong': '<Q',
    'UInt': '<I',
    'UShort': '<H',
    'SByte': '<b',
    #'IP': unk,
    #'MAC': unk,

}    

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
    

    #tag names per il2cpp data NBT.Tags.Tag$$GetNamedTypeFromId()
    if tag_type not in tag_value_to_name:
        print('FATAL ERROR: Undefined NBT tag type: %s' % (tag_type,))
        exit()

    tag = tag_value_to_name[tag_type]
    value = ''
    length = 0

    if tag_type != 0:
        name = nbt_read_string(fh)
    else:
        name = ''

    if tag in type_bytes:
        read_size = type_bytes[tag]

    
    if 'Array' in tag:
        byte_string =  fh.read(4)
        length = struct.unpack('<i', byte_string)[0]

    elif tag == 'String':
        byte_string = fh.read(2)
        length = struct.unpack('<h', byte_string)[0]

    elif tag in type_bytes:
        byte_string = fh.read(read_size)
        length = 1

    
    if tag in type_formats:
        type_format = type_formats[tag]

        if 'Array' in tag:
            value = []
            for i in range(0, length):
                byte_string = fh.read(read_size)
                value.append(struct.unpack(type_format, byte_string))
        else:
            value = struct.unpack(type_format, byte_string)
    else:
        if tag == 'String':
            value = '(len: %s) "%s"'  % (length, fh.read(length))
    
        elif tag == 'List':
            sub_tag_id = int.from_bytes(fh.read(1), byteorder='little')
            length = int.from_bytes(fh.read(4), byteorder='little')
            value = 'sub_tag(%s) length(%s)' % (sub_tag_id, length)
            #TODO: recursion

        elif tag == 'StringArray':
            value = '(count: %s) ' % (length, )
            for i in range(0, length):
                value += '"%s",' % (nbt_read_string(fh),)
    
    if tag not in ('ByteArray', ):
        
        print('%s[%s] %s - "%s" (len: %s) %s' % (''.join(['\t'*depth]), tag_type, tag, name, length, value))
    else:
        print('%s[%s] %s - "%s" (len: %s)' % (''.join(['\t'*depth]), tag_type, tag, name, length))
        
    if tag == 'Compound':
        depth += 1
    if tag == 'End':
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
