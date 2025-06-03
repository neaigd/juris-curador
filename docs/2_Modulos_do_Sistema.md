# Módulos do Sistema

O sistema Juris-Curador é composto pelos seguintes módulos principais, localizados em `src/`:

## 1. `source_downloader.py` (Baixador de Fontes)
-   **Responsabilidade:** Baixar os arquivos PDF das fontes citadas.
-   **Funcionalidades:**
    -   Realiza o download de PDFs a partir de URLs diretas.
    -   Busca e tenta baixar PDFs embutidos ou vinculados em páginas web (scraping básico de links `<a>` com href terminando em `.pdf` ou contendo `pdf`).
    -   Salva os arquivos baixados em um diretório configurável (via `config.yaml`, padrão: `juris_downloads/`).
    -   Evita sobrescrever arquivos existentes, adicionando um sufixo numérico se necessário.

## 2. `llm_integration.py` (Integração com LLM)
-   **Responsabilidade:** Interagir com Modelos de Linguagem Grande (LLMs) para encontrar trechos relevantes em PDFs.
-   **Funcionalidades (Versão Atual):**
    -   Constrói prompts contextuais com base no texto da citação e em um trecho do conteúdo do PDF.
    -   **Simula** uma chamada à API de um LLM (ex: Google PaLM/Gemini). *Nota: A integração real com a API LLM ainda precisa ser implementada.*
    -   Processa a resposta (simulada) do LLM para identificar o trecho de texto relevante.
    -   Configurável para buscar a chave da API de uma variável de ambiente (nome definido em `config.yaml`).

## 3. `pdf_processing.py` (Processador de PDF)
-   **Responsabilidade:** Extrair texto de PDFs e aplicar anotações (realces).
-   **Funcionalidades:**
    -   Extrai o texto completo de arquivos PDF utilizando a biblioteca PyMuPDF (fitz).
    -   Busca por ocorrências exatas do texto citado dentro do conteúdo do PDF.
    -   Se um trecho exato não é encontrado, utiliza o módulo `llm_integration.py` como fallback para identificar um trecho relevante.
    -   Aplica realces (highlights) coloridos diretamente no PDF nos trechos identificados (sejam exatos ou via LLM).
        -   As cores dos realces são configuráveis através do arquivo `config.yaml` (padrão: amarelo para citações primárias, outras cores para secundárias ou identificadas por LLM).
    -   Salva o PDF anotado em um diretório configurável (via `config.yaml`, padrão: `juris_annotated/`).

## 4. `citation_formatter.py` (Formatador de Citações ABNT)
-   **Responsabilidade:** Gerar citações bibliográficas no formato ABNT.
-   **Funcionalidades:**
    -   Formata nomes de autores conforme as regras da ABNT para citações no texto e para a lista de referências.
    -   Gera citações no corpo do texto no estilo ABNT (autor-data, ex: `(SILVA, 2020, p. 15)`).
    -   Constrói a bibliografia final completa no formato ABNT para diversos tipos de itens (artigos, livros, páginas web), incluindo detalhes como título, autores, editora, local, data, URL, DOI, etc.
    -   Permite a inclusão opcional de um link para o PDF local baixado na entrada bibliográfica.
    -   Realiza uma ordenação básica das entradas da bibliografia.

## 5. `zotero_integration.py` (Integração com Zotero)
-   **Responsabilidade:** Gerar arquivos de dados compatíveis para importação no Zotero.
-   **Funcionalidades:**
    -   Mapeia os tipos de item comuns (artigo, livro, etc.) para os tipos reconhecidos pelo Zotero.
    -   Formata os dados dos autores/criadores para o formato esperado pelo Zotero.
    -   Cria estruturas JSON para itens bibliográficos, incluindo metadados como título, autores, data, URL, DOI, resumo, tags, etc.
    -   Associa o caminho do PDF local (baixado e/ou anotado) ao item JSON correspondente, permitindo que o Zotero vincule o arquivo (`linkMode: "linked_file"`).
    -   Gera um arquivo JSON contendo uma lista de itens, que pode ser importado para o Zotero. O local de salvamento é configurável (via `config.yaml`, padrão: `juris_zotero_exports/`).

## 6. `utils.py` (Utilitários)
-   **Responsabilidade:** Fornecer funções auxiliares, gerenciamento de configuração e logging.
-   **Funcionalidades:**
    -   **Gerenciamento de Configuração:**
        -   Carrega configurações de um arquivo `config.yaml` (auto-gerado com padrões na primeira execução se não existir).
        -   Permite configurar diretórios de output, cores de realce para PDFs, nome da variável de ambiente da chave API do LLM, e configurações de log.
    -   **Logging:**
        -   Configura um sistema de logging para a aplicação, com nível, formato e destino (console/arquivo) configuráveis via `config.yaml`. O diretório de logs também é configurável (padrão: `juris_logs/`).
    -   **Utilitários de Arquivo:**
        -   Função para garantir que um diretório exista, criando-o se necessário.

## Módulos Futuros ou a Detalhar:

### Parser de Entrada (Input Parser)
-   *Ainda não implementado como um módulo dedicado.*
-   **Responsabilidade planejada:** Processar o texto de entrada do usuário (ex: um artigo ou parecer) para identificar e extrair citações jurídicas e os links para suas fontes. Este será um componente chave para iniciar o pipeline.

### Extrator de Metadados Avançado
-   *Funcionalidade básica de metadados está presente nos formatadores, mas um módulo avançado não está implementado.*
-   **Responsabilidade planejada:** Utilizar APIs como CrossRef, GROBID ou outras fontes para enriquecer automaticamente os metadados bibliográficos das fontes (ex: obter DOI, ISBN, autores completos, resumos de forma mais robusta).

### Orquestrador do Pipeline (Main/Core)
-   *Ainda não implementado.*
-   **Responsabilidade planejada:** Um script ou módulo principal que coordena o fluxo de trabalho completo, chamando os outros módulos na sequência correta: entrada -> download -> processamento PDF -> formatação -> exportação Zotero.
