# Importando bibliotecas
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def extrair_dados(navegador, link_empresa):

    # Inicializando os Dados
    dados = {
        "Reclamações Respondidas": "N/A",
        "Voltariam a Fazer Negócio": "N/A",
        "Índice de Solução": "N/A",
        "Nota do Consumidor": "N/A",
        "Nota Geral": "N/A"
    }
    try:
        navegador.switch_to.new_window('tab')
        navegador.get(link_empresa)
        wait = WebDriverWait(navegador, 20)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'reputation-container')]")))

        def extrair_texto(testid):
            try:
                return navegador.find_element(By.CSS_SELECTOR, f'[data-testid="{testid}"] span').text
            except:
                return "N/A"

        dados["Reclamações Respondidas"] = extrair_texto("complaint-answered")
        dados["Voltariam a Fazer Negócio"] = extrair_texto("deal-again")
        dados["Índice de Solução"] = extrair_texto("solution-index")
        dados["Nota do Consumidor"] = extrair_texto("consumer-score")

        try:
            dados["Nota Geral"] = navegador.find_element(By.CSS_SELECTOR, 'div[data-testid="reputation"] p.score').text
        except:
            dados["Nota Geral"] = "N/A"
        print(f"    - Dados extraídos com sucesso.")
    except Exception as e:
        print(f"    - Erro ao extrair dados: {e}")
    finally:
        navegador.close()
        navegador.switch_to.window(navegador.window_handles[0])
    return dados


def iniciar_automacao():
    caminho = 'chromedriver.exe'
    servico = Service(executable_path=caminho)

    navegador = webdriver.Chrome(service=servico)
    navegador.maximize_window() # Abrindo em Tela Cheia

    # URL para abrir a página inicial do site Reclame Aqui
    url = 'https://www.reclameaqui.com.br/'
    print("Iniciando o navegador e acessando a página inicial...")
    navegador.get(url)

    lista_empresas = [] # Array para armazenar as Melhores e Piores empresas
    try:
        wait = WebDriverWait(navegador, 20)

        # Esperando o componente de apresentação das empresas carregar totalmete
        print("Aguardando o componente de ranking carregar...")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ranking-segment.w-full")))
        print("Componente carregado.")

        # Abre o menu e seleciona a categoria "Casa de Aposta" automaticamente
        print("Selecionando a categoria 'Casa de Aposta' na página inicial...")
        seletor_placeholder = "input[placeholder='Selecione ou busque uma categoria']"
        campo_selecao = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_placeholder)))
        campo_selecao.click()

        seletor_opcao_categoria = "//button[@title='Casa de Aposta']"
        opcao_casa_aposta = wait.until(EC.element_to_be_clickable((By.XPATH, seletor_opcao_categoria)))
        opcao_casa_aposta.click()

        # Confere se o placeholder encontrado referencia a "Casa de Aposta" antes do menu fechar
        try:
            wait.until(EC.text_to_be_present_in_element_value(
                (By.CSS_SELECTOR, seletor_placeholder),
                "Casa de Aposta"
            ))
            print("✅ Certificado: Categoria 'Casa de Aposta' selecionada com sucesso.")
        except Exception:
            print("❌ Falha ao certificar a seleção da categoria. O script será encerrado.")
            navegador.quit()
            return

        print("Página atualizada com a categoria. Coletando links...")

        # Encontra as empresa pelo atributo "listing-ranking" que cada empresa possui, tanto as Melhores quanto as Piores
        seletor_card_empresa = 'a[data-testid="listing-ranking"]'

        print("\n--- Coletando as 3 Melhores Empresas ---")
        #Armazena todas as 3 empresas na variável "melhores_elementos"
        melhores_elementos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_card_empresa)))
        for elemento in melhores_elementos[:3]:
            # Loop para percorrer cada empresa armazenando seus atributos como Nome e Link
            nome = elemento.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')
            nota = elemento.find_element(By.CSS_SELECTOR, 'span.text-sm.font-bold').text
            link = elemento.get_attribute('href')
            if nome and link:
                # 3. Adiciona a NOTA ao dicionário
                lista_empresas.append({"Nome": nome, "Nota Inicial": nota, "Link": link, "Status": "Melhor"})

        print("--- Coletando as 3 Piores Empresas ---")
        # Reutiliza a lista anterior "melhores_elementos"
        primeiro_item_antigo = melhores_elementos[0]
        # Muda de opção de "Melhores" para "Piores", atualizando as empresas que aparecem, por meio do atributo "tab-worst"
        aba_piores = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-testid="tab-worst"]')))
        aba_piores.click()

        wait.until(EC.staleness_of(primeiro_item_antigo))
        print("   - Lista de empresas foi atualizada com sucesso.")

        # Seleciona todas as 3 piores empresas com o atributo "listing-ranking" e armazena seus dados Nome e Link
        piores_elementos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_card_empresa)))
        for elemento in piores_elementos[:3]:
            nome = elemento.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')
            nota = elemento.find_element(By.CSS_SELECTOR, 'span.text-sm.font-bold').text
            link = elemento.get_attribute('href')
            if nome and link:
                lista_empresas.append({"Nome": nome, "Nota Inicial": nota, "Link": link, "Status": "Pior"})

        print("\nColeta de links finalizada.")

        # Imprimi no terminal as empresas coletadas para conferir o resultado
        print("\nResumo das Empresas Coletadas")
        if lista_empresas:
            for i, empresa in enumerate(lista_empresas, 1):
                print(f"{i}. Nome: {empresa['Nome']} | Nota: {empresa['Nota Inicial']} ({empresa['Status']})")
                print(f"   Link: {empresa['Link']}")
        else:
            print("Nenhuma empresa foi coletada.")

        # Inicializa a extração de dados de cada empresa para criação da planinha
        # FASE AINDA NÃO FINAZLIDA
        print("\nIniciando extração de dados detalhados...")
        dados_coletados = []
        for empresa in lista_empresas:
            print(f"\nProcessando dados de: {empresa['Nome']} ({empresa['Status']})")
            reputacao = extrair_dados(navegador, empresa['Link'])
            registro_completo = {**empresa, **reputacao}
            dados_coletados.append(registro_completo)

        print("\n📊 Gerando planilha Excel...")
        df = pd.DataFrame(dados_coletados)
        df = df.drop(columns=['Link'])
        df.to_excel("relatorio_casas_de_aposta.xlsx", index=False)
        print("✅ Planilha 'relatorio_casas_de_aposta.xlsx' salva com sucesso!")

    except Exception as erro:
        print(f"Ocorreu um erro: {erro}")
    finally:
        time.sleep(5)
        navegador.quit()
        print("\nAutomação finalizada.")


if __name__ == "__main__":
    iniciar_automacao()