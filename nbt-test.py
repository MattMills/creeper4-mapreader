import gzip
import struct
import sys


#Due to the way the recursion works right now, need to increase the limit a bit
sys.setrecursionlimit(10000)

#OPTION: output ByteArrays as files, trying to guess if they are JPG, PNG, or TXT. (byte arrays are not otherwise output as files or in print output)
opt_output_files = False

#OPTION: output structure to stdout, uses recursive_print below.
opt_print = False




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
    'Quaternion': 16,
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
    ##'ByteArray': '<B',
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


depth = 0
tag_path = []

file_count = 1

if opt_output_files:
    with open('output-filenames.txt', 'w') as fh:
        fh.write('')


def nbt_read_string(fh):
    string_size = int.from_bytes(fh.read(2), byteorder="little")
    if(string_size > 255):
        raise(BaseException('Invalid string size?'))
    string = fh.read(string_size)

    return string.decode('utf-8')

def nbt_read(fh, tag_tree, sub_tag = None):
    global depth, file_count, tag_path

    fh_pos = fh.tell()

    if sub_tag == None:
        byte_in = fh.read(1)
        if len(byte_in) == 0:
            return tag_tree
        tag_type = ord(byte_in)
    else:
        tag_type = sub_tag
    

    #tag names per il2cpp data NBT.Tags.Tag$$GetNamedTypeFromId()
    if tag_type not in tag_value_to_name:   
        raise(BaseException('FATAL ERROR: Undefined NBT tag type: %s at file offset: %s' % (tag_type, fh_pos)))

    tag = tag_value_to_name[tag_type]
    value = None
    length = 0
    
    #print('DBG_NBT_READ %s, %s %s' % (fh_pos, tag_path, tag))
    
    if tag_type != 0 and sub_tag == None:
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
                unpacked_values = list(struct.unpack(type_format, byte_string))
                if(len(unpacked_values) == 1):
                    value.append(unpacked_values[0])
                else:
                    value.append(unpacked_values)
        else:
            unpacked_values = list(struct.unpack(type_format, byte_string))
            if(len(unpacked_values) == 1):
                value = unpacked_values[0]
            else:
                value = unpacked_values
    else:
        if tag == 'String':
            value = fh.read(length)
    
        elif tag == 'List':
            sub_tag_id = int.from_bytes(fh.read(1), byteorder='little')
            length = int.from_bytes(fh.read(4), byteorder='little', signed=True)
        elif tag == 'StringArray':
            value = '(count: %s) ' % (length, )
            for i in range(0, length):
                value += '"%s",' % (nbt_read_string(fh),)
        elif tag == 'ByteArray':
            value = fh.read(length)
 
    if tag in ('ByteArray',) and length > 0 and opt_output_files:
        extension = ''

        if(value.find(b'JFIF') != -1):
            extension = '.jpg'
        elif(value.find(b'PNG') != -1):
            extension = '.png'
        elif(all(c < 128 for c in value)):
            extension = '.txt'
        
        with open('output-%s%s'% (file_count, extension), 'wb') as fwh:
            fwh.write(value)

        with open('output-filenames.txt', 'a') as fwh:
            fwh.write('%s output-%s%s %s\n'% (name, file_count, extension, tag_path))
        file_count += 1

   
    #if tag not in ('ByteArray', ) and not ('Array' in tag  and length > 100):
    #    print('%s[%s]{%s} %s - "%s" (len: %s) %s' % (''.join(['\t'*depth]), tag_type, fh_pos, tag, name, length, value))
    #else:
    #    print('%s[%s]{%s} %s - "%s" (len: %s)' % (''.join(['\t'*depth]), tag_type, fh_pos, tag, name, length))
    
    this_tag = {
        'tag': tag,
        'name': name, 
        'tag_type': tag_type, 
        'file_pos': fh_pos, 
        'length': length, 
        'value': value
    }

    #print('DBG_NBT_READ %s, %s %s %s' % (fh_pos, tag_path, tag, name))

    if tag == 'List':

        this_tag['sub_tag_id'] = sub_tag_id

        this_tag['value'] = []

        for i in range(0, length):
            tag_path.append('List-%s' % name)
            depth += 1
            result = nbt_read(fh,[], sub_tag_id)

            this_tag['value'].append(result)
           
        tag_tree.append(this_tag)
    if tag == 'Compound':
        depth += 1
        tag_path.append(name)
        result = nbt_read(fh, [])
        this_tag['value'] = result

        tag_tree.append(this_tag)

    elif tag == 'End':
        depth -= 1
        if(len(tag_path) > 0):
            tag_path.pop()

        tag_tree.append(this_tag)
        return tag_tree
    else:
        tag_tree.append(this_tag)

    if(sub_tag != None ):
        depth -= 1
        if(len(tag_path) > 0):
            tag_path.pop()
        return tag_tree
    else:
        return nbt_read(fh, tag_tree)












def recursive_print(depth, obj):
    if isinstance(obj, list):
        for x in obj:
            recursive_print(depth+1, x)
    elif isinstance(obj, dict) and 'value' in obj.keys() and isinstance(obj['value'], list) and obj['tag'] in ('Compound', 'List'):
        filtered_dict = {k:v for k,v in obj.items() if k not in 'value'}

        print('%s%s VALUES [ ' % (''.join(' '*depth), filtered_dict))
        for x in obj['value']:
            recursive_print(depth+1, x)
        print('%s] ' % (''.join(' '*depth)))
        
    else:
        if isinstance(obj, dict) and 'tag' in obj.keys() and obj['tag'] in ('ByteArray',) and 'value' in obj.keys():
            del obj['value']
        print('%s%s,' % (''.join(' '*depth), obj))

with open('test1.cw4', mode='rb') as fh:
    expected_file_size = int.from_bytes(fh.read(4), byteorder="little")

    gzfh = gzip.GzipFile(fileobj=fh)
    #contents = gzfh.read()
    #measured_file_size = len(contents)
    #gzfh.seek(4)
    try:
        tag_tree = nbt_read(gzfh, [])
    except:
        raise

    if(opt_print):
        recursive_print(0, tag_tree)
        


#if expected_file_size != measured_file_size:
#    print('ERROR: Expected file size error! %s / %s' % (measured_file_size, expected_file_size))
#    exit()


