# Fluxo de Trabalho

```mermaid
flowchart TD
    A[Saída da LLM com citações] --> B[Parser de citações e links]
    B --> C[Download de PDFs]
    C --> D[Extração de metadados]
    D --> E[Anotação automática dos PDFs]
    E --> F[Criação de entrada JSON para Zotero]
    F --> G[Importação no Zotero]
    G --> H[Exportação para Obsidian ou LibreOffice]
```

### Etapas resumidas

1. Coleta da saída da LLM com referências em ABNT.
2. Processamento das citações e links.
3. Download e anotação dos PDFs.
4. Extração de metadados (DOI, autores, etc.).
5. Geração de entradas bibliográficas com os PDFs.
6. Integração Zotero e exportações automáticas.
