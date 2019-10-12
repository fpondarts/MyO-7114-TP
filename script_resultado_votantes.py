def format_resultados_centros(votacion_centros):
  
  file_centros = open('lista_centros_votacion.txt', 'w')

  for centro in votacion_centros:
    file_centros.write('centro:' + centro +' cantidad de votantes:' + str(votacion_centros[centro]) + '\n')

  file_centros.close()

def parse_resultado_votantes(output_file):
    result_centros = {}
    data = [line.rstrip('\n') for line in open(output_file)]
    
    file_votantes = open('lista_votantes_por_centro.txt', 'w')

    for vot in data:
        split_data = vot.split(',')
        
        data_votante = split_data[1].split('[')
        id_votante = data_votante[1]
        
        data_centro = split_data[2].split(']')
        id_centro = data_centro[0]

        bivalente_votante = split_data[3]

        if bivalente_votante == '1':
          file_votantes.write('id_votante:' + id_votante + '  voto en el centro:' + id_centro + '\n')
          if not id_centro in result_centros:
            result_centros[id_centro] = 1
          else:
            result_centros[id_centro] += 1
            #{'id_votante':id_votante, 'voto':bivalente_votante, ' en el centro':id_centro}
    file_votantes.close()
    return result_centros


votantes_procesados = 'votantes_procesados.csv'
result = parse_resultado_votantes(votantes_procesados)
format_resultados_centros(result)