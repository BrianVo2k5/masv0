import os # Imports the operating system module (used for file path manipulations).
import re
from plyer import filechooser # Imports the plyer tool to open native file explorer windows.
from PyPDF2 import PdfReader # Imports the PDF processing library to read and extract text.
import threading # Imports the module used to run tasks in the background so the app doesn't freeze.
from kivy.clock import Clock # Imports the Kivy timer tool to safely send data from a background thread back to the UI.
from PIL import Image
import pytesseract
import cv2
import numpy as np

try:
    import fitz  # PyMuPDF — optional, used as a more robust PDF backend with OCR fallback.
    _HAS_FITZ = True
except ImportError:
    _HAS_FITZ = False

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class FileUploadManager: 
    def __init__(self, callback):
        self.callback = callback
        self.is_processing = False  # 1. ADDED LOCK

    def open_file_dialog(self):
        if self.is_processing:
            return # Block duplicate clicks
        self.is_processing = True
        try:
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            # If the dialog itself fails to open, release the lock so the button isn't dead.
            self.is_processing = False
            Clock.schedule_once(lambda dt: self.callback(f"❌ Error opening file dialog: {e}"))

    def handle_selection(self, selection):
        if not selection:
            self.is_processing = False # Unlock if cancelled
            return
        
        file_path = selection[0]

        threading.Thread(
            target=self.process_file,
            args=(file_path,),
            daemon=True
        ).start()
        
    def process_file(self, file_path):
        try:
            text = self.extract_text(file_path)

            if not text.strip():
                Clock.schedule_once(lambda dt: self.callback("⚠️ File has no readable text."))
                return

            Clock.schedule_once(lambda dt: self.callback(text))

        except Exception as e:
            # Capture the exception as a string immediately
            error_message = f"❌ Error: {str(e)}"
            # Pass the captured string into the lambda
            Clock.schedule_once(lambda dt: self.callback(error_message))
            
        finally:
            # RELEASE LOCK (Delayed slightly to catch rogue plyer double-fires)
            Clock.schedule_once(lambda dt: self._unlock(), 1)
            
    def _unlock(self):
        self.is_processing = False
    
    def extract_image_text(self, file_path):
        # Unicode-safe read: cv2.imread silently returns None on Windows paths
        # containing non-ASCII chars, so go through numpy + imdecode.
        with open(file_path, "rb") as f:
            buf = np.frombuffer(f.read(), dtype=np.uint8)
        image = cv2.imdecode(buf, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image file")

        # Tesseract wants ~300 DPI text. Upscale small images so glyphs are
        # large enough to be recognised reliably.
        h, w = image.shape[:2]
        target = 1800
        if max(h, w) < target:
            scale = target / max(h, w)
            image = cv2.resize(
                image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
            )

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Light denoise before thresholding.
        gray = cv2.bilateralFilter(gray, 5, 50, 50)

        # Otsu picks the threshold per-image; the old fixed 150 destroyed text
        # on anything with non-white backgrounds or low contrast.
        _, binary = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # If the page came out mostly black (dark-mode screenshot, etc.),
        # invert so Tesseract sees dark text on light background.
        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)

        text = pytesseract.image_to_string(binary, config="--oem 3 --psm 6")

        return self._clean_extracted_text(text)

    def _clean_extracted_text(self, raw):
        """Normalise extracted text into one continuous passage for the summariser."""
        if not raw:
            return ""
        # Stitch hyphenated words split across line breaks: "exam-\nple" -> "example".
        raw = re.sub(r"-\s*\n\s*", "", raw)
        # Collapse every whitespace run (spaces, tabs, newlines) into a single space.
        raw = re.sub(r"\s+", " ", raw)
        return raw.strip()

    def _pdf_text_pypdf2(self, file_path):
        """Best-effort PyPDF2 extraction. Catches errors at every level —
        PdfReader init and page iteration can both raise IndexError on malformed PDFs,
        not just page.extract_text()."""
        chunks = []
        try:
            reader = PdfReader(file_path, strict=False)
            num_pages = 0
            try:
                num_pages = len(reader.pages)
            except Exception:
                pass

            for i in range(num_pages):
                try:
                    page = reader.pages[i]
                    page_text = page.extract_text() or ""
                    if page_text:
                        chunks.append(page_text)
                except Exception:
                    # Skip this page; some PDFs have one bad page that takes down iteration.
                    continue
        except Exception:
            pass
        return "\n".join(chunks)

    def _pdf_text_fitz(self, file_path):
        """PyMuPDF extraction — handles a much wider range of PDFs than PyPDF2."""
        chunks = []
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    try:
                        chunks.append(page.get_text("text") or "")
                    except Exception:
                        continue
        except Exception:
            return ""
        return "\n".join(chunks)

    def _pdf_text_ocr(self, file_path):
        """OCR fallback for scanned PDFs (no embedded text). Requires PyMuPDF
        to render pages to images — Tesseract handles the rest."""
        if not _HAS_FITZ:
            return ""
        chunks = []
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    try:
                        # Render at ~300 DPI for readable OCR.
                        pix = page.get_pixmap(dpi=300, alpha=False)
                        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                            pix.height, pix.width, pix.n
                        )
                        if pix.n >= 3:
                            gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2GRAY)
                        else:
                            gray = img[:, :, 0]
                        _, binary = cv2.threshold(
                            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                        )
                        page_text = pytesseract.image_to_string(
                            binary, config="--oem 3 --psm 6"
                        )
                        if page_text:
                            chunks.append(page_text)
                    except Exception:
                        continue
        except Exception:
            return ""
        return "\n".join(chunks)

    def extract_pdf_text(self, file_path):
        # Prefer PyMuPDF when available; fall back to PyPDF2; finally OCR the pages.
        text = self._pdf_text_fitz(file_path) if _HAS_FITZ else ""
        if len(text.strip()) < 50:
            pypdf2_text = self._pdf_text_pypdf2(file_path)
            if len(pypdf2_text.strip()) > len(text.strip()):
                text = pypdf2_text
        if len(text.strip()) < 50:
            # Likely a scanned PDF — render pages and OCR them.
            ocr_text = self._pdf_text_ocr(file_path)
            if len(ocr_text.strip()) > len(text.strip()):
                text = ocr_text
        return self._clean_extracted_text(text)

    def extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        elif ext == ".pdf":
            return self.extract_pdf_text(file_path)

        elif ext in [".png", ".jpg", ".jpeg"]:
            return self.extract_image_text(file_path)

        else:
            raise ValueError("Unsupported file type")