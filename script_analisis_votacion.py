import csv

def generate_resultados_centros(votacion_centros):
  
  file_centros = open('analisis_de_resultados/lista_centros_votacion.txt', 'w')

  for centro in votacion_centros:
    file_centros.write('centro:' + centro +' cantidad de votantes:' + str(votacion_centros[centro]) + '\n')

  file_centros.close()

def parse_resultado_votantes(output_file):
    
    result_centros = {}
    
    with open('analisis_de_resultados/analisis_de_votantes_por_centro.csv', 'w', newline='') as f_lista:  
      wr = csv.writer(f_lista, delimiter=';')
      wr.writerow(['id_votante', 'id_centro'])
      with open(output_file) as resultado_votacion:
        reader = csv.reader(resultado_votacion, delimiter=';')

        for row in reader:
          data_votante = row[1].split(',')

          id_votante = data_votante[0].split('[')
          id_votante = id_votante[1]

          id_centro = data_votante[1].split(']')
          id_centro = id_centro[0]

          bivalente = row[2]

          if bivalente == '1':
            wr.writerow([id_votante, id_centro])
            if not id_centro in result_centros:
              result_centros[id_centro] = 1
            else:
              result_centros[id_centro] += 1
      return result_centros

votantes_procesados = 'resultados_filtrados/resultado_votantes.csv'
result = parse_resultado_votantes(votantes_procesados)
generate_resultados_centros(result)