import os # Imports the operating system module (used for file path manipulations).
from plyer import filechooser # Imports the plyer tool to open native file explorer windows.
from PyPDF2 import PdfReader # Imports the PDF processing library to read and extract text.
import threading # Imports the module used to run tasks in the background so the app doesn't freeze.
from kivy.clock import Clock # Imports the Kivy timer tool to safely send data from a background thread back to the UI.

class FileUploadManager: # Declares a new class to manage file uploading logic.
    def __init__(self, callback):
        self.callback = callback

    def open_file_dialog(self):
        filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        if not selection:
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
                self.callback("⚠️ File has no readable text.")
                return

            Clock.schedule_once(lambda dt: self.callback(text))

        except Exception as e:
            self.callback(f"❌ Error: {e}")

    def extract_text(self, file_path):
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read() # Read and return the content

        elif file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                # Use 'or ""' to handle pages where extract_text might return None
                text += (page.extract_text() or "") + "\n"
            return text

        else:
            raise ValueError("Unsupported file type")