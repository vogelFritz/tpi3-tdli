# Trabajo Práctico Integrador Nº3

Desarrollar un programa que pueda ser ejecutado por consola del siguiente modo:

tpi3 {-c|-d} original compressed

Donde:

- tpi3 es el programa ejecutable
- -c y -d son flags que indican la acción a realizar
- original y compressed son archivos

El programa debe realizar las siguientes acciones:

1. Si se incluye el flag -c, realizar una compresión sin pérdidas del archivo original y almacenarla en el archivo compressed.
2. Si se incluye el flag -d, descomprimir el archivo compressed obtenido en el inciso anterior y recuperar el archivo original.
3. Informar el tiempo que ha demorado en realizar la acción solicitada.
4. Calcular la tasa de compresión, el rendimiento y la redundancia.

## Cosas a tener en cuenta

- Se lee el archivo en formato de bits.

- Hay que decidir qué es considerado una palabra. Se puede elegir una longitud de palabra (longitudes más grandes en teoría ayudan a una mejor compresión).

- Se puede elegir entre el algoritmo de Huffman y el de Shannon-Fano (RLC no sirve mucho). También se pueden investigar otras opciones.

- Incluir la tabla de código y probabilidades en el archivo (si no no se puede descomprimir).
