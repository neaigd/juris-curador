# Módulos do Sistema

## 1. Parser de Citações
- Extrai as citações autor-data e a bibliografia final do texto gerado pela LLM.
- Identifica os links correspondentes.

## 2. Baixador de PDFs
- Faz download direto de arquivos PDF.
- Em caso de páginas HTML, tenta encontrar o link para o PDF.

## 3. Processador e Anotador de PDFs
- Localiza trechos no PDF com base em texto citado.
- Usa PyMuPDF para destacar os trechos automaticamente.

## 4. Extrator de Metadados
- Utiliza CrossRef, GROBID e outras APIs para preencher metadados bibliográficos.

## 5. Gerador de Entrada para Zotero
- Gera JSON compatível com importação direta via Zotero ou API.
- Inclui referência formatada, link, anexo PDF e dados de citação.

## 6. Exportador para Obsidian/LibreOffice
- Usa Zotero + plugins (Zotfile, Mdnotes) para exportar anotações e referências.
