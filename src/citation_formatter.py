# src/citation_formatter.py
# -*- coding: utf-8 -*-
"""Módulo para formatação das citações:
- Geração de citações no corpo do texto (ex: ABNT autor-data)
- Construção da bibliografia final em ABNT
- Inclusão de links e metadados relevantes
"""

from typing import List, Dict, Any, Optional

class ABNTFomatter:

    def _format_authors_abnt(self, authors: List[Dict[str, str]], for_citation: bool = False) -> str:
        """
        Formats authors according to ABNT rules.
        Example author dict: {"firstName": "John", "lastName": "Doe", "creatorType": "author"}
                               or {"name": "Full Name"} for single field author

        For citation (in-text): (SILVA, 2020) or (SILVA; COSTA, 2020) or (SILVA et al., 2020)
        For bibliography: SILVA, João. or SILVA, J. (if only initial is available)
        """
        if not authors:
            return ""

        formatted_authors = []
        for author in authors:
            last_name = author.get("lastName", "")
            first_name = author.get("firstName", "")
            full_name = author.get("name", "") # For cases where name is a single string

            if not last_name and full_name: # Try to parse from full_name
                parts = full_name.split(" ")
                if len(parts) > 1:
                    last_name = parts[-1]
                    first_name = " ".join(parts[:-1])
                else:
                    last_name = parts[0]
                    first_name = ""

            if not last_name: # Skip if no last name
                continue

            last_name_upper = last_name.upper()

            if for_citation:
                formatted_authors.append(last_name_upper)
            else:
                if first_name:
                    # Check if first_name is just an initial (e.g., "J." or "J")
                    if len(first_name) == 1 or (len(first_name) == 2 and first_name.endswith('.')):
                        formatted_authors.append(f"{last_name_upper}, {first_name.upper().replace('.', '')}.")
                    else:
                        formatted_authors.append(f"{last_name_upper}, {first_name}.")
                else:
                    formatted_authors.append(last_name_upper + ".")

        if not formatted_authors:
            # For bibliography context, if item is a webpage and no authors, title is used as entry.
            # Otherwise, it's an unknown author.
            # This logic is now more context-aware in the calling function (format_bibliography_entry)
            return ""


        if for_citation:
            if len(formatted_authors) == 1:
                return formatted_authors[0]
            elif len(formatted_authors) == 2:
                return f"{formatted_authors[0]}; {formatted_authors[1]}"
            elif len(formatted_authors) >= 3:
                return f"{formatted_authors[0]} et al."
        else: # For bibliography
            return "; ".join(formatted_authors)


    def _get_year_from_date(self, date_str: Optional[str]) -> Optional[str]:
        """Extracts year from a date string (YYYY-MM-DD, YYYY, etc.)."""
        if not date_str:
            return None
        if len(date_str) >= 4 and date_str[:4].isdigit():
            return date_str[:4]
        return None

    def format_in_text_citation(
        self,
        item_metadata: Dict[str, Any],
        page: Optional[str] = None
    ) -> str:
        """
        Generates an ABNT in-text citation (Autor-data).
        Example: (SILVA, 2020, p. 15) or (UNIVERSIDADE DE SÃO PAULO, 2019)

        Args:
            item_metadata (Dict[str, Any]): Metadata for the item.
                                           Requires 'authors' and 'date'.
            page (Optional[str]): Page number for direct quotes.
        Returns:
            str: Formatted in-text citation.
        """
        authors = item_metadata.get("authors", [])
        year = self._get_year_from_date(item_metadata.get("date"))

        author_str = self._format_authors_abnt(authors, for_citation=True)

        # Handle corporate authors or title as author for in-text citation
        if not author_str:
            if item_metadata.get("itemType") == "webpage" and item_metadata.get("title"):
                # For webpages with no author, ABNT can use the first few words of title in CAPS.
                # This is a simplification: using the full title, then truncate if too long.
                title_words = item_metadata["title"].upper().split()
                author_str = " ".join(title_words[:3]) # Use first 3 words, for example
                if len(title_words) > 3:
                    author_str += "..."
            elif item_metadata.get("publisher") and not authors: # Check if publisher can be corporate author
                 # This is a heuristic for when 'publisher' might be a corporate author and 'authors' is empty.
                 # For in-text, usually the full name is used.
                 author_str = item_metadata["publisher"].upper()

        year_str = year or "s.d." # "sem data"

        if not author_str and not year:
            return "[s.n.]" # Sem nota / dados insuficientes

        citation_parts = []
        if author_str:
            citation_parts.append(author_str)

        citation_parts.append(year_str)

        if page:
            citation_parts.append(f"p. {page}")

        return f"({', '.join(citation_parts)})"


    def format_bibliography_entry(self, item: Dict[str, Any], include_download_link: bool = True) -> str:
        """
        Generates a bibliography entry in ABNT format.
        """
        parts = []
        entry_start_is_title = False

        # Authors or Title (for items like webpages without authors)
        author_str = self._format_authors_abnt(item.get("authors", []), for_citation=False)

        if author_str:
            parts.append(author_str)
        else:
            # Handle no author: corporate author (publisher) or title capitalization
            if item.get("publisher") and not item.get("authors"): # Check if publisher can be corporate author
                # ABNT NBR 6023:2018, 8.1.1.4 Entidades (órgãos governamentais, empresas, associações e outros)
                # "As obras de responsabilidade de entidade (órgãos governamentais, empresas, associações, congressos, seminários e outros)
                # têm entrada pelo seu próprio nome, por extenso, em letras maiúsculas."
                parts.append(item["publisher"].upper() + ".")
            elif item.get("itemType") == "webpage" and item.get("title"):
                # ABNT NBR 6023:2018, 8.1.1.6 Obras sem autoria ou responsabilidade
                # "A entrada é feita pelo título. A primeira palavra deve ser escrita em letras maiúsculas, seguida de reticências,
                # caso não seja possível determinar se o título é distinto ou significativo."
                # Or, more commonly for known titles: Title in CAPS.
                # Simplified: Full title in CAPS if no author for webpage.
                title_first_word_caps = item["title"].split(" ")[0].upper()
                remaining_title = " ".join(item["title"].split(" ")[1:])
                # parts.append(f"{title_first_word_caps.upper()} {remaining_title}.") # Using whole title in caps is safer
                parts.append(item["title"].upper() + ".")
                entry_start_is_title = True # Flag that the entry starts with a title
            elif item.get("title"): # Fallback to title if no author and not specific webpage rule
                 parts.append(item["title"].upper() + ".") # General rule for no author is title in caps
                 entry_start_is_title = True
            else: # Truly no identifiable entry point
                parts.append("[S.A.]") # Sem autor, if truly unknown and no title to use


        # Title and Subtitle (if not already used as the entry point)
        if not entry_start_is_title:
            title = item.get("title", "[S.T.]")
            subtitle = item.get("subtitle", "")
            if subtitle:
                title = f"{title}: {subtitle}"

            item_type = item.get("itemType", "document")
            if item_type == "journalArticle":
                parts.append(title + ".") # Article title is not bold
            elif item_type == "book":
                parts.append(f"**{title}**.") # Book title in bold
            else:
                parts.append(title + ".") # Default for reports etc.

        # Journal specific details (if it's an article and title wasn't the entry)
        if item.get("itemType") == "journalArticle":
            journal_title = item.get("publicationTitle", "[S.J.]")
            # ABNT: Journal title can be bold or italic. Using bold here.
            parts.append(f"**{journal_title}**")

            # Place of publication for journal (optional, but good if available)
            journal_place = item.get("journalPlace") # Custom field, or parse from publisher info
            if journal_place:
                parts.append(journal_place + ",") # Comma after place before vol/issue

            vol = item.get("volume")
            if vol: parts.append(f"v. {vol},")
            num = item.get("issue")
            if num: parts.append(f"n. {num},")
            pages = item.get("pages")
            if pages:
                if not pages.startswith("p.") and not pages.startswith("f."): # f. for folha
                    pages = "p. " + pages
                parts.append(pages + ",")

            # Date of publication for the specific article issue/volume
            # The main 'year' will be added later if this is more specific
            article_date_str = item.get("date") # Full date of article if available
            # ABNT month abbreviations: jan., fev., mar., abr., maio, jun., jul., ago., set., out., nov., dez.
            # This part can get complex with formatting month/season. For now, use year later.
            # If we have a more specific date for the journal issue (e.g. "Primavera 2023" or "jun. 2023")
            # it would go here. Simplified: year is added generally at the end.


        # Edition (for books)
        edition = item.get("edition")
        if edition and item.get("itemType") == "book":
            try:
                int(edition)
                parts.append(f"{edition}. ed.")
            except ValueError:
                parts.append(edition + ".")

        # Publication Place (for books, reports)
        if item.get("itemType") == "book" or item.get("itemType") == "report":
            if not entry_start_is_title or item.get("authors"): # Avoid repeating place if title was entry and no authors
                place = item.get("place", "[S.l.]")
                parts.append(place + ":")

        # Publisher (for books, reports)
        if item.get("itemType") == "book" or item.get("itemType") == "report":
            if not entry_start_is_title or item.get("authors"):
                 publisher = item.get("publisher", "[s.n.]")
                 parts.append(publisher + ",")

        # Year of publication
        year = self._get_year_from_date(item.get("date")) or "s.d."
        # Ensure year is added, considering if it was part of journal details already
        # A simple check: if the last part doesn't look like a year already.
        # This needs more robust logic if journal dates are more complex.
        if not any(year in p for p in parts[-2:]): # Avoid double year if already in journal info
            parts.append(year + ".")
        else: # If year might be embedded, ensure the part ends correctly
            if parts[-1].endswith(","):
                parts[-1] = parts[-1][:-1] + "." # Change trailing comma to period


        # Series information (for books, reports)
        series_title = item.get("series")
        series_number = item.get("seriesNumber")
        if series_title:
            series_info = series_title
            if series_number:
                series_info += f", {series_number}"
            parts.append(f"({series_info}).")


        # URL and Access Date (for online resources)
        url = item.get("url")
        if url:
            parts.append(f"Disponível em: <{url}>.")
            access_date = item.get("accessDate", "") # Expects "DD Mmm. YYYY" e.g. "10 dez. 2023"
            if access_date:
                parts.append(f"Acesso em: {access_date}.")
            else:
                # For online resources, access date is mandatory by ABNT if resource can change
                parts.append("Acesso em: [informar data de acesso].")


        # DOI
        doi = item.get("doi")
        if doi:
            # Check if DOI is already part of the URL (some styles do this)
            if not (url and doi in url):
                parts.append(f"DOI: {doi}.")

        # Link to local PDF
        local_pdf = item.get("local_pdf_path")
        if include_download_link and local_pdf:
            parts.append(f"[Download Local: {local_pdf}]")

        final_str = " ".join(p for p in parts if p).strip()
        final_str = final_str.replace(" ,", ",").replace(" .", ".").replace(" :", ":")
        final_str = final_str.replace(",.", ".").replace("..", ".").replace(":,", ":").replace(";,", ";")
        final_str = final_str.replace("  ", " ") # Consolidate spaces

        # Ensure ends with a period unless it's a bracketed link or already has proper terminal punctuation
        if not final_str.endswith((".", "]", ")", "?", "!")):
            final_str += "."
        if final_str.endswith("].") or final_str.endswith(")."):
            final_str = final_str[:-1]

        return final_str.strip()


    def generate_bibliography(self, items: List[Dict[str, Any]], include_download_links: bool = True) -> str:
        """
        Generates a full bibliography from a list of item metadata.
        """
        if not items:
            return ""

        def sort_key(item_data):
            authors_list = item_data.get("authors", [])
            year_val = self._get_year_from_date(item_data.get("date", "0000")) or "0000"

            entry_point = "[S.A.]" # Default if no author or title
            if authors_list: # Primary sort by first author's last name
                first_author = authors_list[0]
                last_name = first_author.get("lastName", "").upper()
                if not last_name and first_author.get("name"): # Handle {"name": "Full Name"}
                    name_parts = first_author["name"].split()
                    last_name = name_parts[-1].upper() if name_parts else ""
                entry_point = last_name if last_name else "[S.A.]"
            elif item_data.get("publisher") and not authors_list: # Corporate author (publisher)
                 entry_point = item_data["publisher"].upper()
            elif item_data.get("title"): # Sort by title if no author (e.g. webpage)
                entry_point = item_data["title"].upper()

            return (entry_point, year_val, item_data.get("title", "").upper())

        # Sort items according to ABNT (author, then year, then title)
        # NBR 6023:2018 item 7.1 - Ordem dos elementos:
        # "As referências dos documentos citados em um trabalho devem ser ordenadas de acordo com o sistema utilizado
        # para citação no texto (numérico ou alfabético), conforme Seção 6."
        # Assuming alphabetical system (author-date).
        sorted_items = sorted(items, key=sort_key)

        bib_entries = []
        for item_data in sorted_items:
            bib_entries.append(self.format_bibliography_entry(item_data, include_download_links))

        return "\n\n".join(bib_entries)


# Example Usage:
if __name__ == '__main__':
    formatter = ABNTFomatter()

    example_authors_1 = [{"firstName": "João", "lastName": "Silva"}]
    example_authors_2 = [{"firstName": "Ana", "lastName": "Costa"}, {"firstName": "Carlos", "lastName": "Santos"}]
    example_authors_3 = [
        {"firstName": "Maria", "lastName": "Oliveira"},
        {"firstName": "Pedro", "lastName": "Almeida"},
        {"firstName": "Sofia", "lastName": "Pereira"}
    ]
    example_corp_author = [{"name": "Instituto Brasileiro de Geografia e Estatística"}] # Handled by 'name'

    item1_article = {
        "itemType": "journalArticle", "authors": example_authors_2,
        "title": "O impacto da inteligência artificial no direito processual", "subtitle": "Uma análise contemporânea",
        "publicationTitle": "Revista Brasileira de Direito Tecnológico", "volume": "10", "issue": "2",
        "pages": "45-67", "date": "2022-06-15", "url": "https://example.com/artigo_ia.pdf",
        "accessDate": "10 dez. 2023", "doi": "10.1234/rbdt.v10i2.5678",
        "local_pdf_path": "/downloads/artigo_ia.pdf"
    }
    item2_book = {
        "itemType": "book", "authors": example_authors_1, "title": "Manual de Direito Civil",
        "edition": "5", "place": "São Paulo", "publisher": "Editora Jurídica Atlas", "date": "2020",
        "series": "Manuais Jurídicos Essenciais", "seriesNumber": "3",
        "local_pdf_path": "/downloads/manual_civil.pdf"
    }
    item3_webpage_corp_author = {
        "itemType": "webpage", "authors": example_corp_author, # Authors list with a corporate name
        "title": "Censo Demográfico 2022: Primeiros Resultados",
        "url": "https://www.ibge.gov.br/censo2022", "accessDate": "05 ago. 2023", "date": "2023-07-28"
    }
    item4_webpage_no_author = { # No 'authors' field
        "itemType": "webpage", "title": "Guia Completo de Python para Análise de Dados",
        "url": "https://www.pythontotal.com/guia-python-dados", "accessDate": "01 jan. 2024", "date": "2023"
    }
    item5_book_publisher_as_author = { # No 'authors', but has 'publisher'
        "itemType": "book", "title": "Relatório Anual de Atividades 2022",
        "place": "Brasília", "publisher": "Ministério da Economia", "date": "2023"
    }


    print("--- In-text Citations ---")
    print(formatter.format_in_text_citation(item1_article))
    print(formatter.format_in_text_citation(item2_book, "101-105"))
    print(formatter.format_in_text_citation(item3_webpage_corp_author)) # (INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA, 2023)
    print(formatter.format_in_text_citation(item4_webpage_no_author)) # (GUIA COMPLETO DE PYTHON..., 2023)
    print(formatter.format_in_text_citation(item5_book_publisher_as_author, "33")) # (MINISTÉRIO DA ECONOMIA, 2023, p. 33)
    print(formatter.format_in_text_citation({"authors": example_authors_3, "date": "2021"}, "77"))


    print("\n--- Bibliography Entries (Individually) ---")
    print("Article:\n" + formatter.format_bibliography_entry(item1_article))
    print("\nBook:\n" + formatter.format_bibliography_entry(item2_book))
    print("\nWebpage (Corporate Author):\n" + formatter.format_bibliography_entry(item3_webpage_corp_author))
    print("\nWebpage (No Author - Title entry):\n" + formatter.format_bibliography_entry(item4_webpage_no_author))
    print("\nBook (Publisher as Author entry):\n" + formatter.format_bibliography_entry(item5_book_publisher_as_author))


    print("\n--- Full Bibliography (Sorted) ---")
    all_items = [item1_article, item2_book, item3_webpage_corp_author, item4_webpage_no_author, item5_book_publisher_as_author]
    # Add one more for sorting test
    item6_another_silva = {
        "itemType": "book", "authors": [{"firstName": "Mariana", "lastName": "Silva"}],
        "title": "Direito Constitucional Avançado", "edition": "2",
        "place": "Rio de Janeiro", "publisher": "Editora Forense", "date": "2019"
    }
    all_items.append(item6_another_silva)

    print(formatter.generate_bibliography(all_items, include_download_links=True))

    print("\n--- Bibliography (No Local Links) ---")
    print(formatter.generate_bibliography(all_items, include_download_links=False))
