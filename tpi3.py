import sys

if len(sys.argv) < 4:
    print("Hacen falta argumentos")
    print("tpi3 {-c|-d} original compressed")
    sys.exit(1)

longitud_palabra = 16 # Longitud de la palabra en bytes

original_path = sys.argv[2]
compressed_path = sys.argv[3]

print("longitud palabra:", longitud_palabra)
print("original path:", original_path)
print("compressed path:", compressed_path)

# Abrir en binario
with open(original_path, 'rb') as file:
    content = file.read()

