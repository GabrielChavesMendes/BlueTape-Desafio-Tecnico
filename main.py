# Importando bibliotecas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import random


def get_navegador():
    # Função para criar e retornar um navegador padrão

    caminho_driver = 'chromedriver.exe'
    servico = Service(executable_path=caminho_driver)
    navegador = webdriver.Chrome(service=servico)
    navegador.maximize_window()
    return navegador


def coletar_links_empresas():
     # Função para abrir a página inicial do Reclama Aqui e coletar todos os links das melhores e piores empresas

    print("Coletando Links das Empresas")
    navegador = get_navegador()
    lista_empresas = []

    try:
        url = 'https://www.reclameaqui.com.br/'
        navegador.get(url)
        wait = WebDriverWait(navegador, 20)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ranking-segment.w-full")))
        placeholder = "input[placeholder='Selecione ou busque uma categoria']"
        menu_selecao = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, placeholder)))
        menu_selecao.click()
        categoria = "//button[@title='Casa de Aposta']"
        casa_aposta = wait.until(EC.element_to_be_clickable((By.XPATH, categoria)))
        casa_aposta.click()
        wait.until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, placeholder), "Casa de Aposta"))
        print("Categoria 'Casa de Aposta' selecionada")

        seleciona_empresa = 'a[data-testid="listing-ranking"]'
        melhores_empresas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seleciona_empresa)))
        for elemento in melhores_empresas[:3]:
            nome = elemento.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')
            nota = elemento.find_element(By.CSS_SELECTOR, 'span.text-sm.font-bold').text
            link = elemento.get_attribute('href')
            if nome and link:
                lista_empresas.append({"Nome": nome, "Nota Inicial": nota, "Link": link, "Status": "Melhor"})

        primeira_empresa = melhores_empresas[0]
        aba_piores = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-testid="tab-worst"]')))
        aba_piores.click()
        wait.until(EC.staleness_of(primeira_empresa))

        piores_empresas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seleciona_empresa)))
        for elemento in piores_empresas[:3]:
            try:
                nome = elemento.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')
                if 'Selo RA' in nome:
                    raise ValueError("Usar fallback.")
            except:
                nome = elemento.find_element(By.CSS_SELECTOR, 'span.font-semibold').text

            nota = elemento.find_element(By.CSS_SELECTOR, 'span.text-sm.font-bold').text
            link = elemento.get_attribute('href')
            if nome and link:
                lista_empresas.append({"Nome": nome, "Nota Inicial": nota, "Link": link, "Status": "Pior"})

        print("Coleta de links finalizada com sucesso.")

    except Exception as e:
        print(f"Erro ao coletar os links: {e}")
    finally:
        navegador.quit()
        print("Primeira Coleta Finalizada\n")

    return lista_empresas


def extrair_dados_empresa(empresa):
    # Função para abrir o link de cada navegador individualmente para coletar os dados
    print(f"--- Iniciando Sessão para: {empresa['Nome']} ---")
    navegador = get_navegador()

    # Inicializando variável de armazenamento
    dados = {
        "Reclamações Respondidas": "N/A", "Voltariam a Fazer Negócio": "N/A",
        "Índice de Solução": "N/A", "Nota do Consumidor": "N/A"
    }

    try:
        pausa = random.uniform(2, 5)
        print(f"   - Pausa de: {pausa:.1f} segundos para coleta de dados")
        time.sleep(pausa)

        navegador.get(empresa['Link'])
        wait = WebDriverWait(navegador, 20)

        wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(., 'Respondeu')]")))

        def extrair_valor_com_chave(texto_chave, is_percent=True, posicao=1):
            """
            Encontra um <span> que contém um texto_chave, entra na tag <strong> filha
            na posição especificada, e extrai o valor numérico.
            """
            try:
                # O seletor XPath agora inclui a posição para desambiguação
                seletor_xpath = f"(//span[contains(., '{texto_chave}')]/strong)[{posicao}]"
                valor_completo = navegador.find_element(By.XPATH, seletor_xpath).text

                if is_percent:
                    valor_limpo = valor_completo.split('%')[0] + '%'
                else:
                    valor_limpo = valor_completo[:-1] if valor_completo.endswith('.') else valor_completo

                return valor_limpo
            except Exception:
                return "N/A"

        # --- LÓGICA DE EXTRAÇÃO ATUALIZADA ---
        dados["Reclamações Respondidas"] = extrair_valor_com_chave("Respondeu")
        dados["Voltariam a Fazer Negócio"] = extrair_valor_com_chave("voltariam a fazer negócio")
        dados["Índice de Solução"] = extrair_valor_com_chave("A empresa resolveu")
        dados["Nota do Consumidor"] = extrair_valor_com_chave("nota média dos consumidores", is_percent=False, posicao=2)

        print(f"Dados de {empresa['Nome']} extraídos com sucesso.")

    except Exception as e:
        print(f"Erro ao extrair dados de {empresa['Nome']}.\nErro: {e}")
    finally:
        navegador.quit()
        print(f"Extração de dados da empresa {empresa['Nome']} finalizada\n")

    return dados

# Função Principal
if __name__ == "__main__":
    empresas = coletar_links_empresas()
    dados_finais = []

    if empresas:
        print(f"--- {len(empresas)} empresas serão processadas individualmente ---")

        for empresa_informacao in empresas:
            dados_reputacao = extrair_dados_empresa(empresa_informacao)
            registro_completo = {**empresa_informacao, **dados_reputacao}
            dados_finais.append(registro_completo)

        print("Gerando planilha Excel com todos os dados")
        df = pd.DataFrame(dados_finais)
        df = df.drop(columns=['Link'])
        df.to_excel("relatorio_casas_de_aposta.xlsx", index=False)
        print("Planilha 'relatorio_casas_de_aposta.xlsx' gerada e salva com sucesso!")
    else:
        print("Nenhuma empresa foi coletada. O script será encerrado.")

    print("\nAutomação finalizada.")