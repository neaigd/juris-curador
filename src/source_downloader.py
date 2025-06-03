# src/source_downloader.py
# -*- coding: utf-8 -*-
"""Módulo para download e gerenciamento das fontes:
- Download de PDFs a partir de URLs diretas.
- Busca e download de PDFs a partir de páginas web.
- Validação e armazenamento local dos arquivos baixados.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class SourceDownloader:
    def __init__(self, download_dir: str = "downloads"):
        """
        Initializes the SourceDownloader.
        Args:
            download_dir (str): Directory to save downloaded files.
        """
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)

    def _get_filename_from_url(self, url: str, content_type: str = None) -> str:
        """
        Extracts a filename from a URL or Content-Type header.
        """
        # Try to get filename from URL path
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if filename and '.' in filename: # Basic check for an extension
            return filename

        # Try to get filename from Content-Disposition header (not directly accessible here,
        # but often reflected in final URL after redirects or if server suggests one)
        # This part is simplified. A more robust solution would check response headers.

        # Fallback based on content type
        if content_type:
            if 'application/pdf' in content_type:
                return "document.pdf"

        # Generic fallback
        return "downloaded_file"

    def download_direct_pdf(self, pdf_url: str, custom_filename: str = None) -> str | None:
        """
        Downloads a PDF directly from a given URL.
        Args:
            pdf_url (str): The direct URL to the PDF file.
            custom_filename (str, optional): A custom name for the downloaded file.
        Returns:
            str | None: Path to the downloaded PDF, or None if download fails.
        """
        try:
            print(f"INFO: Attempting to download direct PDF from: {pdf_url}")
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors

            content_type = response.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type:
                print(f"WARNING: URL {pdf_url} does not appear to be a direct PDF link. Content-Type: {content_type}")
                # Depending on strictness, you might return None here or try to save anyway.
                # For now, we'll proceed if server doesn't explicitly say it's not a PDF.

            if custom_filename:
                filename = custom_filename
                if not filename.lower().endswith(".pdf"):
                    filename += ".pdf"
            else:
                filename = self._get_filename_from_url(pdf_url, content_type)
                if not filename.lower().endswith(".pdf"): # Ensure it has a .pdf extension
                    name_part, _ = os.path.splitext(filename)
                    filename = name_part + ".pdf"


            file_path = os.path.join(self.download_dir, filename)

            count = 0
            base_name, ext = os.path.splitext(file_path)
            while os.path.exists(file_path): # Avoid overwriting
                count += 1
                file_path = f"{base_name}_{count}{ext}"

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"INFO: Successfully downloaded PDF to: {file_path}")
            return file_path
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to download PDF from {pdf_url}. Error: {e}")
            return None
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while downloading {pdf_url}. Error: {e}")
            return None

    def find_and_download_pdf_from_page(self, page_url: str, custom_filename_base: str = None) -> str | None:
        """
        Scrapes a webpage to find PDF links and downloads the first one found.
        Args:
            page_url (str): URL of the webpage to scrape.
            custom_filename_base (str, optional): A custom base name for the downloaded file if found.
        Returns:
            str | None: Path to the downloaded PDF, or None if not found or download fails.
        """
        try:
            print(f"INFO: Attempting to find PDF on page: {page_url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(page_url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            pdf_links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Check if href ends with .pdf or contains .pdf? (common for download links)
                if href.lower().endswith('.pdf') or '.pdf?' in href.lower():
                    pdf_url = urljoin(page_url, href) # Handle relative links
                    pdf_links.append(pdf_url)
                # Optional: Check if the link text suggests it's a PDF
                elif 'pdf' in a_tag.get_text().lower() and (href.startswith('http') or href.startswith('/')):
                    pdf_url = urljoin(page_url, href)
                    # Further check if this link might lead to a PDF (less reliable)
                    # For now, we prioritize direct .pdf links
                    # You could add a HEAD request here to check Content-Type if needed
                    pdf_links.append(pdf_url)


            if not pdf_links:
                print(f"INFO: No direct PDF links found on {page_url} via common patterns.")
                # Add more sophisticated search logic here if needed (e.g., looking for specific class names, etc.)
                return None

            # Try downloading the first plausible link
            # More advanced logic could involve trying multiple links or using heuristics
            for idx, found_pdf_url in enumerate(pdf_links):
                print(f"INFO: Found potential PDF link: {found_pdf_url}")
                # Create a filename based on the page URL or a custom name
                if custom_filename_base:
                    filename_to_use = f"{custom_filename_base}_{idx}.pdf" if len(pdf_links) > 1 else f"{custom_filename_base}.pdf"
                else:
                    page_domain = urlparse(page_url).netloc.replace('.', '_')
                    base_name_from_url = self._get_filename_from_url(found_pdf_url)
                    # remove .pdf from base_name_from_url if it exists, it will be added by download_direct_pdf
                    base_name_from_url, _ = os.path.splitext(base_name_from_url)

                    filename_to_use = f"{page_domain}_{base_name_from_url}.pdf"


                # Attempt to download this PDF
                # We call download_direct_pdf which will also check content-type if possible
                downloaded_path = self.download_direct_pdf(found_pdf_url, custom_filename=filename_to_use)
                if downloaded_path:
                    # For this basic version, we take the first successfully downloaded PDF
                    return downloaded_path

            print(f"ERROR: Found PDF links, but failed to download any from {page_url}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to access page {page_url}. Error: {e}")
            return None
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while scraping {page_url}. Error: {e}")
            return None

# Example Usage
if __name__ == '__main__':
    print("Running Source Downloader example...")
    downloader = SourceDownloader(download_dir="downloaded_pdfs_test")

    # Test 1: Direct PDF download
    # Using a known public PDF link for testing. Replace with a stable link if this becomes invalid.
    # Example: arXiv PDF link (usually stable)
    direct_pdf_url = "https://arxiv.org/pdf/2307.09288.pdf" # Example: Llama 2 paper
    print(f"\n--- Test 1: Direct PDF Download from {direct_pdf_url} ---")
    downloaded_file_path = downloader.download_direct_pdf(direct_pdf_url, custom_filename="llama2_paper.pdf")
    if downloaded_file_path:
        print(f"Direct download successful: {downloaded_file_path}")
        # os.remove(downloaded_file_path) # Clean up
        # print(f"Cleaned up {downloaded_file_path}")
    else:
        print(f"Direct download failed for {direct_pdf_url}")

    # Test 2: Scrape a webpage for a PDF
    # This requires a webpage that is known to link to a PDF.
    # Example: A page that links to a PDF.
    # For this test to work reliably, you need a stable URL that you know contains a PDF link.
    # Let's use an arXiv abstract page, which links to its PDF.
    page_with_pdf_url = "https://arxiv.org/abs/2307.09288" # Abstract page for Llama 2 paper
    print(f"\n--- Test 2: Scrape PDF from Page {page_with_pdf_url} ---")
    scraped_pdf_path = downloader.find_and_download_pdf_from_page(page_with_pdf_url, custom_filename_base="scraped_arxiv_doc")
    if scraped_pdf_path:
        print(f"Scraping and download successful: {scraped_pdf_path}")
        # os.remove(scraped_pdf_path) # Clean up
        # print(f"Cleaned up {scraped_pdf_path}")
    else:
        print(f"Scraping and download failed for {page_with_pdf_url}")

    # Test 3: Direct PDF download - invalid URL
    invalid_pdf_url = "https://example.com/nonexistent.pdf"
    print(f"\n--- Test 3: Direct PDF Download from Invalid URL {invalid_pdf_url} ---")
    downloaded_file_path_invalid = downloader.download_direct_pdf(invalid_pdf_url)
    if not downloaded_file_path_invalid:
        print(f"Direct download from invalid URL failed as expected.")
    else:
        print(f"Direct download from invalid URL somehow succeeded (unexpected): {downloaded_file_path_invalid}")
        # os.remove(downloaded_file_path_invalid)
        # print(f"Cleaned up {downloaded_file_path_invalid}")

    # Test 4: Scrape a webpage - no PDF expected
    page_without_pdf_url = "https://www.google.com"
    print(f"\n--- Test 4: Scrape Page with No PDF Expected {page_without_pdf_url} ---")
    scraped_pdf_path_no_pdf = downloader.find_and_download_pdf_from_page(page_without_pdf_url)
    if not scraped_pdf_path_no_pdf:
        print(f"Scraping page with no PDF failed to find a PDF, as expected.")
    else:
        print(f"Scraping page with no PDF somehow found and downloaded a PDF (unexpected): {scraped_pdf_path_no_pdf}")
        # os.remove(scraped_pdf_path_no_pdf)
        # print(f"Cleaned up {scraped_pdf_path_no_pdf}")

    print("\nSource Downloader example finished.")
    print(f"Please check the '{downloader.download_dir}' directory for downloaded files.")
    print("Remember to manually clean up this directory after testing if files are not removed by the script.")
