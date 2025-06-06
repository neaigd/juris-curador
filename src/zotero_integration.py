# src/zotero_integration.py
# -*- coding: utf-8 -*-
"""Módulo para integração com Zotero:
- Criação de entradas bibliográficas no formato JSON compatível com Zotero.
- Associação dos PDFs às entradas.
- Exportação do JSON para arquivo.
"""

import json
import os
from typing import List, Dict, Any, Optional

class ZoteroIntegration:

    def _map_item_type_to_zotero(self, item_type_str: Optional[str]) -> str:
        """Maps common item types to Zotero item types."""
        if not item_type_str:
            return "document" # Default Zotero type

        type_map = {
            "journalArticle": "journalArticle",
            "book": "book",
            "bookSection": "bookSection",
            "conferencePaper": "conferencePaper",
            "report": "report",
            "thesis": "thesis",
            "webpage": "webpage",
            "manuscript": "manuscript",
            "patent": "patent",
            "statute": "statute", # Or "bill" depending on context
            "case": "case",
            # Add more mappings as needed
        }
        return type_map.get(item_type_str.lower(), "document")

    def _format_creators_for_zotero(self, authors_list: Optional[List[Dict[str, str]]]) -> List[Dict[str, str]]:
        """
        Formats authors into Zotero creator format.
        Input: [{"firstName": "John", "lastName": "Doe", "creatorType": "author"}, {"name": "Some Organization"}]
        Output: [{"creatorType": "author", "firstName": "John", "lastName": "Doe"}, {"creatorType": "author", "name": "Some Organization"}]
        """
        if not authors_list:
            return []

        zotero_creators = []
        for author_data in authors_list:
            creator = {}
            # Determine creator type (author, editor, contributor, etc.)
            # For simplicity, assume 'author' if not specified or map from a 'role' field if available.
            # Zotero uses 'creatorType' which can be 'author', 'editor', 'contributor', 'seriesEditor', etc.
            creator["creatorType"] = author_data.get("creatorType", "author").lower()

            if "firstName" in author_data or "lastName" in author_data:
                creator["firstName"] = author_data.get("firstName", "")
                creator["lastName"] = author_data.get("lastName", "")
            elif "name" in author_data: # For institutional authors or single-field names
                creator["name"] = author_data["name"]
            else:
                continue # Skip if no identifiable name fields

            zotero_creators.append(creator)
        return zotero_creators

    def create_zotero_json_item(self, item_metadata: Dict[str, Any], pdf_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a Zotero JSON item from metadata.
        Args:
            item_metadata (Dict[str, Any]): A dictionary containing metadata like:
                itemType, title, authors, date, url, doi, publicationTitle, volume,
                issue, pages, publisher, place, abstractNote, tags, etc.
            pdf_path (Optional[str]): Absolute path to the associated PDF file.
        Returns:
            Dict[str, Any]: A dictionary formatted for Zotero JSON import.
        """
        zotero_item = {
            "itemType": self._map_item_type_to_zotero(
                item_metadata.get("itemType")
            ),
            "title": item_metadata.get(
                "title", "No Title"
            ),
            "creators": self._format_creators_for_zotero(item_metadata.get("authors")),
            "date": item_metadata.get("date", ""), # YYYY-MM-DD or YYYY
            "url": item_metadata.get("url", ""),
            "DOI": item_metadata.get(
                "doi", ""
            ),
            "publicationTitle": item_metadata.get(
                "publicationTitle", ""
            ),  # Journal name, Book series
            "journalAbbreviation": item_metadata.get(
                "journalAbbreviation", ""
            ),
            "volume": item_metadata.get("volume", ""),
            "issue": item_metadata.get("issue", ""),
            "pages": item_metadata.get(
                "pages", ""
            ),
            "publisher": item_metadata.get("publisher", ""),
            "place": item_metadata.get(
                "place", ""
            ),  # Publication place
            "edition": item_metadata.get(
                "edition", ""
            ),
            "ISBN": item_metadata.get("ISBN", ""),
            "abstractNote": item_metadata.get("abstractNote", ""),
            "language": item_metadata.get(
                "language", "pt-BR"
            ),  # Default to Portuguese/Brazil
            "shortTitle": item_metadata.get(
                "shortTitle", ""
            ),
            "archive": item_metadata.get(
                "archive", ""
            ),
            "archiveLocation": item_metadata.get(
                "archiveLocation", ""
            ),
            "libraryCatalog": item_metadata.get(
                "libraryCatalog", ""
            ),
            "callNumber": item_metadata.get(
                "callNumber", ""
            ),
            "rights": item_metadata.get(
                "rights", ""
            ),
            "extra": item_metadata.get(
                "extra", ""
            ),
            "series": item_metadata.get(
                "series", ""
            ),
            "seriesNumber": item_metadata.get(
                "seriesNumber", ""
            ),
            "numberOfVolumes": item_metadata.get(
                "numberOfVolumes", ""
            ),
            "conferenceName": item_metadata.get(
                "conferenceName", ""
            ),
        }

        # Tags
        tags = item_metadata.get("tags", [])
        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
            zotero_item["tags"] = [
                {"tag": t} for t in tags
            ]
        elif isinstance(tags, list) and tags and isinstance(tags[0], dict) and "tag" in tags[0]:
             zotero_item["tags"] = tags # Assume already in Zotero format
        else:
            zotero_item["tags"] = []

        # Attachments (for PDF)
        zotero_item["attachments"] = []
        if pdf_path and os.path.exists(pdf_path):
            abs_pdf_path = os.path.abspath(pdf_path)
            attachment = {
                "title": item_metadata.get(
                    "title", "Attached PDF"
                ) + " (PDF)",
                # "path": abs_pdf_path, # Zotero desktop uses 'path' for linked files
                "localPath": abs_pdf_path, # Some importers might use this or 'path'
                                       # For Zotero Better BibTeX JSON, it's often `fileAttachments` array with `path`
                                       # For standard CSL-JSON import, Zotero connector often uploads and links.
                                       # For direct JSON import, Zotero expects file to be imported separately or path to be resolvable.
                                       # We'll use a common field, 'path', and note that Zotero might need manual linking or specific import method.
                "path": abs_pdf_path, # This is the most common field Zotero looks for when importing local files via JSON/RDF.
                "mimeType": "application/pdf",
                "itemType": "attachment", # Explicitly define item type for attachment
                "linkMode": "linked_file" # "imported_file" (copies to Zotero storage) or "linked_file" (links to original path)
                                          # "linked_url" for remote URLs.
                                          # For local files, "linked_file" is safer if user manages their own PDF store.
                                          # "imported_file" is better for Zotero's own storage management.
                                          # Let's default to linked_file for now.
            }
            # If you want Zotero to copy the file into its own storage on import:
            # attachment["linkMode"] = "imported_file" # Zotero will make a copy
            # If you want Zotero to link to the existing file path:
            attachment["linkMode"] = "linked_file"

            zotero_item["attachments"].append(attachment)

        # Remove empty fields for cleaner JSON
        return {k: v for k, v in zotero_item.items() if v or k == "title"} # title always included

    def generate_zotero_export_file(self, items_metadata: List[Dict[str, Any]], output_filepath: str, pdf_base_path: Optional[str] = None) -> bool:
        """
        Generates a Zotero JSON export file from a list of item metadata.
        Each item in items_metadata can have a 'local_pdf_filename' key (relative to pdf_base_path or absolute).
        Args:
            items_metadata (List[Dict[str, Any]]): List of item metadata dictionaries.
            output_filepath (str): Path to save the generated Zotero JSON file.
            pdf_base_path (Optional[str]): Base directory where PDFs are stored.
                                           If provided, 'local_pdf_filename' in metadata
                                           is joined with this path.
        Returns:
            bool: True if file generation was successful, False otherwise.
        """
        zotero_items_list = []
        for item_meta in items_metadata:
            pdf_path_for_item = None
            local_pdf_fn = item_meta.get("local_pdf_filename") # e.g., "document1.pdf"

            if local_pdf_fn:
                if os.path.isabs(local_pdf_fn):
                    pdf_path_for_item = local_pdf_fn
                elif pdf_base_path:
                    pdf_path_for_item = os.path.join(pdf_base_path, local_pdf_fn)
                else: # Assume relative to current dir if no base path and not absolute
                    pdf_path_for_item = os.path.abspath(local_pdf_fn)

            # The key 'local_pdf_path' might also be directly in item_meta from previous steps
            if not pdf_path_for_item and item_meta.get("local_pdf_path"):
                pdf_path_for_item = item_meta.get("local_pdf_path")


            if pdf_path_for_item and not os.path.exists(pdf_path_for_item):
                print(
                    f"WARNING: PDF path specified but not found: {pdf_path_for_item} "
                    f"for item '{item_meta.get('title')}'. Skipping attachment."
                )
                pdf_path_for_item = None

            zotero_json_item = self.create_zotero_json_item(item_meta, pdf_path=pdf_path_for_item)
            zotero_items_list.append(zotero_json_item)

        if not zotero_items_list:
            print("WARNING: No items to export to Zotero JSON.")
            return False

        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_filepath)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_filepath, 'w', encoding='utf-8') as f:
                # Zotero typically expects an array of items at the top level of the JSON file.
                json.dump(zotero_items_list, f, ensure_ascii=False, indent=4)
            print(
                f"INFO: Zotero JSON export file successfully created at: "
                f"{output_filepath}"
            )
            return True
        except IOError as e:
            print(f"ERROR: Could not write Zotero JSON file to {output_filepath}. Error: {e}")
            return False
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during Zotero JSON generation: {e}")
            return False

# Example Usage
if __name__ == '__main__':
    zotero_integrator = ZoteroIntegration()

    # Example metadata (similar to what citation_formatter might use/produce)
    item1_meta = {
        "itemType": "journalArticle",
        "authors": [{"firstName": "Ana", "lastName": "Costa", "creatorType": "author"},
                    {"firstName": "Carlos", "lastName": "Santos", "creatorType": "author"}],
        "title": "O impacto da inteligência artificial no direito processual",
        "publicationTitle": "Revista Brasileira de Direito Tecnológico",
        "volume": "10", "issue": "2", "pages": "45-67", "date": "2022-06-15",
        "url": "https://example.com/artigo_ia.pdf", "doi": "10.1234/rbdt.v10i2.5678",
        "abstractNote": "Uma análise contemporânea sobre IA e direito.",
        "tags": ["IA", "Direito Processual", "Tecnologia"],
        "local_pdf_filename": "artigo_ia_processual_annotated.pdf" # Relative filename
    }
    item2_meta = {
        "itemType": "book",
        "authors": [{"firstName": "João", "lastName": "Silva", "creatorType": "author"}],
        "title": "Manual de Direito Civil", "edition": "5", "place": "São Paulo",
        "publisher": "Editora Jurídica Atlas", "date": "2020", "ISBN": "978-8502123456",
        "tags": ["Direito Civil", "Manual"],
        "local_pdf_path": "/absolute/path/to/manual_civil_annotated.pdf" # Absolute path example
    }
    item3_meta = {
        "itemType": "webpage",
        "authors": [{"name": "JurisCurador Project Team", "creatorType":"author"}], # Institutional author
        "title": "Juris-Curador Oficial Website",
        "url": "https://example.com/juris-curador", "accessDate": "2023-12-01", "date": "2023-01-01",
        "tags": ["Jurisprudência", "Automação", "Software"]
        # No PDF for this webpage example
    }

    all_items_metadata = [item1_meta, item2_meta, item3_meta]

    # Create a dummy PDF file for item1 to test attachment linking
    # In a real scenario, this PDF would be the one downloaded and annotated.
    dummy_pdf_dir = "temp_pdfs_for_zotero_test"
    if not os.path.exists(dummy_pdf_dir):
        os.makedirs(dummy_pdf_dir)

    dummy_pdf_path_item1 = os.path.join(dummy_pdf_dir, item1_meta["local_pdf_filename"])
    with open(dummy_pdf_path_item1, "w") as f: # Create empty file
        f.write("This is a dummy PDF content for testing Zotero linking.")

    # For item2, the path is absolute and likely won't exist unless manually created by user.
    # The system will print a warning if it doesn't exist.
    # To make the test pass for item2 attachment, create a dummy file at that absolute path or change path.
    # For this example, we'll let it try the absolute path and potentially warn if not found.
    # If you want to test item2 pdf linking, create this file:
    # e.g. on Linux/macOS: mkdir -p /absolute/path/to; touch /absolute/path/to/manual_civil_annotated.pdf

    print("\n--- Generating Zotero JSON Item (Single) ---")
    single_z_item = zotero_integrator.create_zotero_json_item(item1_meta, pdf_path=dummy_pdf_path_item1)
    print(json.dumps(single_z_item, indent=4, ensure_ascii=False))


    print("\n--- Generating Zotero Export File ---")
    output_json_path = os.path.join(dummy_pdf_dir, "zotero_export.json")
    success = zotero_integrator.generate_zotero_export_file(
        all_items_metadata,
        output_json_path,
        pdf_base_path=dummy_pdf_dir  # Base path for relative PDF filenames
        # like in item1_meta
    )

    if success:
        print(
            f"Zotero export file generated: {output_json_path}"
        )
        print(
            "You can try importing this file into Zotero "
            "(e.g., File > Import from Clipboard after copying content, "
            "or File > Import...)."
        )
        print(
            "Ensure that PDF paths are correct and accessible from Zotero's "
            "perspective for linking."
        )
    else:
        print("Zotero export file generation failed.")

    # Clean up dummy files and directory (optional)
    # if os.path.exists(dummy_pdf_path_item1):
    #     os.remove(dummy_pdf_path_item1)
    # if os.path.exists(output_json_path):
    #     os.remove(output_json_path)
    # if os.path.exists(dummy_pdf_dir) and not os.listdir(dummy_pdf_dir):
    #     os.rmdir(dummy_pdf_dir)
    # print(
    #     f"Cleaned up dummy files in {dummy_pdf_dir}. Manual cleanup may be "
    #     "needed for absolute paths."
    # )
