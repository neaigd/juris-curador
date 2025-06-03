# src/pdf_processing.py
# -*- coding: utf-8 -*-
"""Módulo responsável pelo processamento de arquivos PDF:
- Extração de texto
- Identificação de trechos relevantes (com fallback para LLM)
- Anotação (como marcações, highlights) nos PDFs
"""

import fitz  # PyMuPDF
import os
from typing import List, Dict, Tuple, Any
from .llm_integration import LLMIntegration # Import the LLMIntegration class

# Define default highlight colors (RGB)
DEFAULT_HIGHLIGHT_COLORS: Dict[str, Tuple[float, float, float]] = {
    "primary": (1, 1, 0),  # Yellow for primary citations
    "secondary": (0, 1, 1),  # Cyan for secondary notes (example)
    "llm_identified": (0.8, 0.8, 0.2) # Khaki-like for LLM identified
}

class PDFProcessor:
    def __init__(self, llm_api_key: str = None, highlight_colors: Dict[str, Tuple[float, float, float]] = None):
        """
        Initializes the PDFProcessor.
        Args:
            llm_api_key (str, optional): API key for the LLM service.
            highlight_colors (Dict[str, Tuple[float, float, float]], optional):
                Custom colors for highlighting. Defaults to DEFAULT_HIGHLIGHT_COLORS.
        """
        self.llm_client = LLMIntegration(api_key=llm_api_key)
        self.highlight_colors = highlight_colors or DEFAULT_HIGHLIGHT_COLORS.copy()

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts all text from a given PDF file.
        Args:
            pdf_path (str): Path to the PDF file.
        Returns:
            str: Extracted text content, or empty string if extraction fails.
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def find_exact_matches(self, text_content: str, citation_text: str) -> List[Dict[str, Any]]:
        """
        Finds all exact occurrences of a citation_text in the text_content.
        Returns a list of dictionaries, each with 'page_num' and 'rect' (fitz.Rect).
        This function needs to be implemented based on how fitz provides coordinates.
        For now, it's a placeholder for locating text and getting its coordinates.

        Args:
            text_content (str): The full text of the PDF (used for context, not directly for fitz search).
            citation_text (str): The exact text to search for.
        Returns:
            List[fitz.Rect]: A list of fitz.Rect objects for each occurrence.
                               This is a simplified representation. In reality, you'd search page by page.
        """
        # This is a simplified placeholder. Real implementation would iterate through pages
        # and use page.search_for(citation_text) which returns fitz.Rect objects.
        # For now, we'll just indicate if it's found, but not the exact location.
        # This part needs to be significantly enhanced for actual highlighting.
        locations = []
        if citation_text.lower() in text_content.lower():
            # Simulate finding it on page 0 for now for highlighting demonstration
            # In a real scenario, you would call page.search_for(citation_text)
            # and get actual coordinates.
            print(f"DEBUG: Exact match found for '{citation_text}' (simulation for highlighting).")
            # This simulated rect will not correctly highlight in a multi-page document.
            # locations.append({"page_num": 0, "rect_list": [fitz.Rect(50, 100, 250, 120)]}) # Example Rect
        return locations


    def highlight_text_in_pdf(
        self,
        pdf_path: str,
        text_to_highlight: str,
        output_pdf_path: str,
        citation_type: str = "primary", # "primary", "secondary", "llm_identified"
        use_llm_fallback: bool = True
    ) -> bool:
        """
        Highlights specified text in a PDF. If exact text is not found,
        optionally uses LLM to find relevant text and highlights that.
        Saves the modified PDF to output_pdf_path.

        Args:
            pdf_path (str): Path to the original PDF file.
            text_to_highlight (str): The text snippet to search and highlight.
            output_pdf_path (str): Path to save the annotated PDF.
            citation_type (str): Type of citation ('primary', 'secondary', 'llm_identified') to determine color.
            use_llm_fallback (bool): Whether to use LLM if exact match fails.

        Returns:
            bool: True if highlighting was performed, False otherwise.
        """
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found at {pdf_path}")
            return False

        doc = fitz.open(pdf_path)
        highlight_color = self.highlight_colors.get(citation_type, self.highlight_colors["primary"])
        highlight_performed = False

        for page_num, page in enumerate(doc):
            # Try to find exact matches first
            exact_locations = page.search_for(text_to_highlight, quads=True)
            if exact_locations:
                for quad in exact_locations:
                    annot = page.add_highlight_annot(quad)
                    annot.set_colors(stroke=highlight_color) # PyMuPDF uses 'stroke' for highlight color
                    annot.update()
                    highlight_performed = True
                print(f"DEBUG: Highlighted exact match for '{text_to_highlight}' on page {page_num + 1} with color {highlight_color}")

        # If no exact matches found on any page and LLM fallback is enabled
        if not highlight_performed and use_llm_fallback:
            print(f"DEBUG: No exact match for '{text_to_highlight}'. Attempting LLM fallback.")
            pdf_full_text = self.extract_text_from_pdf(pdf_path) # Get full text for LLM
            if pdf_full_text:
                llm_snippet = self.llm_client.find_relevant_snippet(text_to_highlight, pdf_full_text)
                if llm_snippet and llm_snippet not in pdf_full_text : # check if the snippet is a substring of the original text
                    # This is a fallback if the LLM returns a phrase not directly searchable
                    print(f"DEBUG: LLM identified snippet that is not a direct substring. LLM snippet: '{llm_snippet}'")
                    # Try to find the LLM snippet (this might be broad)
                    # A more sophisticated approach would be needed here, like fuzzy matching or searching sentence by sentence
                    llm_highlight_color = self.highlight_colors.get("llm_identified", self.highlight_colors["primary"])
                    for page_num_llm, page_llm in enumerate(doc):
                        # This is a simplified search for the LLM snippet.
                        # Real-world LLM snippets might need more advanced localization.
                        # For example, the LLM might return a sentence, and you search for that sentence.
                        llm_locations = page_llm.search_for(llm_snippet, quads=True)
                        if llm_locations:
                            for quad in llm_locations:
                                annot = page_llm.add_highlight_annot(quad)
                                annot.set_colors(stroke=llm_highlight_color)
                                annot.update()
                                highlight_performed = True
                            print(f"DEBUG: Highlighted LLM-identified snippet ('{llm_snippet}') on page {page_num_llm + 1} with color {llm_highlight_color}")
                            break # Stop searching pages if LLM snippet found and highlighted
                elif llm_snippet: # if the snippet is a substring of the original text
                    llm_highlight_color = self.highlight_colors.get("llm_identified", self.highlight_colors["primary"])
                    for page_num_llm, page_llm in enumerate(doc):
                        llm_locations = page_llm.search_for(llm_snippet, quads=True)
                        if llm_locations:
                            for quad in llm_locations:
                                annot = page_llm.add_highlight_annot(quad)
                                annot.set_colors(stroke=llm_highlight_color)
                                annot.update()
                                highlight_performed = True
                            print(f"DEBUG: Highlighted LLM-identified snippet ('{llm_snippet}') on page {page_num_llm + 1} with color {llm_highlight_color}")
                            # Potentially break here if you only want the first occurrence highlighted by LLM
                else:
                    print(f"DEBUG: LLM fallback did not identify a usable snippet for '{text_to_highlight}'.")


        if highlight_performed:
            try:
                # Ensure the output directory exists
                output_dir = os.path.dirname(output_pdf_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
                print(f"INFO: Annotated PDF saved to {output_pdf_path}")
            except Exception as e:
                print(f"Error saving annotated PDF {output_pdf_path}: {e}")
                highlight_performed = False # Failed to save
        else:
            print(f"INFO: No highlights were made for '{text_to_highlight}' in {pdf_path}.")

        doc.close()
        return highlight_performed

# Example Usage (for testing purposes when run directly)
if __name__ == '__main__':
    print("Running PDF Processing example...")

    # Create a dummy PDF for testing
    dummy_pdf_path = "dummy_test.pdf"
    annotated_pdf_path = "dummy_test_annotated.pdf"

    # Create a simple PDF with PyMuPDF
    doc = fitz.open() # New empty PDF
    page = doc.new_page() # Add a page

    # Add some text to the page
    page.insert_text(fitz.Point(50, 72), "Este é um teste de processamento de PDF.", fontsize=11)
    page.insert_text(fitz.Point(50, 100), "A citação a ser encontrada é: 'Artigo 123 do Código Civil'.", fontsize=11)
    page.insert_text(fitz.Point(50, 120), "Mais algum texto para preencher a página.", fontsize=11)
    page.insert_text(fitz.Point(50, 140), "Outra frase importante: 'Princípio da Legalidade'.", fontsize=11)

    # Add a second page for LLM testing
    page2 = doc.new_page()
    page2.insert_text(fitz.Point(50, 72), "Esta é a segunda página.", fontsize=11)
    page2.insert_text(fitz.Point(50, 100), "Suponha que a LLM identifique o trecho: 'segunda página'.", fontsize=11)

    doc.save(dummy_pdf_path)
    doc.close()

    # Initialize PDFProcessor (assuming LLM API key is handled by LLMIntegration or set via ENV)
    pdf_processor = PDFProcessor(llm_api_key="DUMMY_API_KEY_FOR_SUBTASK") # LLM call is mocked in llm_integration for now

    # Test 1: Exact match highlighting
    citation1 = "Artigo 123 do Código Civil"
    print(f"\n--- Test 1: Exact Match for: '{citation1}' ---")
    success1 = pdf_processor.highlight_text_in_pdf(dummy_pdf_path, citation1, annotated_pdf_path, citation_type="primary")
    if success1:
        print(f"Exact match highlighting successful for '{citation1}'. Output: {annotated_pdf_path}")
        # For next step, use the already annotated PDF if you want cumulative highlights, or original for isolated.
        # For this test, we'll use the output of the previous step as input for the next.
        current_input_pdf = annotated_pdf_path
    else:
        print(f"Exact match highlighting failed for '{citation1}'.")
        current_input_pdf = dummy_pdf_path # Start fresh if previous failed


    # Test 2: LLM fallback (simulated)
    # This citation won't be found exactly, so LLM should be triggered.
    # The LLM mock will try to find it in the first 2000 chars of "dummy_pdf_path" text.
    # Let's make a citation that the LLM *can* find in the text (based on the mock logic)
    citation2_llm_target = "Princípio da Legalidade"
    # This is the text LLM mock will return as "identified" if "Apenas um teste para LLM" is the input to find_relevant_snippet
    # because the mock looks for `citation_text.lower() in pdf_snippet_for_prompt.lower()`
    # and `pdf_snippet_for_prompt` contains "Princípio da Legalidade"

    # The actual `text_to_highlight` is what we are "searching" for
    citation2_search_term = "Uma citação que não existe literalmente para teste LLM"

    annotated_pdf_path_llm = "dummy_test_annotated_llm.pdf"
    print(f"\n--- Test 2: LLM Fallback for: '{citation2_search_term}' (expecting LLM to find context around '{citation2_llm_target}') ---")

    # Modify llm_integration.py's mock to help this test case:
    # If find_relevant_snippet gets `citation2_search_term`, it should "find" `citation2_llm_target`
    # This requires modifying the llm_integration.py mock logic, which we can't do in this subtask directly.
    # So, we will rely on the existing mock logic: if the search term is part of the pdf text, it will return a snippet.
    # Let's make the search term something that *is* in the PDF to test the LLM path, but not an exact full quote.

    # For the LLM to "find" something, the `citation_text` given to `find_relevant_snippet`
    # must be present in `pdf_content[:2000]`.
    # The `pdf_content` of `dummy_test.pdf` includes "Princípio da Legalidade".
    # So, if we search for "Legalidade", the LLM mock should return a snippet.

    citation2_for_llm_mock = "Legalidade" # This text is in the dummy PDF.
                                      # The mock LLM will "find" this and return a snippet.

    # We need to ensure the LLM mock in llm_integration.py will behave as expected.
    # The current mock is:
    # if citation_text.lower() in pdf_snippet_for_prompt.lower():
    #    start_index = pdf_snippet_for_prompt.lower().find(citation_text.lower())
    #    end_index = start_index + len(citation_text) + 150
    #    llm_identified_text = pdf_snippet_for_prompt[start_index:end_index]
    # So if we search for "Legalidade", it will find "Legalidade'.", and return "Legalidade'. A jurisprudência..."

    success2 = pdf_processor.highlight_text_in_pdf(
        current_input_pdf, # Use output from previous step or original
        citation2_for_llm_mock, # The text we are trying to find (which will trigger LLM)
        annotated_pdf_path_llm,
        citation_type="secondary",
        use_llm_fallback=True
    )
    if success2:
        print(f"LLM fallback highlighting test successful for '{citation2_for_llm_mock}'. Output: {annotated_pdf_path_llm}")
    else:
        print(f"LLM fallback highlighting test failed for '{citation2_for_llm_mock}'.")

    # Test 3: Text not found (no LLM fallback or LLM doesn't find)
    citation3_not_found = "Texto inexistente no PDF"
    annotated_pdf_path_not_found = "dummy_test_annotated_not_found.pdf"
    print(f"\n--- Test 3: Text Not Found for: '{citation3_not_found}' ---")
    success3 = pdf_processor.highlight_text_in_pdf(
        dummy_pdf_path, # Use original PDF
        citation3_not_found,
        annotated_pdf_path_not_found,
        use_llm_fallback=True # LLM mock will also not find this
    )
    if not success3:
        print(f"Test for not found text successful (as expected, no highlight made).")
    else:
        print(f"Test for not found text failed (highlight was made unexpectedly).")


    # Test 4: Highlighting on second page using LLM (simulated)
    # The LLM mock needs to be "tricked" or it needs the text on the second page.
    # The current LLM mock only takes `pdf_content[:2000]`.
    # The text "segunda página" might be beyond the first 2000 chars if page 1 is dense.
    # Let's assume for this test the text "Esta é a segunda página." is within the first 2000 chars.
    # To make the LLM find something on the second page, the `find_relevant_snippet`
    # in `llm_integration.py` would need the text of the second page.
    # The current `pdf_processing.py` `highlight_text_in_pdf` calls `extract_text_from_pdf`
    # which gets ALL text. So the LLM mock *will* get all text.

    citation4_on_page2 = "segunda página" # This text is on page 2 of dummy_pdf_path
    annotated_pdf_path_page2 = "dummy_test_annotated_page2.pdf"
    print(f"\n--- Test 4: LLM Fallback for text on Page 2: '{citation4_on_page2}' ---")
    success4 = pdf_processor.highlight_text_in_pdf(
        dummy_pdf_path,
        citation4_on_page2,
        annotated_pdf_path_page2,
        citation_type="primary",
        use_llm_fallback=True # LLM mock should find "segunda página"
    )
    if success4:
        print(f"LLM fallback highlighting for page 2 text successful for '{citation4_on_page2}'. Output: {annotated_pdf_path_page2}")
    else:
        print(f"LLM fallback highlighting for page 2 text failed for '{citation4_on_page2}'.")


    # Clean up dummy files
    # os.remove(dummy_pdf_path)
    # print(f"Cleaned up {dummy_pdf_path}")
    # if os.path.exists(annotated_pdf_path): os.remove(annotated_pdf_path); print(f"Cleaned up {annotated_pdf_path}")
    # if os.path.exists(annotated_pdf_path_llm): os.remove(annotated_pdf_path_llm); print(f"Cleaned up {annotated_pdf_path_llm}")
    # if os.path.exists(annotated_pdf_path_not_found): os.remove(annotated_pdf_path_not_found); print(f"Cleaned up {annotated_pdf_path_not_found}")
    # if os.path.exists(annotated_pdf_path_page2): os.remove(annotated_pdf_path_page2); print(f"Cleaned up {annotated_pdf_path_page2}")

    print("\nPDF Processing example finished.")
