import math
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
def obtener_alfabeto_frecuencias(content, longitud_palabra):
    chunks = [content[i:i + longitud_palabra] for i in range(0, len(content), longitud_palabra)]

    alfabeto = list(set(chunks))  # Obtener los símbolos únicos
    conteos = Counter(chunks)     # Contar las ocurrencias de cada símbolo
    
    frecuencias = [conteos[symbol] for symbol in alfabeto]
    
    return alfabeto, frecuencias

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
    alfabeto = []
    frecuencias = []
    chunk_size = longitud_palabra * 500000 # leer de a 500kb
    total_symbols = 0

    with open(original_path, 'rb') as file:
       while True:
           chunk = file.read(chunk_size)
           if not chunk:
               break
           alfabeto_chunk, frecuencias_chunk = obtener_alfabeto_frecuencias(chunk, longitud_palabra)
           total_symbols += len(chunk) #para calcular la cant de simbolos por cada chunk leido 

           for caracter in alfabeto_chunk:
                if caracter in alfabeto:
                   index = alfabeto.index(caracter)
                   chunk_index = alfabeto_chunk.index(caracter)
                   frecuencias[index] += frecuencias_chunk[chunk_index]
                else:
                   alfabeto.append(caracter)
                   index = alfabeto_chunk.index(caracter)
                   frecuencias.append(frecuencias_chunk[index])

    print(alfabeto)
    print(frecuencias)

    # Primer paso Huffman
    quickSortDescendingParallel(frecuencias, 0, len(frecuencias) - 1, [alfabeto])

    main_arr = frecuencias.copy()
    num_arr = frecuencias.copy()

    while len(main_arr) > 2:
        aux = main_arr[len(main_arr) - 2:]
        num_arr = [*num_arr[:len(num_arr) - 2], list_recursive_sum(aux)]
        main_arr = [*main_arr[:len(main_arr) - 2], aux]
        quickSortDescendingParallel(num_arr, 0, len(num_arr) - 1, [main_arr])

    codigo = [[0], [1]] # Almacenar de forma óptima los bytes
    while len(main_arr) < len(frecuencias):
        i = len(main_arr) - 1
        while i >= 0 and type(main_arr[i]) is not list:
            i -= 1
        if i >= 0:
            main_arr = [*main_arr[:i], *main_arr[i], *main_arr[i+1:]]
            num_arr = list(map(list_recursive_sum_type_safe, main_arr))
            codigo = [*codigo[:i], [*codigo[i], 0], [*codigo[i], 1], *codigo[i+1:]]
            
    print("Códigos generados:")
    print(codigo)  
    print("alfabeto", alfabeto, frecuencias)  
    print("longitud alfabeto", len(alfabeto))


 # Crea un diccionario de Huffman con cada codigo
    huffman_dict = {bytes(alfabeto[i]): codigo[i] for i in range(len(alfabeto))}

    with open(compressed_path, "wb") as file:
        file.write(struct.pack('>I', len(alfabeto)))  # Tamaño del alfabeto
        for symbol in alfabeto:
            file.write(struct.pack('B', len(symbol)))
        for symbol in alfabeto:
            file.write(symbol)  # Escribe cada símbolo

        # Escribe las longitudes de los códigos
        for symbol in alfabeto:
            code = huffman_dict[symbol]
            file.write(struct.pack('B', len(code)))  # Longitud del código

        codes = [huffman_dict[symbol] for symbol in alfabeto]
        print(codes)
        codes_bits_list = [ bit for bits in codes for bit in bits]
        print(codes_bits_list)
        codes_bytes = bytes(codes_bits_list)

        print(len(codes_bytes))
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
    calcular_rendimientos(codigo,frecuencias,total_symbols)


def decompressAndSave(compressed_path, original_path):
    start_time = time.time()

    print("Descomprimir y recuperar original")
    with open(compressed_path, 'rb') as file:
        # para obtener el alfabeto
        alfabeto_length = struct.unpack('>I', file.read(4))[0]  # obtine la long del alfabeto, el primer byte y lo tranforma en entero
        print("longitud alfabeto", alfabeto_length)
        longitudes_alfabeto = [file.read(1)[0] for _ in range(alfabeto_length)]
        print(longitudes_alfabeto)
        alfabeto = [file.read(long) for long in longitudes_alfabeto]  #se guarda en una lista en formato utf-8
        
        # Lee las longitudes del codigo de huffman
        longitudes_codigo = [file.read(1)[0] for _ in range(alfabeto_length)]
        # TODO: No guardar ese padding (no hace falta)
        codigo_padding = file.read(1)[0]
        print(longitudes_codigo)
        total_bits = sum(longitudes_codigo)
        total_bytes = math.ceil(total_bits / 8.0)
        print("total_bytes", total_bytes)
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
                print(current_code)
                print(codigos)
                if red_code_bytes == longitudes_codigo[code_index]:
                    codigos.append(current_code)
                    red_code_bytes = 0
                    current_code = ""
                    code_index += 1
                if code_index == len(longitudes_codigo):
                    break
            if code_index == len(longitudes_codigo):
                    break
        
        print(codigos)

         # mapea cada codigo de huffman a cada simbolo para despues ir decodificando
        huffman_dict = {}
        for i in range(len(alfabeto)):
            huffman_dict[codigos[i]] = alfabeto[i]

        print("huffman_dict:")
        print(huffman_dict)
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

def leerArchivoBinarioEnHex(ruta_archivo):
    with open(ruta_archivo, 'rb') as file:
        contenido = file.read()
        
        hex_output = contenido.hex()
        print("Contenido del archivo comprimido en hexadecimal:")
        print(hex_output)


#leerArchivoBinarioEnHex(compressed_path)

if(compress):
    compressAndSave(original_path, compressed_path, longitud_palabra)
else:
    decompressAndSave(compressed_path, original_path)