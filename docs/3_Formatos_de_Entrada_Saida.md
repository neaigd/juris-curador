# Formatos de Entrada e Saída

## Entrada
- Texto com citações no corpo no estilo ABNT (autor-data).
- Bibliografia com links (PDFs ou páginas web).

## Saída
- PDFs anotados com trechos citados.
- Arquivos JSON contendo entradas bibliográficas completas.
- Exportações em Markdown ou RTF para uso em Obsidian ou LibreOffice.

## Exemplo de JSON Zotero
```json
{
  "title": "Título do artigo",
  "creators": [{ "firstName": "Nome", "lastName": "Sobrenome", "creatorType": "author" }],
  "itemType": "journalArticle",
  "date": "2023",
  "DOI": "10.xxxx/yyyy",
  "url": "https://...",
  "attachments": [{ "title": "PDF", "path": "/caminho/arquivo.pdf", "mimeType": "application/pdf" }]
}
```
