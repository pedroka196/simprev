# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""

from util.dados import get_id_beneficios, get_tabelas, ids_pop_ibge, ids_pop_pnad, ids_salarios, corrige_erros_estoque
from modelos.fazenda.probabilidades import calc_probabilidades
from modelos.fazenda.demografia import calc_demografia
from modelos.fazenda.taxas import calc_taxas
from modelos.fazenda.estoques import calc_estoques
import pandas as pd

# Não usado pode enquanto
def main():
    pass

#  Sò queremos que nossa função main() seja executada se o módulo for
# o principal. Caso ele tenha sido importado, a aplicação só deverá ser 
# executada se main() for chamado explicitamente.
if __name__ == "__main__":
    main()

###### Parâmetros de simulação

# Período de projeção
periodo = list(range(2015,2061))


print('--- Iniciando projeção --- \n')
print('Lendo arquivo de dados ... \n')
# Arquivo com os dados da Fazenda
arquivo = '../datasets/FAZENDA/dados_fazenda.xlsx'
# Abri o arquivo
dados = pd.ExcelFile(arquivo)


print('Carregando tabelas ...\n')
# Dicionários que armazenarão os dados de estoques, concessões, etc.
estoques = get_tabelas(get_id_beneficios([], 'Es'), dados, info=True)
concessoes = get_tabelas(get_id_beneficios([], 'Co'), dados, info=True)
cessacoes = get_tabelas(get_id_beneficios([], 'Ce'), dados, info=True)
populacao = get_tabelas(ids_pop_ibge, dados)
populacao_pnad = get_tabelas(ids_pop_pnad, dados)
salarios = get_tabelas(ids_salarios, dados)

# Calcula taxas de urbanização, participação e ocupação
print('Calculando taxas ...\n')
taxas = calc_taxas(populacao_pnad)

# Calcula: Pop Urbana|Rural, PEA e Pop Ocupada, 
# Contribuintes, Segurados
print('Calculando dados demográficos ...\n')
segurados = calc_demografia(populacao, taxas)

# Corrige inconsistências nos estoques
corrige_erros_estoque(estoques, concessoes, cessacoes)

# Calcula as probabilidades de entrada em benefício e morte
print('Calculando probabilidades ...\n')
probabilidades = calc_probabilidades(populacao, segurados, estoques, 
                                     concessoes, cessacoes, periodo)

# Projeta Estoques
print('Projetando Estoques ...\n')
estoques = calc_estoques(estoques, probabilidades, populacao, segurados, periodo)


# Comparar os segurados calculados com os segurados das planilhas