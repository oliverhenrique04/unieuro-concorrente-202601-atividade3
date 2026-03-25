import os
import time
import random
import string
import multiprocessing as mp


# ===============================
# Consolidação dos resultados
# ===============================

def consolidar_resultados(resultados):
    total_linhas = 0
    total_palavras = 0
    total_caracteres = 0

    contagem_global = {
        "erro": 0,
        "warning": 0,
        "info": 0
    }

    for r in resultados:
        total_linhas += r["linhas"]
        total_palavras += r["palavras"]
        total_caracteres += r["caracteres"]

        for chave in contagem_global:
            contagem_global[chave] += r["contagem"][chave]

    return {
        "linhas": total_linhas,
        "palavras": total_palavras,
        "caracteres": total_caracteres,
        "contagem": contagem_global
    }


# ===============================
# Processamento de arquivo
# ===============================

def processar_arquivo(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.readlines()

    total_linhas = len(conteudo)
    total_palavras = 0
    total_caracteres = 0

    contagem = {
        "erro": 0,
        "warning": 0,
        "info": 0
    }

    for linha in conteudo:
        palavras = linha.split()

        total_palavras += len(palavras)
        total_caracteres += len(linha)

        for p in palavras:
            if p in contagem:
                contagem[p] += 1

        # Simulação de processamento pesado
        for _ in range(1000):
            pass

    return {
        "linhas": total_linhas,
        "palavras": total_palavras,
        "caracteres": total_caracteres,
        "contagem": contagem
    }

# ===============================
# Funções Produtor / Consumidor
# ===============================

def produtor_arquivos(pasta, arquivos, fila_tarefas, qtd_consumidores):
    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        fila_tarefas.put(caminho)
        
    # Envia o sinal de parada (Poison Pill) para os consumidores
    for _ in range(qtd_consumidores):
        fila_tarefas.put(None)

def consumidor_arquivos(fila_tarefas, fila_resultados):
    while True:
        caminho = fila_tarefas.get()
        if caminho is None:
            break # Encerra se receber o sinal de parada
        
        resultado = processar_arquivo(caminho)
        fila_resultados.put(resultado)


# ===============================
# Execução serial (Original mantida)
# ===============================

#def executar_serial(pasta):
#    resultados = []

#    inicio = time.time()

#    for arquivo in os.listdir(pasta):
#        caminho = os.path.join(pasta, arquivo)
#
#        resultado = processar_arquivo(caminho)
#        resultados.append(resultado)

#    fim = time.time()

#    resumo = consolidar_resultados(resultados)

#    print("\n=== EXECUÇÃO SERIAL ===")
#    print(f"Arquivos processados: {len(resultados)}")
#    print(f"Tempo total: {fim - inicio:.4f} segundos")

#    print("\n=== RESULTADO CONSOLIDADO ===")
#    print(f"Total de linhas: {resumo['linhas']}")
#    print(f"Total de palavras: {resumo['palavras']}")
#    print(f"Total de caracteres: {resumo['caracteres']}")

#    print("\nContagem de palavras-chave:")
#    for k, v in resumo["contagem"].items():
#        print(f"  {k}: {v}")

#    return resumo

# ===============================
# Execução paralela
# ===============================

def executar_paralelo(pasta, num_processos):
    resultados = []
    inicio = time.time()

    arquivos = os.listdir(pasta)
    total_arquivos = len(arquivos)
    
    # Criando o buffer limitado (maxsize)
    tamanho_buffer = 10 
    fila_tarefas = mp.Queue(maxsize=tamanho_buffer)
    fila_resultados = mp.Queue()

    # Iniciando o produtor
    produtor = mp.Process(target=produtor_arquivos, args=(pasta, arquivos, fila_tarefas, num_processos))
    produtor.start()

    # Iniciando os consumidores baseados na escolha do usuário
    consumidores = []
    for _ in range(num_processos):
        p = mp.Process(target=consumidor_arquivos, args=(fila_tarefas, fila_resultados))
        p.start()
        consumidores.append(p)

    # Coletando os resultados
    for _ in range(total_arquivos):
        resultados.append(fila_resultados.get())

    # Aguardando todos os processos finalizarem
    produtor.join()
    for p in consumidores:
        p.join()

    fim = time.time()
    resumo = consolidar_resultados(resultados)

    print("\n=== EXECUÇÃO PARALELA ===")
    print(f"Arquivos processados: {len(resultados)}")
    print(f"Processos utilizados: {num_processos}")
    print(f"Tempo total: {fim - inicio:.4f} segundos")

    print("\n=== RESULTADO CONSOLIDADO ===")
    print(f"Total de linhas: {resumo['linhas']}")
    print(f"Total de palavras: {resumo['palavras']}")
    print(f"Total de caracteres: {resumo['caracteres']}")

    print("\nContagem de palavras-chave:")
    for k, v in resumo["contagem"].items():
        print(f"  {k}: {v}")

    return resumo

# ===============================
# Main
# ===============================

if __name__ == "__main__":
    pasta = "log2" # Certifique-se de que esta pasta existe

    # 1. Executa a versão serial original
    #print("Iniciando versão serial...")
    #executar_serial(pasta)

    # 2. Pede a quantidade de threads/processos para o usuário
    print("\n---------------------------------------------------")
    escolha = input("Quantos processos (threads) deseja usar na versão paralela? ")
    
    try:
        num_processos = int(escolha)
        if num_processos <= 0:
            num_processos = 1
    except ValueError:
        print("Valor inválido. Utilizando 4 processos por padrão.")
        num_processos = 4

    # 3. Executa a versão paralela
    print("Iniciando versão paralela...")
    executar_paralelo(pasta, num_processos)