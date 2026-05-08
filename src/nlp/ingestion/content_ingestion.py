from urllib.parse import urlparse
import requests, io, socket, ipaddress

from pathlib import Path
import re

from pdf2image import convert_from_bytes
import pdfplumber
import pytesseract

from docx import Document
from zipfile import ZipFile, is_zipfile

from bs4 import BeautifulSoup

class ContentIngestion:
    def __init__(self, file=None, url=None):
        self.file = file
        self.url = url
        self.text = ""

    def read(self):
        if not self.file and not self.url:
            return False

        if self.url:
            if self._is_blocked_host():
                return False
            self._fetch_url()

        if not self.file:
            return False

        ext = self._get_extension()

        if self._is_blocked_file(ext):
            return False

        self.text = ""

        readers = {
            "pdf": self._read_pdf,
            "doc": self._read_doc,
            "docx": self._read_doc,
            "txt": self._read_text,
            "text": self._read_text,
            "html": self._read_html,
            "xml": self._read_html,
        }

        reader = readers.get(ext)
        if not reader:
            return False

        reader()

        if not self.text.strip():
            return False

        cleaned_text = self._clean_text()
        return cleaned_text

    def _get_extension(self):
        return self.file.filename.split(".")[-1].lower()

    def _is_blocked_file(self, ext):
        allowed = {"pdf", "doc", "docx", "txt", "html"}
        max_size = 5 * 1024 * 1024

        if ext not in allowed:
            return True

        self.file.file.seek(0)
        content = self.file.file.read()
        size = len(content)
        self.file.file.seek(0)

        return size > max_size

    def _fetch_url(self):
        resp = requests.get(self.url, timeout=10)
        resp.raise_for_status()

        filename = Path(self.url).name or "file"

        self.file = type("FileObject", (), {})()
        self.file.filename = filename
        self.file.file = io.BytesIO(resp.content)

    def _is_blocked_host(self):
        allowed_types = [
            "application/pdf",
            "text/plain",
            "image/jpeg",
            "image/png",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

        try:
            resp = requests.head(self.url, allow_redirects=True, timeout=5)

            if resp.status_code != 200:
                return True

            content_type = resp.headers.get("Content-Type", "")
            if not any(t in content_type for t in allowed_types):
                return True

            parsed = urlparse(resp.url)
            domain = parsed.hostname
            if not domain:
                return True

            ip = ipaddress.ip_address(socket.gethostbyname(domain))

            if not parsed.path.lower().endswith(
                (".pdf", ".txt", ".jpg", ".png", ".docx")
            ):
                return True

            if (
                ip.is_private
                or ip.is_reserved
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_unspecified
            ):
                return True

            return False

        except requests.RequestException:
            return True

    def _clean_text(self):
        text = self.text.lower()
        text = re.sub(r"[^a-z0-9%\s]", " ", text)
        text = re.sub(r"\b\d+\b(?!%)", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _read_pdf(self):
        self.file.file.seek(0)
        content = self.file.file.read()

        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        self.text += t + "\n"

            if not self.text.strip():
                images = convert_from_bytes(content)
                for img in images:
                    self.text += pytesseract.image_to_string(
                        img, lang="rus+eng+ukr"
                    ) + "\n"

        except Exception as e:
            pass

    def _read_doc(self):
        self.file.file.seek(0)
        content = self.file.file.read()
        stream = io.BytesIO(content)

        if is_zipfile(stream):
            with ZipFile(stream) as z:
                if any("vbaProject.bin" in name for name in z.namelist()):
                    return

        stream.seek(0)
        doc = Document(stream)

        self.text = "\n".join(p.text for p in doc.paragraphs)

    def _read_text(self):
        self.file.file.seek(0)
        content = self.file.file.read()
        self.text = content.decode("utf-8", errors="ignore")
    
    def _read_html(self):
        dangerous = {"script", "iframe", "object", "embed"}

        self.file.file.seek(0)
        content = self.file.file.read().decode("utf-8", errors="ignore")

        soup = BeautifulSoup(content, "html.parser")

        if any(soup.find(tag) for tag in dangerous):
            return

        self.text = soup.get_text(separator="\n", strip=True)
