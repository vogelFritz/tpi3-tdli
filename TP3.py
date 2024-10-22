import math
import heapq
import sys
import time
import struct
import os

def partition(array, low, high, parallel_arrays):
    pivot = array[high]

    i = low - 1

    for j in range(low, high):
        if array[j] > pivot:
            i += 1

            (array[i], array[j]) = (array[j], array[i])
            for parallel_array in parallel_arrays:
                (parallel_array[i], parallel_array[j]) = (parallel_array[j], parallel_array[i])

    (array[i + 1], array[high]) = (array[high], array[i + 1])
    for parallel_array in parallel_arrays:
        (parallel_array[i + 1], parallel_array[high]) = (parallel_array[high], parallel_array[i + 1])

    return i + 1


def quickSortDescendingParallel(array, low, high, parallel_arrays):
    if low < high:
        pi = partition(array, low, high, parallel_arrays)

        quickSortDescendingParallel(array, low, pi - 1, parallel_arrays)

        quickSortDescendingParallel(array, pi + 1, high, parallel_arrays)

def swap(arr, i, j):
    aux = arr[i]
    arr[i] = arr[j]
    arr[j] = aux

def list_recursive_sum(arr):
    sum = 0.0
    for i in range(len(arr)):
        if type(arr[i]) is list:
            sum += list_recursive_sum(arr[i])
        else:
            sum += arr[i]
    return sum

def list_recursive_sum_type_safe(maybe_arr):
    if maybe_arr is list:
        return list_recursive_sum(maybe_arr)
    else:
        return maybe_arr
    
from collections import Counter

# TODO: Obtener frecuencias en vez de probabilidades (al leer de a chunks no funciona)
def obtener_alfabeto_frecuencias(content, alfabeto_dict, longitud_palabra):
    chunks = [content[i:i + longitud_palabra] for i in range(0, len(content), longitud_palabra)]

    conteos = Counter(chunks)     # Contar las ocurrencias de cada símbolo
    for symbol, count in conteos.items():
        if symbol in alfabeto_dict:
            alfabeto_dict[symbol] += count
        else:
            alfabeto_dict[symbol] = count
    
    return alfabeto_dict

def calcular_tasa_compresion(original_path, compressed_path):
   
    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)

    
    tasa_compresion = original_size / compressed_size
    print(f"Tasa de compresión: {tasa_compresion:.4f}")
    
def calcular_rendimientos(codigo, frecuencias, total_symbols):
    longitud_media = 0
    entropia = 0
    #for i in range(len(codigo)):
    #    probabilidad = frecuencias[i] / total_symbols
    #    longitud_media += probabilidad * len(codigo[i])  # Longitud del código de Huffman

    #for f in frecuencias:
    #    probabilidad = f / total_symbols
    #    if probabilidad > 0:
    #        entropia += probabilidad * (-1) * math.log2(probabilidad)

    for i in range(len(codigo)):
        probabilidad = frecuencias[i] / total_symbols
        
       
        longitud_media += probabilidad * len(codigo[i])  
        
        
        if probabilidad > 0:
            entropia += probabilidad * (-1) * math.log2(probabilidad)

    
    rendimiento = entropia / longitud_media
    redundancia = 1 - rendimiento
    print(f"Rendimiento: {rendimiento:.4f}")
    print(f"Rendundancia: {redundancia:.4f}")
    
def compressAndSave(original_path, compressed_path, longitud_palabra):
    start_time = time.time()
    alfabeto_dict = {} # Mapa de símbolo a frecuencia
    chunk_size = longitud_palabra * 500000 # leer de a 500kb
    total_symbols = 0

    with open(original_path, 'rb') as file:
       while True:
           chunk = file.read(chunk_size)
           if not chunk:
               break
           alfabeto_dict = obtener_alfabeto_frecuencias(chunk, alfabeto_dict, longitud_palabra)
           total_symbols += len(chunk) #para calcular la cant de simbolos por cada chunk leido 

    # Primer paso Huffman
    heap = [[freq, [symbol]] for symbol, freq in alfabeto_dict.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        low1 = heapq.heappop(heap)
        low2 = heapq.heappop(heap)

        new_node = [low1[0] + low2[0], low1[1] + low2[1]]
        heapq.heappush(heap, new_node)

    huffman_tree = heap[0][1]
    # Paso 4: Generar los códigos de Huffman
    huffman_dict = {}
    def generate_codes(tree, prefix=[]):
        if len(tree) == 1:
            symbol = tree[0]
            huffman_dict[symbol] = prefix
        else:
            left = tree[:len(tree) // 2]
            right = tree[len(tree) // 2:]
            generate_codes(left, prefix + [0])
            generate_codes(right, prefix + [1])

    generate_codes(huffman_tree)
    symbols = list(huffman_dict.keys())
    codes = [huffman_dict[symbol] for symbol in symbols]

    with open(compressed_path, "wb") as file:
        file.write(struct.pack('>I', len(alfabeto_dict)))  # Tamaño del alfabeto
        for symbol in symbols:
            file.write(struct.pack('B', len(symbol)))
        for symbol in symbols:
            file.write(symbol)  # Escribe cada símbolo

        # Escribe las longitudes de los códigos
        for code in codes:
            file.write(struct.pack('B', len(code)))  # Longitud del código

        codes_bits_list = [ bit for bits in codes for bit in bits]
        codes_bytes = bytes(codes_bits_list)

        codes_bytes = []
        byte = 0
        bit_count = 0
        for bit in codes_bits_list:
            byte = (byte << 1) | bit
            bit_count += 1
            if bit_count == 8:
                codes_bytes.append(byte)
                byte = 0
                bit_count = 0
        if bit_count > 0:
            padding = 8 - bit_count
            file.write(struct.pack('B', padding))
            byte = byte << padding
            codes_bytes.append(byte)
        else:
            file.write(struct.pack('B', 0))
        for byte in codes_bytes:
            file.write(struct.pack('B', byte))

        padding_index = file.tell()
        file.write(struct.pack('B', 0)) # Guardo un byte inicializado en 0 para el padding

        byte = 0
        bit_count = 0
        with open(original_path, "rb") as original_file:
            while True:
                current_data = original_file.read(chunk_size)
                if not current_data:
                    break
                words = [current_data[i:i + longitud_palabra] for i in range(0, len(current_data), longitud_palabra)]
                for caracter in words:
                    binary_array = huffman_dict[caracter]
                    for bit in binary_array:
                        byte = (byte << 1) | bit 
                        bit_count += 1
                        if bit_count == 8:
                            file.write(struct.pack('<B', byte))
                            byte = 0
                            bit_count = 0

        if bit_count > 0:
            byte = byte << (8 - bit_count)  # Padding
            file.write(struct.pack('B', byte))
            file.seek(padding_index)
            file.write(struct.pack('B', 8 - bit_count))

    end_time = time.time()  
    elapsed_time = end_time - start_time  
    print(f"Tiempo de compresión: {elapsed_time:.6f} segundos")

    calcular_tasa_compresion(original_path,compressed_path)
    calcular_rendimientos(codes, [alfabeto_dict[symbol] for symbol in symbols], total_symbols)


def decompressAndSave(compressed_path, original_path):
    start_time = time.time()

    with open(compressed_path, 'rb') as file:
        # para obtener el alfabeto
        alfabeto_length = struct.unpack('>I', file.read(4))[0]  # obtine la long del alfabeto, el primer byte y lo tranforma en entero
        longitudes_alfabeto = [file.read(1)[0] for _ in range(alfabeto_length)]
        alfabeto = [file.read(long) for long in longitudes_alfabeto]  #se guarda en una lista en formato utf-8
        
        # Lee las longitudes del codigo de huffman
        longitudes_codigo = [file.read(1)[0] for _ in range(alfabeto_length)]
        # TODO: No guardar ese padding (no hace falta)
        codigo_padding = file.read(1)[0]
        total_bits = sum(longitudes_codigo)
        total_bytes = math.ceil(total_bits / 8.0)
        codes_bytes = file.read(total_bytes)
        red_code_bytes = 0
        code_index = 0
        current_code = ""
        codigos = []
        for byte in codes_bytes:
            for i in range(8):
                bit = (byte >> (8 - i - 1)) & 1
                current_code += str(bit)
                red_code_bytes += 1
                if red_code_bytes == longitudes_codigo[code_index]:
                    codigos.append(current_code)
                    red_code_bytes = 0
                    current_code = ""
                    code_index += 1
                if code_index == len(longitudes_codigo):
                    break
            if code_index == len(longitudes_codigo):
                    break
        
         # mapea cada codigo de huffman a cada simbolo para despues ir decodificando
        huffman_dict = {}
        for i in range(len(alfabeto)):
            huffman_dict[codigos[i]] = alfabeto[i]

        padding = file.read(1)[0]

        current_index = file.tell()
        file.seek(0, 2)
        last_byte_index = file.tell()
        file.seek(current_index)
        original = open(original_path, 'wb')
        redByte = file.read(1)
        current_byte_index = file.tell()
        current_code = ''
        while redByte:
            byte = struct.unpack('>B', redByte)[0]
            if current_byte_index == last_byte_index:
                range_size = 8 - padding
            else:
                range_size = 8
            for i in range(range_size):
                bit = (byte >> (8 - i - 1)) & 1
                current_code += str(bit)
                if current_code in huffman_dict:
                    original.write(huffman_dict[current_code])
                    current_code = ''
            redByte = file.read(1)
            current_byte_index += 1
            
    original.close()

    end_time = time.time()
    elapsed_time = end_time - start_time  
    print(f"Tiempo de descompresión: {elapsed_time:.6f} segundos")




if len(sys.argv) < 4:
   print("Hacen falta argumentos")
   print("tpi3 {-c|-d} original compressed")
   sys.exit(1)

longitud_palabra = 1 # Longitud de la palabra en bytes

original_path = sys.argv[2]
compressed_path = sys.argv[3]

compress = sys.argv[1] == "-c"

print("longitud palabra:", longitud_palabra)
print("original path:", original_path)
print("compressed path:", compressed_path)

if(compress):
    compressAndSave(original_path, compressed_path, longitud_palabra)
else:
    decompressAndSave(compressed_path, original_path)