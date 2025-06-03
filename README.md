Perfeito! Vamos começar com o `README.md`.

Com base em tudo que discutimos, aqui está uma versão inicial e organizada do conteúdo para o projeto **Juris-Curador**:

---

## 📚 Juris-Curador

**Juris-Curador** é uma ferramenta automatizada para validação de fontes jurídicas citadas em pesquisas assistidas por IA. O sistema identifica, baixa, anota e organiza documentos jurídicos (como acórdãos e artigos), destacando os trechos relevantes e integrando metadados para uso direto no Zotero e outras ferramentas de escrita científica (Obsidian, LibreOffice etc.).

---

### ⚙️ Funcionalidades principais

* 📌 **Formatação de Citações e Bibliografia**: Geração de citações no corpo do texto e bibliografia final em formato ABNT (implementado em `src/citation_formatter.py`).
* 🔗 **Download Automatizado de Fontes**: Download de PDFs a partir de URLs diretas ou por busca em páginas web (implementado em `src/source_downloader.py`).
* 🖍️ **Anotação Automática de PDFs**: Marcação de trechos relevantes em arquivos PDF, com fallback para identificação via LLM (implementado em `src/pdf_processing.py`).
* 📄 **Geração de Entradas para Zotero**: Criação de arquivos JSON compatíveis para importação no Zotero, com metadados e links para os PDFs (implementado em `src/zotero_integration.py`).
* 🛠️ **Utilitários e Configuração**: Funções auxiliares para gerenciamento de configuração (via `config.yaml`), logging e manipulação de arquivos (implementado em `src/utils.py`).
* 🧩 Estrutura modular, facilitando expansão e integração com pipelines de escrita jurídica ou científica.

---

### 🧪 Exemplo de fluxo de uso

1. Você pede a uma LLM que gere um parecer ou artigo com fontes jurídicas.
2. O Juris-Curador:

   * Extrai e estrutura as citações e a bibliografia.
   * Baixa os arquivos das fontes referenciadas.
   * Destaca nos PDFs os trechos que justificam as citações.
   * Gera arquivos `.json` para importar para o Zotero.
3. Você importa os dados anotados no Zotero e utiliza normalmente em seu processo de escrita.

---

### 🗂 Estrutura do projeto

```
juris-curador/
├── config.yaml          # Arquivo de configuração principal (gerado na primeira execução)
├── docs/                # Documentação do sistema
├── examples/            # Exemplos de entrada e saída (a serem adicionados)
├── src/                 # Código-fonte dos módulos
│   ├── __init__.py
│   ├── citation_formatter.py
│   ├── llm_integration.py
│   ├── pdf_processing.py
│   ├── source_downloader.py
│   ├── utils.py
│   └── zotero_integration.py
├── tests/               # Testes unitários e de integração
│   ├── __init__.py
│   └── test_placeholder.py # (testes reais a serem adicionados)
├── README.md            # Este arquivo
└── requirements.txt     # Dependências do projeto
```

---

### 📌 Requisitos

* Python 3.10+
* Zotero (opcional, para integração com as entradas JSON geradas).
* Dependências listadas em `requirements.txt` (instaláveis via `pip install -r requirements.txt`), que incluem:
    * `PyMuPDF` para manipulação de PDFs.
    * `requests` e `BeautifulSoup4` para download e scraping de fontes.
    * `PyYAML` para gerenciamento da configuração.
    * `google-generativeai` (ou SDK similar) para integração com LLM (atualmente simulado).
* Uma chave de API para o serviço de LLM pode ser necessária para a funcionalidade completa de identificação de trechos por IA. Esta chave é configurada através da variável de ambiente especificada em `config.yaml` (e gerenciada por `src/utils.py`).

---

### 🛠️ Configuração

O Juris-Curador utiliza um arquivo de configuração chamado `config.yaml`, localizado na raiz do projeto. Este arquivo permite personalizar diversas configurações, incluindo:

* **Diretórios**: Caminhos para download de arquivos, PDFs anotados, exports do Zotero e logs.
* **Cores de Destaque**: Cores (RGB) usadas para os diferentes tipos de anotações nos PDFs.
* **Formatos de Saída**: Estilo de bibliografia (atualmente ABNT) e indentação do JSON para Zotero.
* **LLM**: Nome da variável de ambiente que armazena a chave da API LLM e modelo padrão.
* **Logging**: Nível de log, formato das mensagens e formato da data.

Se o arquivo `config.yaml` não for encontrado na primeira execução, o sistema o criará automaticamente com as configurações padrão. É recomendável revisar e ajustar este arquivo conforme necessário.

---

### 🛣️ Roadmap

**Funcionalidades Implementadas:**
* [x] Estrutura de documentação inicial.
* [x] Parser de citações e bibliografia ABNT (Implementado em `src/citation_formatter.py`).
* [x] Downloader de PDFs (por link direto ou scraping leve) (Implementado em `src/source_downloader.py`).
* [x] Marcador automático de trechos em PDF (Implementado em `src/pdf_processing.py` com fallback de LLM).
* [x] Exportador de entradas para o Zotero (JSON) (Implementado em `src/zotero_integration.py`).
* [x] Módulo de integração LLM (base) (Implementado em `src/llm_integration.py`, atualmente com resposta simulada).
* [x] Utilitários (configuração, logs) (Implementado em `src/utils.py`, utiliza `config.yaml`).

**Próximos Passos:**
* `[ ] Adicionar testes unitários e de integração abrangentes.`
* `[ ] Implementar lógica real de chamada à API LLM em llm_integration.py (substituir mock).`
* `[ ] Desenvolver o parser inicial de texto/documento de entrada para extrair citações e links (módulo principal do pipeline).`
* `[ ] Integrar todos os módulos em um pipeline funcional principal.`
* `[ ] Refinar a extração de metadados de PDFs.`
* `[ ] Melhorar a interface de linha de comando (CLI).`

---

### 🤝 Contribuições

Este projeto está em desenvolvimento. Se você deseja contribuir, envie sugestões, issues ou pull requests!

---

### 📜 Licença

Em definição. Sugestão inicial: [MIT License](https://opensource.org/licenses/MIT) ou [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.pt-br.html).


