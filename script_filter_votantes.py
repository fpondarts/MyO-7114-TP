import csv
import re

def filter_resultados_votantes(input_file):
    f_in = open(input_file, "r")
    #f_out = open('resultados_filtrados/resultados_votantes.txt', 'w')
    with open('resultados_filtrados/resultado_votantes.csv', 'w', newline='') as myfile:
        wr = csv.writer(myfile, delimiter=';')
        for line in f_in:
            if "y[" in line:
                filter_line = re.sub(' +', ' ', filter_info(line))
                #print(filter_line)
                split_line = filter_line.split()
                wr.writerow([split_line[0], split_line[1], split_line[2]])
                #f_out.write(filter_line + '\n')
    ##f_out.close()
    f_in.close()

def filter_info(line):
    split_line = line.split('*')
    
    votante = split_line[0]
    info_voto = split_line[1]
    
    #split_info_voto = info_voto.split(' ')
    votante = " ".join(votante.split())
    info_voto = " ".join(info_voto.split())
    split_info_voto = info_voto.split(' ')

    return votante + ' ' +split_info_voto[0]


file_sol = 'tp.sol'
filter_resultados_votantes(file_sol)