# 🤖 Automação de Coleta de Dados - Reclame Aqui

Este projeto consiste em um script Python que utiliza a biblioteca Selenium para automatizar a coleta de dados de reputação de empresas no site Reclame Aqui. O foco da coleta é a categoria "Casa de Aposta", extraindo as 3 melhores e 3 piores empresas, seus indicadores de performance e salvando o resultado final em uma planilha Excel.

---

## Pré-requisitos

Antes de executar o script, garanta que os seguintes requisitos sejam atendidos:

1.  **Python** instalado na máquina (versão 3.8 ou superior recomendada).
2.  O arquivo **`chromedriver.exe`** deve estar presente na mesma pasta raiz do projeto.
3.  **Bibliotecas necessárias**: Instale as dependências executando o seguinte comando no seu terminal (com o ambiente virtual ativado):

    ```bash
    pip install selenium pandas openpyxl selenium-stealth
    ```

---

## Como Executar

Existem duas maneiras recomendadas para executar o script:

### Método 1: Executar pela IDE (Ex: PyCharm)

1.  **Abrir o Projeto**
    * Baixe ou clone este repositório para a sua máquina.
    * Abra a pasta do projeto na sua IDE de preferência (o projeto foi desenvolvido no PyCharm).

2.  **Verificar o Interpretador**
    * Certifique-se de que a IDE está configurada para usar o interpretador Python do ambiente virtual (`.venv`) do projeto. Isso geralmente é detectado automaticamente.

3.  **Executar o Script**
    * Abra o arquivo `main.py`.
    * Clique com o botão direito do mouse no editor de código.
    * Selecione a opção **"Run 'main'"**.
    * A automação será iniciada e o progresso será exibido no console da IDE.

### Método 2: Executar pelo Terminal (Windows)

1.  **Abrir o Terminal na Pasta do Projeto**
    * Navegue até a pasta raiz do projeto usando o Windows Explorer.
    * Clique na barra de endereço, digite `cmd` e pressione **Enter**.

2.  **Ativar o Ambiente Virtual (.venv)**
    * No terminal que foi aberto, execute o seguinte comando para ativar o ambiente:

        ```bash
        .\.venv\Scripts\activate
        ```
    * O prompt do terminal deve agora ser prefixado com `(.venv)`.

3.  **Executar o Código**
    * Com o ambiente ativado, inicie o script com o comando:

        ```bash
        python main.py
        ```
    * O navegador Chrome será aberto e a automação começará.

---

## Observações Importantes

> * Caso a primeira execução falhe (por instabilidade da rede ou do site), é recomendado executar o código novamente.
> * Durante a execução do robô, é sugerido **não utilizar o computador** para outras tarefas. Interações do usuário (como cliques ou mudança de janela) podem interferir na capacidade do Selenium de "enxergar" os elementos da página, o que pode causar erros e interromper o processo.
