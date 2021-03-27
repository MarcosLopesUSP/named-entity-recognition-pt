
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:57:50 2021

@author: andressa  #M: Nome completo aqui
"""

### Comentários gerais do Marcos - 27/3/21 ###
# Vai ser preciso padronizar a redação para publicar. Isso vale para este módulo e para os outros:
# - Vamos usar aspas simples, ok?
# - Nomes de variáveis e constantes: escolha se você quer em inglês ou português e mantenha a língua.
# - Vale a pena escrever comentários e docstrings. Vai ser preciso escolher inglês ou português para isso, também. 
# - Fiquei um pouco confuso com as alternâncias no código entre tantas maiúsculas e minúsculas. Muitos upper() e lower(). 
# --- Não dava para converter tudo de uma vez no início?
# --- Já as etiquetas poderiam ficar direto em maiúsculas e abreviadas (PES, ORG...), como é padrão nas tarefas de classificação.


from listas import get_classifiers


AGNOMES = ('jr', 'junior', 'primeiro', 'segundo', 'I', 'II', 'filho', 'neto')
EMPRESAS = ('ltda', 'sa', 'me', 'mei', 'epp', 'eireli')


def ort_lex_features(ne):
    last_en_token = ne[-1]
    
    if "&" in ne:
        return 'organização'
    if last_en_token in EMPRESAS:
        return 'organização'
    if last_en_token in AGNOMES:
        return 'pessoa'

    return 'O'

  
def match_contexts(first_index, last_index, sentence, scenario): 
    first_en_token = sentence[first_index].lower() 
    prevWord = sentence[first_index-1].lower() if first_index-1 > 0 else 'NONE'
    ne = ' '.join(sentence[first_index:last_index])
    
    if scenario == 'total':
        classifiers = get_classifiers()
    elif scenario == 'selective': #M: Por que tem um elif se não termina em else?
        classifiers = get_classifiers(lists_names=['parentesco', 'pronome', 'profissão',
                                       'estabelecimento', 'geomorfologia', 'logradouro'])
        
    for cat, dic  in classifiers.items():
        clas, subclas = cat.split('|')
        if prevWord in dic['singular'] or first_en_token in dic['singular']:
            return clas, 'sg'
        elif prevWord in dic['plural'] or first_en_token in dic['plural']:
            return clas, 'pl'
    
    ort_lex_feat = ort_lex_features(ne)
    
    if ort_lex_feat != 'O':
        return ort_lex_feat, 'ort'
    
    return 'O', None
                

def is_sequence(document, prev_index, doc_entities):
    sequence = 0
    e_bool = False
    
    for first_index, last_index in doc_entities:
        if first_index == prev_index + 1:
            if document[prev_index] == 'e':
                e_bool = True
                sequence += 1
                break    
            elif document[prev_index] == ',':
                sequence += 1  #M: esse incremento também aparece no if acima. Parece melhor subir um nível (para o if anterior).
        else:
            break
        prev_index = last_index
    
    if e_bool:
        return sequence
    
    return 0
        
    
def classify_contexts(document, doc_entities, scenario):
    context_features = ['O'] * len(document)
    sequence = 0
    clas = 'O'
    
    for i, (first_index, last_index) in enumerate(doc_entities):
        if sequence == 0:
            clas, ft = match_contexts(first_index, last_index, document, scenario)
        
        if clas != 'O':
            ne_len = last_index - first_index
            context_features[first_index:last_index] = [clas.upper()] * ne_len   
            
        if ft == 'pl':
            sequence = is_sequence(document, last_index, doc_entities[i+1:])
            
    return context_features

        
