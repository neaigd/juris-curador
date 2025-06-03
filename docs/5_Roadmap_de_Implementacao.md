# Roadmap de Implementação

Este roadmap descreve as etapas de desenvolvimento do Juris-Curador, desde o protótipo inicial até funcionalidades mais avançadas.

## Etapa 1: Fundação e Protótipo dos Módulos Centrais (Concluída Parcialmente/Em Andamento)

Os seguintes componentes foram implementados, formando a base do sistema:

*   ✅ **Formatação de Citações e Bibliografia (`citation_formatter.py`):**
    *   Geração de citações ABNT (autor-data) no corpo do texto.
    *   Criação de bibliografia completa no formato ABNT.
*   ✅ **Download de PDFs (`source_downloader.py`):**
    *   Download direto de arquivos PDF via URL.
    *   Scraping básico de páginas HTML para encontrar e baixar links de PDF.
*   ✅ **Processamento e Anotação de PDFs (`pdf_processing.py`):**
    *   Extração de texto de PDFs.
    *   Localização e realce de trechos exatos citados.
    *   Mecanismo de fallback para identificação de trechos relevantes via LLM (ver `llm_integration.py`).
    *   Cores de realce configuráveis.
*   ✅ **Geração de JSON para Zotero (`zotero_integration.py`):**
    *   Criação de arquivos JSON compatíveis com Zotero, incluindo metadados e links para os PDFs locais (anotados).
*   ✅ **Integração LLM (Base) (`llm_integration.py`):**
    *   Estrutura para construção de prompts e processamento de respostas de LLMs.
    *   *Implementação atual utiliza um mock para simular chamadas à API LLM.*
*   ✅ **Utilitários e Configuração (`utils.py`):**
    *   Sistema de configuração via arquivo `config.yaml` (diretórios, cores, chaves de API, logging).
    *   Módulo de logging configurável.
    *   Funções auxiliares para manipulação de arquivos.

**Itens Pendentes da Etapa Inicial:**
*   🚧 **Parser de Entrada de Texto:** Um módulo dedicado para analisar o texto inicial do usuário, extrair as citações e os links de forma estruturada para alimentar o pipeline.
*   🚧 **Orquestrador do Pipeline Principal:** Um script ou classe central que gerencia o fluxo completo de execução dos módulos.

## Próximos Passos Imediatos

Antes de prosseguir com novas funcionalidades, as seguintes tarefas são prioritárias:

*   ⏳ **Adicionar Testes Unitários e de Integração:**
    *   Desenvolver testes para cada módulo (`llm_integration`, `pdf_processing`, `source_downloader`, `citation_formatter`, `zotero_integration`, `utils`).
    *   Criar testes de integração para o fluxo principal (simulado, até o orquestrador existir).
*   🚀 **Implementação Real da Chamada à API LLM:**
    *   Substituir o mock em `llm_integration.py` por chamadas reais a uma API LLM (ex: Google Gemini/PaLM, OpenAI GPT).
    *   Gerenciar tokens, tratamento de erros e otimização de custos/performance.

## Etapa 2: Refinamento e Expansão do Core

*   **Melhoria da Extração de Metadados:**
    *   Integrar com APIs como CrossRef, OpenAlex, ou bibliotecas como GROBID para extrair metadados bibliográficos detalhados e precisos dos PDFs ou a partir de DOIs/URLs.
*   **Aprimoramento do Parser de Entrada:**
    *   Tornar o parser de citações mais robusto, suportando variações e identificando citações indiretas (apud).
*   **Interface de Linha de Comando (CLI):**
    *   Desenvolver uma CLI amigável para interagir com o sistema, passar arquivos de entrada e configurar opções.
*   **Validação e Tratamento de Erros:**
    *   Melhorar o tratamento de exceções, resiliência a links quebrados, PDFs protegidos ou mal formatados.

## Etapa 3: Integração Avançada com Zotero e Funcionalidades Adicionais

*   **Sincronização Direta com Zotero (API):**
    *   Explorar o uso da API do Zotero para criar/atualizar itens e coleções diretamente, em vez de apenas exportar JSON.
    *   Sincronizar anotações e PDFs modificados.
*   **Suporte a Múltiplos Formatos de Citação:**
    *   Expandir `citation_formatter.py` para suportar outros estilos (ex: APA, Vancouver), possivelmente integrando com bibliotecas CSL.
*   **Detecção Semântica Avançada:**
    *   Utilizar embeddings ou técnicas de busca semântica para encontrar trechos relevantes no PDF, especialmente quando citações exatas falham ou são parafraseadas.

## Etapa 4: Interface Gráfica (Opcional)

*   Desenvolvimento de uma interface gráfica simples (ex: web app local com Flask/Streamlit, ou uma extensão para Zotero) para facilitar o uso por usuários menos técnicos.

## Etapa 5: Empacotamento e Distribuição

*   Empacotar o projeto como uma biblioteca Python instalável (PyPI).
*   Criar executáveis ou pacotes para fácil distribuição.
*   Documentação oficial completa para usuários e desenvolvedores.
