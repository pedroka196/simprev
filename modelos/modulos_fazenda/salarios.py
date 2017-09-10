# -*- coding: utf-8 -*-
"""
@author: Patrick Alves
"""
import pandas as pd


# Calcula rendimentos médios 
def calc_salarios(salarios, populacao, segurados, produtividade, 
                  salMinInicial, dadosLDO, tetoInicialRGPS, periodo):
     
    ##### Projeta crescimento do Salário Mínimo #####
    
    # último ano do estoque (2014)    
    ano_inicial = periodo[0]-1

    # Objeto do tipo Serie que armazena o Salario Minimo
    salarioMinimo =  pd.Series(index=[ano_inicial])

    # Inicializa com o valor conhecido
    salarioMinimo[ano_inicial] = salMinInicial
    
    # Projeta crescimento do Salário Mínimo (Eq. 36)
    for txCres in dadosLDO['TxCrescimentoSalMin']:
        ano_inicial += 1
        salarioMinimo[ano_inicial] = salarioMinimo[ano_inicial-1] * (1 + txCres/100) 

    # Salva a Serie no dicionário
    salarios['salarioMinimo']  = salarioMinimo  
    
    
    ##### Projeta crescimento do Teto do RGPS #####
    
    # Objeto do tipo Serie que armazena o teto
    ano_inicial = periodo[0]-1                              # 2014
    ano_final = ano_inicial + len(tetoInicialRGPS)          # 2018
    # Salva os valores conhecidos de Teto de 2014 a 2017    
    teto = pd.Series(tetoInicialRGPS, index=range(ano_inicial, ano_final))
    
    for ano in range(ano_final, (periodo[-1]+1)):           # 2018-2060        
        inflacao = dadosLDO['TxInflacao'][ano]              # em %
        teto[ano] = teto[ano-1] * (1 + inflacao/100) 

    # Salva a Serie no dicionário
    salarios['tetoRGPS'] = teto
    
        
    ###### Projeta crescimento dos salários da Pop. Ocupada a partir dos 
    # dados da Pnad e da produtividade (Eq 32)
    # A equação original não considera Inflação, mas é necessário adicionar pois a inflação 
    # é considerada no cálculo dos valores dos benefícios
    
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:
            id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
            
            for ano in periodo:                
                # Atualização monetária utilizada para os anos de 2015-2017 de acordo com as Planilhas do MF            
                atualizMonet = 1
            
                if ano == 2015:
                    atualizMonet = 1.0641
                elif ano == 2016:
                    atualizMonet = 1.1067
                elif ano == 2017:
                    atualizMonet = 1.0629
                
                inflacao = dadosLDO['TxInflacao'][ano]
                # Produtivididade 1.7% a partir de 2016
                prod = produtividade if ano > 2015 else 0
                salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + prod/100 + inflacao/100) * atualizMonet             
    
                
    ###### Projeta crescimento dos salários dos Segurados acima do SM a partir da produtividade (Eq. 37)
    # A equação original não considera Inflação, mas é necessário adicionar pois a inflação 
    # é considerada no cálculo dos valores dos benefícios     
    for sexo in ['H', 'M']:
        id_sal = 'SalMedSegUrbAcimPnad' + sexo
                
        # Reajusta os anos (2015-20160)
        for ano in periodo:    
            # Atualização monetária utilizada para os anos de 2015-2017 de acordo com as Planilhas do MF            
            atualizMonet = 1
        
            if ano == 2015:
                atualizMonet = 1.0641
            elif ano == 2016:
                atualizMonet = 1.1067
            elif ano == 2017:
                atualizMonet = 1.0629
            
            inflacao = dadosLDO['TxInflacao'][ano]
            # Produtivididade 1.7% a partir de 2016
            prod = produtividade if ano > 2015 else 0
            salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + prod/100 + inflacao/100) * atualizMonet            
            
    
    ###### Projeta crescimento dos salários da Pop. Ocupada que recebe acima do piso
    # a partir da Pnad e da produtividade
    # REVISAR: Esses valores são utilizados na Eq. 45, porém acredito que deveriam
    # Ser utilizados os segurados e náo a PopOcup
    for sexo in ['H', 'M']:
        id_sal = 'SalMedPopOcupUrbAcimPnad' + sexo
            
        for ano in periodo:
            # Atualização monetária utilizada para os anos de 2015-2017 de acordo com as Planilhas do MF            
            atualizMonet = 1
        
            if ano == 2015:
                atualizMonet = 1.0641
            elif ano == 2016:
                atualizMonet = 1.1067
            elif ano == 2017:
                atualizMonet = 1.0629
            
            inflacao = dadosLDO['TxInflacao'][ano]
            # Produtivididade 1.7% a partir de 2016
            prod = produtividade if ano > 2015 else 0
            salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + prod/100 + inflacao/100) * atualizMonet                   
         
            
    return salarios


# Calcula Massa Salarial
def calc_MassaSalarial(salarios, populacao, segurados, produtividade, 
                  salMinInicial, dadosLDO, tetoInicialRGPS, periodo):

    
    ###### Projeta Massa Salarial para Pop. Ocupada (Eq. 33)
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:            
            id_msal = 'MSalPopOcup' + clientela + sexo
            id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
            id_pocup = 'Ocup' + clientela + sexo
            salarios[id_msal] = salarios[id_sal] * populacao[id_pocup]

           
    ###### Projeta Massa Salarial para Contribuintes Urbanos que recebem o SM (Eq. 34)
    for sexo in ['H', 'M']:            
        id_contrib = 'CsmUrb' + sexo
        id_msal = 'MSal' + id_contrib
        # Multiplica SM do ano correspondente pela quantidade de trabalhadores em cada idade        
        salarios[id_msal] = salarios['salarioMinimo'] * segurados[id_contrib]
        # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
            
    
    ###### Projeta Massa Salarial para Contribuintes que recebem acima do SM (Eq. 35)
    for sexo in ['H', 'M']:            
        id_contrib = 'CaUrb' + sexo
        id_msal = 'MSal' + id_contrib
        id_sal = 'SalMedSegUrbAcimPnad'+ sexo
        teto = salarios["tetoRGPS"]
                
        # Limita o salário de contribuição pelo teto
        salContr = salarios[id_sal].copy()               # faz uma cópia do objeto que armazenas os salários
        for ano in teto.index:            # para cada ano  
            for idade in salContr[ano].index:            # para cada idade
                if salContr[ano][idade] > teto[ano]:
                    salContr[ano][idade] = teto[ano]
        
        salarios[id_msal] = salContr * segurados[id_contrib]
         # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
                
        
    return salarios


# Calcula rendimentos médios - OBS: não utilizado
def calc_salarios_bkp(salarios, populacao, segurados, produtividade, 
                  salMinInicial, dadosLDO, tetoInicialRGPS, periodo):
     
    ##### Projeta crescimento do Salário Mínimo #####
    
    # último ano do estoque (2014)    
    ano_inicial = periodo[0]-1

    # Objeto do tipo Serie que armazena o Salario Minimo
    salarioMinimo =  pd.Series(index=[ano_inicial])

    # Inicializa com o valor conhecido
    salarioMinimo[ano_inicial] = salMinInicial
    
    # Projeta crescimento do Salário Mínimo (Eq. 36)
    for txCres in dadosLDO['TxCrescimentoSalMin']:
        ano_inicial += 1
        salarioMinimo[ano_inicial] = salarioMinimo[ano_inicial-1] * (1 + txCres/100) 

    # Salva a Serie no dicionário
    salarios['salarioMinimo']  = salarioMinimo  
    
    
    ##### Projeta crescimento do Teto do RGPS #####
    
    # Objeto do tipo Serie que armazena o teto
    ano_inicial = periodo[0]-1                              # 2014
    ano_final = ano_inicial + len(tetoInicialRGPS)          # 2018
    # Salva os valores conhecidos de Teto de 2014 a 2017    
    teto = pd.Series(tetoInicialRGPS, index=range(ano_inicial, ano_final))
    
    for ano in range(ano_final, (periodo[-1]+1)):           # 2018-2060        
        inflacao = dadosLDO['TxInflacao'][ano]              # em %
        teto[ano] = teto[ano-1] * (1 + inflacao/100) 

    # Salva a Serie no dicionário
    salarios['tetoRGPS'] = teto
    
        
    ###### Projeta crescimento dos salários da Pop. Ocupada a partir dos 
    # dados da Pnad e da produtividade (Eq 32)
    # A equação original não considera Inflação, mas é necessário adicionar pois a inflação 
    # é considerada no cálculo dos valores dos benefícios
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:
            for ano in periodo:
                id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
                inflacao = dadosLDO['TxInflacao'][ano]
                salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100 + inflacao/100)             
    
                
    ###### Projeta crescimento dos salários dos Segurados acima do SM a partir da produtividade (Eq. 37)
    # A equação original não considera Inflação, mas é necessário adicionar pois a inflação 
    # é considerada no cálculo dos valores dos benefícios
    for sexo in ['H', 'M']:
        id_sal = 'SalMedSegUrbAcimPnad' + sexo
        
        # Suavização para o ano de 2014 - Utilizado nas Planilhas do MF
        if periodo[0]-1 == 2014:
            suavizacao = 1.0641
            salarios[id_sal][2014] = salarios[id_sal][2014] * suavizacao
        
        # Reajusta os demais anos (2015-20160)
        for ano in periodo:    
            # Atualização monetária utilizada para os anos de 2015-2017 de acordo com as Planilhas do MF            
            atualizMonet = 1
        
            if ano == 2015:
                atualizMonet = 1.0641
            elif ano == 2016:
                atualizMonet = 1.1067
            elif ano == 2017:
                atualizMonet = 1.0629
            
            inflacao = dadosLDO['TxInflacao'][ano]
            salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100 + inflacao/100)             
    
    
    ###### Projeta crescimento dos salários da Pop. Ocupada que recebe acima do piso
    # a partir da Pnad e da produtividade
    # REVISAR: Esses valores são utilizados na Eq. 45, porém acredito que deveriam
    # Ser utilizados os segurados e náo a PopOcup
    for sexo in ['H', 'M']:
        for ano in periodo:
            id_sal = 'SalMedPopOcupUrbAcimPnad' + sexo
            inflacao = dadosLDO['TxInflacao'][ano]
            salarios[id_sal][ano] = salarios[id_sal][ano-1] * (1 + produtividade/100 + inflacao/100)                    
     
            
    ###### Projeta Massa Salarial para Pop. Ocupada (Eq. 33)
    for clientela in ['Urb', 'Rur']:
        for sexo in ['H', 'M']:            
            id_msal = 'MSalPopOcup' + clientela + sexo
            id_sal = 'SalMedPopOcup' + clientela + 'Pnad' + sexo
            id_pocup = 'Ocup' + clientela + sexo
            salarios[id_msal] = salarios[id_sal] * populacao[id_pocup]
                    
    
    ###### Projeta Massa Salarial para Contribuintes Urbanos que recebem o SM (Eq. 34)
    for sexo in ['H', 'M']:            
        id_contrib = 'CsmUrb' + sexo
        id_msal = 'MSal' + id_contrib
        # Multiplica SM do ano correspondente pela quantidade de trabalhadores em cada idade        
        salarios[id_msal] = salarios['salarioMinimo'] * segurados[id_contrib]
        # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
            
    
    ###### Projeta Massa Salarial para Contribuintes que recebem acima do SM (Eq. 35)
    for sexo in ['H', 'M']:            
        id_contrib = 'CaUrb' + sexo
        id_msal = 'MSal' + id_contrib
        id_sal = 'SalMedSegUrbAcimPnad'+ sexo
                
        # Limita o salário de contribuição pelo teto
        salContr = salarios[id_sal].copy()               # faz uma cópia do objeto que armazenas os salários
        for ano in teto.index:                           # para cada ano  
            for idade in salContr[ano].index:            # para cada idade
                if salContr[ano][idade] > teto[ano]:
                    salContr[ano][idade] = teto[ano]
        
        salarios[id_msal] = salContr * segurados[id_contrib]
         # Elimina colunas vazias
        salarios[id_msal].dropna(how='all', axis=1, inplace=True)  
                
        
    return salarios
        