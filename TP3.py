import sys
import time
import struct


# Python program for implementation of Quicksort Sort

# This implementation utilizes pivot as the last element in the nums list
# It has a pointer to keep track of the elements smaller than the pivot
# At the very end of partition() function, the pointer is swapped with the pivot
# to come up with a "sorted" nums relative to the pivot


# Function to find the partition position
def partition(array, low, high, parallel_arrays):

    # choose the rightmost element as pivot
    pivot = array[high]

    # pointer for greater element
    i = low - 1

    # traverse through all elements
    # compare each element with pivot
    for j in range(low, high):
        if array[j] > pivot:

            # If element smaller than pivot is found
            # swap it with the greater element pointed by i
            i += 1

            # Swapping element at i with element at j
            (array[i], array[j]) = (array[j], array[i])
            for parallel_array in parallel_arrays:
                (parallel_array[i], parallel_array[j]) = (parallel_array[j], parallel_array[i])

    # Swap the pivot element with the greater element specified by i
    (array[i + 1], array[high]) = (array[high], array[i + 1])
    for parallel_array in parallel_arrays:
        (parallel_array[i + 1], parallel_array[high]) = (parallel_array[high], parallel_array[i + 1])

    # Return the position from where partition is done
    return i + 1

# function to perform quicksort


def quickSortDescendingParallel(array, low, high, parallel_arrays):
    if low < high:

        # Find pivot element such that
        # element smaller than pivot are on the left
        # element greater than pivot are on the right
        pi = partition(array, low, high, parallel_arrays)

        # Recursive call on the left of pivot
        quickSortDescendingParallel(array, low, pi - 1, parallel_arrays)

        # Recursive call on the right of pivot
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
def obtener_alfabeto_probabilidades(content):
    alfabeto = list(set(content))  # Obtener los símbolos únicos
    conteos = Counter(content)     # Contar las ocurrencias de cada símbolo
    total_simbolos = len(content)  # Longitud del contenido 
    
    # Calcular las probabilidades
    probabilidades = [conteos[symbol] / total_simbolos for symbol in alfabeto]
    
    return alfabeto, probabilidades

    
def compressAndSave(original_path, compressed_path, longitud_palabra):
    start_time = time.time()
    alfabeto = []
    probabilidades = []
    chunk_size = 500000 # leer de a 500kb

    with open(original_path, 'rb') as file:
       while True:
           chunk = file.read(chunk_size)
           if not chunk:
               break
           # Update alphabet and probabilities from the chunk
           alfabeto_chunk, probabilidades_chunk = obtener_alfabeto_probabilidades(chunk)
           # Combine with the rest
           for caracter in alfabeto_chunk:
                if caracter in alfabeto:
                   index = alfabeto.index(caracter)
                   chunk_index = alfabeto_chunk.index(caracter)
                   probabilidades[index] += probabilidades_chunk[chunk_index]
                else:
                   alfabeto.append(caracter)
                   index = alfabeto_chunk.index(caracter)
                   probabilidades.append(probabilidades_chunk[index])

    print(alfabeto)
    print(probabilidades)

    # Primer paso Huffman
    quickSortDescendingParallel(probabilidades, 0, len(probabilidades) - 1, [alfabeto])

    main_arr = probabilidades.copy()
    num_arr = probabilidades.copy()

    while len(main_arr) > 2:
        aux = main_arr[len(main_arr) - 2:]
        num_arr = [*num_arr[:len(num_arr) - 2], list_recursive_sum(aux)]
        main_arr = [*main_arr[:len(main_arr) - 2], aux]
        quickSortDescendingParallel(num_arr, 0, len(num_arr) - 1, [main_arr])

    codigo = [[0], [1]] # Almacenar de forma óptima los bytes
    while len(main_arr) < len(probabilidades):
        i = len(main_arr) - 1
        while i >= 0 and type(main_arr[i]) is not list:
            i -= 1
        if i >= 0:
            main_arr = [*main_arr[:i], *main_arr[i], *main_arr[i+1:]]
            num_arr = list(map(list_recursive_sum_type_safe, main_arr))
            codigo = [*codigo[:i], [*codigo[i], 0], [*codigo[i], 1], *codigo[i+1:]]
            
    print("Códigos generados:")
    print(codigo)  
    print("alfabeto", alfabeto, probabilidades)  
    print("longitud alfabeto", len(alfabeto))


 # Crea un diccionario de Huffman con cada codigo
    huffman_dict = {alfabeto[i]: codigo[i] for i in range(len(alfabeto))}

    with open(compressed_path, "wb") as file:
        file.write(struct.pack('I', len(alfabeto)))  # Tamaño del alfabeto
        for symbol in alfabeto:
            file.write(bytes([symbol]))  # Escribe cada símbolo

        # Escribe las longitudes de los códigos
        for symbol in alfabeto:
            code = huffman_dict[symbol]
            file.write(struct.pack('B', len(code)))  # Longitud del código

        for symbol in alfabeto:
            code = huffman_dict[symbol]
            for bit in code:
                file.write(struct.pack('B', bit))

        padding_index = file.tell()
        file.write(struct.pack('B', 0)) # Guardo un byte inicializado en 0 para el padding

        byte = 0
        bit_count = 0
        with open(original_path, "rb") as original_file:
            while True:
                current_data = original_file.read(chunk_size)
                if not current_data:
                    break
                for caracter in current_data:
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

def decompressAndSave(compressed_path, original_path):
    start_time = time.time()

    print("Descomprimir y recuperar original")
    with open(compressed_path, 'rb') as file:
        # para obtener el alfabeto
        alfabeto_length = struct.unpack('<i', file.read(4))[0]  # obtine la long del alfabeto, el primer byte y lo tranforma en entero
        print("longitud alfabeto", alfabeto_length)
        alfabeto = [file.read(1) for _ in range(alfabeto_length)]  #se guarda en una lista en formato utf-8
        
        # Lee las longitudes del codigo de huffman
        longitudes_codigo = [file.read(1)[0] for _ in range(alfabeto_length)]
        
        # Lee los códigos binarios de cada simbolo
        codigo = []
        for longitud in longitudes_codigo:
            codigo.append([file.read(1) for _ in range(longitud)])  # Leer los bits como 1 o 0
        padding = struct.unpack('B', file.read(1))[0]

         # mapea cada codigo de huffman a cada simbolo para despues ir decodificando
        huffman_dict = {}
        for i in range(len(alfabeto)):
            bits_string = ''.join(map(lambda byte: bin(int.from_bytes(byte, byteorder='big'))[2:], codigo[i]))
            huffman_dict[bits_string] = alfabeto[i]

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

longitud_palabra = 16 # Longitud de la palabra en bytes

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