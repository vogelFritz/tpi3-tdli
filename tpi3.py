import sys


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
    
def compressAndSave(original_path, compressed_path, longitud_palabra):
    # Abrir en binario
    with open(original_path, 'rb') as file:
        content = file.read()
    print(type(content))
    # TODO: Obtener alfabeto y probabilidades

    alfabeto = ['b', 'a', 'c']
    probabilidades = [2.0, 3.0, 1.0]

    # Primer paso Huffman
    quickSortDescendingParallel(probabilidades, 0, len(probabilidades) - 1, [alfabeto])

    main_arr = probabilidades
    num_arr = probabilidades

    while len(main_arr) > 2:
        aux = main_arr[len(main_arr) - 2:]
        num_arr = [*num_arr[:len(num_arr) - 2], list_recursive_sum(aux)]
        main_arr = [*main_arr[:len(main_arr) - 2], aux]
        quickSortDescendingParallel(num_arr, 0, len(num_arr) - 1, [main_arr])
        print(num_arr)
        print(main_arr)

    codigo = [[0], [1]] # Almacenar de forma óptima los bytes
    while len(main_arr) < len(probabilidades):
        i = len(main_arr) - 1
        while i >= 0 and type(main_arr[i]) is not list:
            i -= 1
        if i >= 0:
            main_arr = [*main_arr[:i], *main_arr[i], *main_arr[i+1:]]
            num_arr = list(map(list_recursive_sum_type_safe, main_arr))
            codigo = [*codigo[:i], [*codigo[i], 0], [*codigo[i], 1], *codigo[i+1:]]
            print(codigo)
            quickSortDescendingParallel(num_arr, 0, len(num_arr) - 1, [main_arr, codigo]) # Quizás este ordenamiento no hace falta

    print("codigo, probabilidades y alfabeto")
    print(codigo)
    print(num_arr)
    print(alfabeto)

    # TODO: Guardar archivo comprimido

    # TODO: Lo de abajo es INCORRECTO, solo es una idea para el formato del archivo (tabla al comienzo del archivo)
    # Los unos y los ceros hay que guardarlos como bits y no en formato de int, si no no se comprime nada
    with open(compressed_path, "rwb") as file:
        file.write(len(alfabeto))
        for car in alfabeto:
            file.write(car)
        for arr in codigo:
            file.write(len(arr)) # Longitudes de las palabras código
        for arr in codigo:
            for num in arr: # num es 1 o 0
                file.write(num) # Digitos de la palabra código
        


def decompressAndSave(compressed_path, original_path):
    print("Descomprimir y recuperar original")




if len(sys.argv) < 4:
    print("Hacen falta argumentos")
    print("tpi3 {-c|-d} original compressed")
    sys.exit(1)

longitud_palabra = 16 # Longitud de la palabra en bytes

original_path = sys.argv[2]
compressed_path = sys.argv[3]

compress = sys.argv[1] == "-c"
print(compress)

print("longitud palabra:", longitud_palabra)
print("original path:", original_path)
print("compressed path:", compressed_path)


if(compress):
    compressAndSave(original_path, compressed_path, longitud_palabra)
else:
    decompressAndSave(compressed_path, original_path)