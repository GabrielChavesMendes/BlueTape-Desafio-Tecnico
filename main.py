# Importando bibliotecas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time


def iniciar_automacao():
    # Caminho para o arquivo chromedriver.exe
    # Garanta que este arquivo está na mesma pasta do seu projeto.
    caminho = 'chromedriver.exe'

    # CORREÇÃO: O nome do parâmetro correto é 'executable_path'
    servico = Service(executable_path=caminho)

    # Instanciando o navegador
    navegador = webdriver.Chrome(service=servico)

    # URL do site Reclame Aqui
    url = 'https://www.reclameaqui.com.br'

    # Comando de abertura do Site
    print("Iniciando o navegador...")
    navegador.get(url)

    # Uma pausa para vermos o site abrir antes de fechar
    print("Site aberto com sucesso! O navegador será fechado em 10 segundos.")
    time.sleep(10)

    # Comando para fechar o navegador e encerrar a sessão
    navegador.quit()

    print("Automação finalizada.")


# Ponto de entrada do script (boa prática manter)
if __name__ == "__main__":
    iniciar_automacao()