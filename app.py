import sys
import subprocess
import importlib


# ==========================================
# AUTO INSTALL REQUIRED PYTHON PACKAGES
# ==========================================

REQUIRED_PACKAGES = {
    "yt_dlp": "yt-dlp",
    "customtkinter": "customtkinter"
}


def install_package(package):
    """Install a missing Python package."""
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        package
    ])


def check_packages():
    """Check and install required packages."""

    for module, package in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module)

        except ImportError:
            try:
                install_package(package)

            except Exception as error:
                print(f"Could not install {package}: {error}")
                sys.exit(1)


check_packages()


# ==========================================
# IMPORTS
# ==========================================

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp


# ==========================================
# APP SETTINGS
# ==========================================

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# ==========================================
# MAIN APPLICATION
# ==========================================

class VideoDownloader(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("Video Downloader By Adolf")
        self.geometry("700x480")
        self.minsize(700, 480)

        self.cancel_requested = False

        # Default download folder
        self.download_path = os.path.join(
            os.path.expanduser("~"),
            "Downloads"
        )

        self.create_widgets()


    # ==========================================
    # CREATE GUI
    # ==========================================

    def create_widgets(self):

        # Main title
        title = ctk.CTkLabel(
            self,
            text="🎬 Video Downloader By Adolf",
            font=("Arial", 30, "bold")
        )

        title.pack(
            pady=(30, 25)
        )


        # ------------------------------------------
        # VIDEO URL
        # ------------------------------------------

        url_label = ctk.CTkLabel(
            self,
            text="Video URL",
            font=("Arial", 16)
        )

        url_label.pack(
            anchor="w",
            padx=50
        )


        self.url_entry = ctk.CTkEntry(
            self,
            width=600,
            height=45,
            placeholder_text="Paste video URL here..."
        )

        self.url_entry.pack(
            padx=50,
            pady=(5, 25)
        )


        # ------------------------------------------
        # SAVE LOCATION
        # ------------------------------------------

        path_label = ctk.CTkLabel(
            self,
            text="Save Location",
            font=("Arial", 16)
        )

        path_label.pack(
            anchor="w",
            padx=50
        )


        path_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        path_frame.pack(
            padx=50,
            pady=(5, 20),
            fill="x"
        )


        self.path_entry = ctk.CTkEntry(
            path_frame,
            height=45
        )

        self.path_entry.insert(
            0,
            self.download_path
        )

        self.path_entry.pack(
            side="left",
            fill="x",
            expand=True
        )


        self.browse_button = ctk.CTkButton(
            path_frame,
            text="📁 Browse",
            width=120,
            height=45,
            command=self.select_folder
        )

        self.browse_button.pack(
            side="right",
            padx=(10, 0)
        )


        # ------------------------------------------
        # DOWNLOAD BUTTON
        # ------------------------------------------

        self.download_button = ctk.CTkButton(
            self,
            text="⬇ Download",
            width=300,
            height=50,
            font=("Arial", 18, "bold"),
            command=self.start_download
        )

        self.download_button.pack(
            pady=(5, 20)
        )


        # ------------------------------------------
        # PROGRESS BAR
        # ------------------------------------------

        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=600,
            height=18
        )

        self.progress_bar.pack(
            pady=(0, 10)
        )

        self.progress_bar.set(0)


        # ------------------------------------------
        # STATUS LABEL
        # ------------------------------------------

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Arial", 15)
        )

        self.status_label.pack(
            pady=(5, 20)
        )


    # ==========================================
    # SELECT DOWNLOAD FOLDER
    # ==========================================

    def select_folder(self):

        folder = filedialog.askdirectory(
            initialdir=self.path_entry.get()
        )

        if folder:

            self.download_path = folder

            self.path_entry.delete(
                0,
                "end"
            )

            self.path_entry.insert(
                0,
                folder
            )


    # ==========================================
    # START DOWNLOAD
    # ==========================================

    def start_download(self):

        url = self.url_entry.get().strip()

        save_path = self.path_entry.get().strip()


        # Check URL
        if not url:

            messagebox.showwarning(
                "Missing URL",
                "Please enter a video URL."
            )

            return


        # Check download path
        if not save_path:

            messagebox.showwarning(
                "Missing Folder",
                "Please select a download folder."
            )

            return


        # Create folder if needed
        try:
            os.makedirs(
                save_path,
                exist_ok=True
            )

        except Exception as error:

            messagebox.showerror(
                "Folder Error",
                f"Could not create the folder:\n{error}"
            )

            return


        # Disable controls while downloading
        self.download_button.configure(
            state="disabled",
            text="Downloading..."
        )

        self.browse_button.configure(
            state="disabled"
        )


        # Reset progress
        self.progress_bar.set(0)

        self.status_label.configure(
            text="Starting download..."
        )


        # Start download in background
        download_thread = threading.Thread(
            target=self.download_video,
            args=(url, save_path),
            daemon=True
        )

        download_thread.start()


    # ==========================================
    # PROGRESS HOOK
    # ==========================================

    def progress_hook(self, data):

        status = data.get("status")


        # Downloading
        if status == "downloading":

            downloaded = data.get(
                "downloaded_bytes",
                0
            )

            total = (
                data.get("total_bytes")
                or data.get("total_bytes_estimate")
            )


            if total and total > 0:

                percent = downloaded / total

                percent = max(
                    0,
                    min(percent, 1)
                )


                # Update GUI safely
                self.after(
                    0,
                    lambda p=percent:
                    self.progress_bar.set(p)
                )


                self.after(
                    0,
                    lambda p=percent:
                    self.status_label.configure(
                        text=f"Downloading... {p * 100:.1f}%"
                    )
                )


        # File downloaded
        elif status == "finished":

            self.after(
                0,
                lambda:
                self.progress_bar.set(1)
            )


            self.after(
                0,
                lambda:
                self.status_label.configure(
                    text="Download finished. Processing file..."
                )
            )


    # ==========================================
    # DOWNLOAD VIDEO
    # ==========================================

    def download_video(
        self,
        url,
        save_path
    ):

        options = {

            # Save file in selected folder
            "outtmpl": os.path.join(
                save_path,
                "%(title)s.%(ext)s"
            ),

            # Progress callback
            "progress_hooks": [
                self.progress_hook
            ],

            # Download one video
            "noplaylist": True,

            # Better filenames
            "restrictfilenames": False,

            # No unnecessary console output
            "quiet": True,

            # Show errors internally
            "no_warnings": True
        }


        try:

            with yt_dlp.YoutubeDL(
                options
            ) as ydl:

                ydl.download([
                    url
                ])


            # Success
            self.after(
                0,
                lambda:
                self.download_complete(save_path)
            )


        except Exception as error:

            # Error
            self.after(
                0,
                lambda e=str(error):
                self.download_error(e)
            )


    # ==========================================
    # DOWNLOAD COMPLETE
    # ==========================================

    def download_complete(
        self,
        save_path
    ):

        self.progress_bar.set(1)


        self.status_label.configure(
            text="✓ Download completed successfully!"
        )


        self.download_button.configure(
            state="normal",
            text="⬇ Download"
        )


        self.browse_button.configure(
            state="normal"
        )


        messagebox.showinfo(
            "Download Complete",
            f"Video downloaded successfully!\n\nSaved to:\n{save_path}"
        )


    # ==========================================
    # DOWNLOAD ERROR
    # ==========================================

    def download_error(
        self,
        error
    ):

        self.progress_bar.set(0)


        self.status_label.configure(
            text="✗ Download failed."
        )


        self.download_button.configure(
            state="normal",
            text="⬇ Download"
        )


        self.browse_button.configure(
            state="normal"
        )


        messagebox.showerror(
            "Download Error",
            f"The video could not be downloaded.\n\n{error[:500]}"
        )


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    app = VideoDownloader()

    app.mainloop()