# Fluxo de Trabalho

```mermaid
flowchart TD
    A[Entrada: Texto com citações e links] --> B{Identifica/Parseia Citações e Links};
    B --> C[Download de PDFs (`source_downloader`)];
    C --> D{Processamento do PDF (`pdf_processing`)};
    D -- Trecho exato encontrado --> E[Realce de trecho exato];
    D -- Trecho exato NÃO encontrado --> F{Fallback com LLM (`llm_integration`)};
    F -- Trecho relevante identificado pela LLM --> G[Realce de trecho via LLM];
    F -- Trecho relevante NÃO identificado pela LLM --> H_skip[PDF salvo sem realce de citação específica];
    E --> I{PDF Anotado};
    G --> I;
    H_skip --> I;
    I --> J[Geração de JSON para Zotero (`zotero_integration`)];
    J --> K[Importação no Zotero (manual/via arquivo JSON)];
    I --> L[Geração de Citações ABNT (`citation_formatter`)];
    L --> M[Uso em Obsidian, LibreOffice, etc.];
    K --> M;
```

### Etapas resumidas

1.  **Entrada de Texto:** O sistema recebe um texto (ex: artigo, parecer) contendo citações jurídicas e links para as fontes.
2.  **Extração de Links e Download:** Links para PDFs são identificados. Os PDFs são baixados diretamente ou através de scraping da página vinculada (usando `source_downloader.py`).
3.  **Processamento e Anotação de PDFs:**
    *   Cada PDF baixado tem seu texto extraído (`pdf_processing.py`).
    *   O sistema busca os trechos exatos citados no texto original da pesquisa dentro do PDF.
    *   Se o trecho exato não for encontrado, uma chamada a um modelo de linguagem grande (LLM) é realizada (via `llm_integration.py`, atualmente com mock) para identificar um trecho relevante com base no contexto da citação.
    *   Os trechos encontrados (exatos ou via LLM) são destacados (realçados) diretamente no PDF. O PDF anotado é salvo.
4.  **Geração de Formatos de Saída:**
    *   **JSON para Zotero:** Metadados da fonte e links para os PDFs anotados são compilados em arquivos JSON compatíveis com Zotero (`zotero_integration.py`), facilitando a importação.
    *   **Citações ABNT:** Referências bibliográficas e citações no formato ABNT (autor-data) são geradas (`citation_formatter.py`) para uso em documentos.
5.  **Uso Externo:** As referências e os PDFs anotados podem ser utilizados em softwares como Zotero, Obsidian, LibreOffice, etc.
