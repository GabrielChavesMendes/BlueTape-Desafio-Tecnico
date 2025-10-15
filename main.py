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
    # Função para criar e retornar um navegador padrão do Chrome

    caminho_driver = 'chromedriver.exe'
    servico = Service(executable_path=caminho_driver)
    navegador = webdriver.Chrome(service=servico)
    navegador.maximize_window()
    return navegador


def coletar_links_empresas():
     # Função para abrir a página inicial do Reclama Aqui e coletar todos os links das melhores e piores empresas

    print("Coletando Links das Empresas")
    # Inicia uma nova instância do navegador para essa função
    navegador = get_navegador()
    lista_empresas = [] # Lista para armazenar todos os primeiros dados das empresas (Nome e Link)

    try:
        # Define a URL da página inicial
        url = 'https://www.reclameaqui.com.br/'
        navegador.get(url)
        # Tempo máximo para a automação esperar o carregamento completo da página
        wait = WebDriverWait(navegador, 20)

        '''
            Espera até o componente "ranking" esteja visível 
            Seleciona o seletor (placeholder) para o campo de seleção
            Espera o campo ser clicável e clica nele para abrir as opções
            Procura e seleciona o seletor "Casa de Aposta"
            Verifica se é a categoria certa e imprimi mensagem no terminal
        '''
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ranking-segment.w-full")))
        placeholder = "input[placeholder='Selecione ou busque uma categoria']"
        menu_selecao = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, placeholder)))
        menu_selecao.click()
        categoria = "//button[@title='Casa de Aposta']"
        casa_aposta = wait.until(EC.element_to_be_clickable((By.XPATH, categoria)))
        casa_aposta.click()
        wait.until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, placeholder), "Casa de Aposta"))
        print("Categoria 'Casa de Aposta' selecionada")

        '''
            Define o seletor para achar cada empresa (data-testid="listing-ranking")
            Espera todas as empresas estejam visíveis na aba "Melhores" e analisa as 3 primeiras
            Dentro do for, coleta:
                                  - Nome, encontrado no atributo 'alt' da imagem de cada empresa
                                  - Nota, encontrado no atributo <span>
                                  - Link, encontrado no atributo 'href' 
            Logo após a coleta, inclui todas as informações dentro da lista de empresas (lista_empresas.append) 
        '''
        seleciona_empresa = 'a[data-testid="listing-ranking"]'
        melhores_empresas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seleciona_empresa)))
        for elemento in melhores_empresas[:3]:
            nome = elemento.find_element(By.CSS_SELECTOR, 'img').get_attribute('alt')
            nota = elemento.find_element(By.CSS_SELECTOR, 'span.text-sm.font-bold').text
            link = elemento.get_attribute('href')
            if nome and link:
                lista_empresas.append({"Nome": nome, "Nota Inicial": nota, "Link": link, "Status": "Melhor"})


        primeira_empresa = melhores_empresas[0] # Referencia para a primeira empresa da lista
        # Encontra e clica na aba "Piores", por meio do atributo "tab-worst"
        aba_piores = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-testid="tab-worst"]')))
        aba_piores.click()
        # Espera até que o primeiro item da lista "Melhores" não seja mais usado garantindo que a página foi atualizada
        wait.until(EC.staleness_of(primeira_empresa))

        '''
            Espera todos as empresas da aba "Piores" estejam visíveis
            Analisa as 3 primeiras
            Dentro do for, coleta:
                                  - Nome, encontrado no atributo 'alt' da imagem de cada empresa, caso a coleta falhe e 
                                         resulte em "RA", coleta o nome da empresa por meio do atributo <span>
                                  - Nota, encontrado no atributo <span>
                                  - Link, encontrado no atributo 'href' 
            Logo após a coleta, inclui todas as informações dentro da lista de empresas (lista_empresas.append) 
        '''
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
        # Captura e amostra de erro
        print(f"Erro ao coletar os links: {e}")
    finally:
        # Garante que o navegador seja fechado ao finalizar a função
        navegador.quit()
        print("Primeira Coleta Finalizada\n")

    # Retorna a lista de empresas coletadas com as informações iniciais
    return lista_empresas


def extrair_dados_empresa(empresa):
    # Função para abrir o link de cada navegador individualmente para coletar os dados

    print(f"Iniciando Sessão para: {empresa['Nome']}")
    navegador = get_navegador() # Inicia um novo navegador para essa função

    # Inicializando dados de armazenamento
    dados = {
        "Reclamações Respondidas": "N/A", "Voltariam a Fazer Negócio": "N/A",
        "Índice de Solução": "N/A", "Nota do Consumidor": "N/A"
    }

    try:
        # Simulação de uma pausa para camuflar a detecção de robôs e automação na página
        pausa = random.uniform(2, 5)
        print(f"Pausa de: {pausa:.1f} segundos para coleta de dados")
        time.sleep(pausa)

        # Coleta o link da empresa pela lista preenchida pela função anterior, abre o link e espera 20seg para o carregamento total da página
        navegador.get(empresa['Link'])
        wait = WebDriverWait(navegador, 20)

        # Procura o primeiro dado por meio da frase "Respondeu" para garantir que a página foi acessada
        wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(., 'Respondeu')]")))

        # Função para extrair os dados necessário para a tabela
        def extrair_valor(texto_chave, is_percent=True, posicao=1):
            """
                Encontra a tag <span>
                Procura o texto auxiliar (texto_chave)
                Procura a tag filha <strong>
                Extrai o valor númerico dentro da tag filha até o simbolo %
                Retorna "N/A" caso não ache o valor
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

        # Chama a função auxiliar para cada texto chave e coleta as informações
        dados["Reclamações Respondidas"] = extrair_valor("Respondeu")
        dados["Voltariam a Fazer Negócio"] = extrair_valor("voltariam a fazer negócio")
        dados["Índice de Solução"] = extrair_valor("A empresa resolveu")
        dados["Nota do Consumidor"] = extrair_valor("nota média dos consumidores", is_percent=False, posicao=2)

        print(f"Dados de {empresa['Nome']} extraídos com sucesso.")

    except Exception as e:
        print(f"Erro ao extrair dados de {empresa['Nome']}.\nErro: {e}")
    finally:
        navegador.quit()
        print(f"Extração de dados da empresa {empresa['Nome']} finalizada\n")

    # Retorna os dados coletados
    return dados

# Função Principal
if __name__ == "__main__":
    # Chama a função "coletar_links_empresas" e armazena os dados em uma nova variável chamada empresas
    empresas = coletar_links_empresas()
    # Cria uma lista vazia para coletar os dados finais de cada empresa
    dados_finais = []

    if empresas:
        print(f"{len(empresas)} empresas serão processadas individualmente")

        ''' 
            O for irá passar por cada empresa coletada, acessando seu link 
            Chama a função para extrair os dados da empresa
            Combina os dados coletados em "empresa_informacao" com os dados em "dados_reputacao"
            Adiciona a combinação dos dados à lista final (dados_finas.append)
        '''
        for empresa_informacao in empresas:
            dados_reputacao = extrair_dados_empresa(empresa_informacao)
            registro_completo = {**empresa_informacao, **dados_reputacao}
            dados_finais.append(registro_completo)

        ''' 
            Gera a planilha com os dados coletados
            Cria um DataFrame do Pandas com os dados_finais
            Remova a coluna "Link" por ela não ser necessária na tebela
            Salva o DataFrame em .xlsx
        '''
        print("Gerando planilha Excel com todos os dados")
        df = pd.DataFrame(dados_finais)
        df = df.drop(columns=['Link'])
        df.to_excel("relatorio_casas_de_aposta.xlsx", index=False)
        print("Planilha 'relatorio_casas_de_aposta.xlsx' gerada e salva com sucesso!")
    else:
        print("Nenhuma empresa foi coletada. O script será encerrado.")

    print("\nAutomação finalizada.")

    '''
    GUIA DE EXECUÇÃO DO CÓDIGO

    PRÉ-REQUISITOS:
    1. Python instalado na máquina
    2. O arquivo 'chromedriver.exe' deve estar na mesma pasta que o código
    3. As bibliotecas necessárias para a execução do código: pip install selenium pandas openpyxl selenium-stealth

    ----------------------------------------------------------------------------------------------------------------------------------------

    MÉTODO 1: EXECUTAR PELA IDE

    Passo 1: Abrir o projeto
        - Baixe ou clone o projeto no github 
        - Abra o PyCharm (IDE utilizada para o projeto) ou outra IDE de preferência e certifique-se de que o projeto esteja aberto

    Passo 2: Verificar o interpretador
        - Verifique se a IDE está usando o interpretador do ambiente virtual (.venv). 
        Normalmente, isso é configurado automaticamente na criação do projeto

    Passo 3: Executando o Script
        - Abra o arquivo 'main.py' 
        - No menu de opções da IDE, selecione a opção "Run 'main'"
        - A execução irá começar
    
    ----------------------------------------------------------------------------------------------------------------------------------------
    
    MÉTODO 2: EXECUTAR PELO TERMINAL (WINDOWS EXPLORER)

    Passo 1: Abrir o terminal do projeto
       - Navegue até a pasta do projeto usando o Windows Explorer
       - Clique na barra de endereço 
       - Apague o texto do caminho, digite "cmd" e pressione Enter
       - Um terminal do Windows será aberto já dentro da pasta do projeto

    Passo 2: Ativar o ambiente virtual (.venv)
       - No terminal, digite o seguinte comando e pressione Enter: .\\.venv\\Scripts\\activate
       - Funcionará quando o nome (.venv) aparecer no início da linha de comando, ex: (.venv) C:\\Users\\SeuUsuario\\Documents\\BlueTape>

    Passo 3: Executar o código
       - Com o ambiente virtual ativado, digite o comando e pressione Enter para iniciar o robô: python main.py
       - O script começará a ser executado no terminal, e uma janela do navegador Chrome será aberta
       
    ----------------------------------------------------------------------------------------------------------------------------------------
       
    OBS: Caso a primeira execução falhe, execute o código novamente.
         É sujerido no momento que iniciar a execução, que a pessoa que esteja visualizando, não fique alterando os aplicativos ou 
            mexendo na máquina durante a execução, para que o código posso interpretar as páginas do navegador, caso contrário gerando erro
    '''