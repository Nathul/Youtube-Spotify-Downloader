import customtkinter as ctk
from tkinter import filedialog, messagebox, Toplevel
import yt_dlp
import threading
import sys
import os
from datetime import datetime
from queue import Queue, Empty


class ConsoleRedirect:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        if text.strip():
            self.queue.put(text)

    def flush(self):
        pass


class CyberCrackFlux(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Hide window until password is verified
        self.withdraw()

        self.title("Cyber-Crack Flux")
        self.geometry("950x700")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0F111A")

        self.default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.path_mode = "default"
        self.download_active = False
        self.stop_requested = False
        self.log_window = None
        self.log_text = None
        self.log_queue = Queue()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_ui()

        self.after(100, self.show_startup_password)

    def create_ui(self):
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#090B10")
        sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(sidebar, text="HISTORY", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 10))

        self.history_box = ctk.CTkTextbox(sidebar, fg_color="transparent", text_color="#888888", font=("Inter", 11))
        self.history_box.pack(expand=True, fill="both", padx=10, pady=10)
        self.reset_history_display()

        ctk.CTkButton(sidebar, text="CLEAR LOGS", command=self.clear_history,
                      fg_color="transparent", border_width=1).pack(pady=5, padx=20)

        ctk.CTkButton(sidebar, text="⚙ SETTINGS", command=self.open_settings,
                      fg_color="transparent", border_width=1).pack(pady=5, padx=20)

        # Main content
        console = ctk.CTkFrame(self, fg_color="transparent")
        console.grid(row=0, column=1, padx=40, pady=40, sticky="nsew")

        ctk.CTkLabel(console, text="C Y B E R - C R A C K",
                     font=ctk.CTkFont(size=38, weight="bold")).pack(pady=(0, 0))

        ctk.CTkLabel(console, text="ULTRA-FAST MEDIA EXTRACTION", text_color="#555555").pack(pady=(0, 30))

        self.service_var = ctk.StringVar(value="youtube")
        service_frame = ctk.CTkFrame(console, fg_color="transparent")
        service_frame.pack(pady=10)

        ctk.CTkRadioButton(service_frame, text="YOUTUBE", variable=self.service_var, value="youtube",
                           command=self.on_service_change, fg_color="#7B61FF").pack(side="left", padx=20)
        ctk.CTkRadioButton(service_frame, text="SPOTIFY", variable=self.service_var, value="spotify",
                           command=self.on_service_change, fg_color="#1DB954").pack(side="left", padx=20)

        self.url_entry = ctk.CTkEntry(console, placeholder_text="Enter YouTube URL...", width=500, height=45,
                                      corner_radius=10, fg_color="#161925")
        self.url_entry.pack(pady=20)

        self.format_var = ctk.StringVar(value="best")
        format_frame = ctk.CTkFrame(console, fg_color="transparent")
        format_frame.pack(pady=10)

        for text, mode in [("4K / BEST", "best"), ("1080P", "1080"), ("MP3", "mp3")]:
            ctk.CTkRadioButton(format_frame, text=text, variable=self.format_var, value=mode,
                               fg_color="#7B61FF").pack(side="left", padx=20)

        self.path_selector = ctk.CTkSegmentedButton(console, values=["DEFAULT", "CUSTOM"],
                                                    command=self.set_path_mode, selected_color="#7B61FF")
        self.path_selector.set("DEFAULT")
        self.path_selector.pack(pady=20)

        self.prog_label = ctk.CTkLabel(console, text="SYSTEM READY", font=("Inter", 12))
        self.prog_label.pack(pady=(20, 5))

        self.bar = ctk.CTkProgressBar(console, width=500, height=4, progress_color="#7B61FF")
        self.bar.set(0)
        self.bar.pack()

        btn_frame = ctk.CTkFrame(console, fg_color="transparent")
        btn_frame.pack(pady=30)

        self.execute_btn = ctk.CTkButton(btn_frame, text="EXECUTE", command=self.start_download,
                                         fg_color="#7B61FF", hover_color="#5E44FF", height=50, width=180,
                                         corner_radius=25, font=ctk.CTkFont(weight="bold"))
        self.execute_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(btn_frame, text="STOP", command=self.request_stop,
                                      fg_color="#FF4B4B", hover_color="#CC3333", height=50, width=140,
                                      corner_radius=25, font=ctk.CTkFont(weight="bold"),
                                      state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        self.details_btn = ctk.CTkButton(btn_frame, text="DETAILS", command=self.show_details_window,
                                         fg_color="#3A3F5A", hover_color="#2C314A", height=50, width=140,
                                         corner_radius=25, font=ctk.CTkFont(weight="bold"),
                                         state="disabled")
        self.details_btn.pack(side="left", padx=10)

        self.after(150, self.process_log_queue)

    def show_startup_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Authorization Required")
        dialog.geometry("440x300")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#121521")

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text="CYBER-CRACK ACCESS", font=("Segoe UI", 18, "bold"),
                     text_color="#7B61FF").pack(pady=(40, 10))

        ctk.CTkLabel(dialog, text="Enter the authorization code", 
                     font=("Segoe UI", 12), text_color="gray").pack(pady=(0, 25))

        pass_entry = ctk.CTkEntry(dialog, show="*", width=280, height=44, 
                                  fg_color="#1A1F2E", border_color="#7B61FF", 
                                  placeholder_text="Enter code here...")
        pass_entry.pack(pady=10)
        pass_entry.focus()

        def verify():
            if pass_entry.get().strip() == "`":
                dialog.destroy()
                self.deiconify()
                self.focus_force()
            else:
                messagebox.showerror("Access Denied", "Wrong code.", parent=dialog)
                pass_entry.delete(0, "end")
                pass_entry.focus()

        def on_closing():
            dialog.destroy()
            self.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_closing)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=30)

        ctk.CTkButton(btn_frame, text="ENTER", command=verify,
                      fg_color="#7B61FF", hover_color="#5E44FF", width=140).pack(side="left", padx=15)

        ctk.CTkButton(btn_frame, text="EXIT", command=on_closing,
                      fg_color="transparent", border_width=2, text_color="gray", width=140).pack(side="left", padx=15)

        dialog.bind("<Return>", lambda e: verify())

    def set_path_mode(self, value):
        self.path_mode = value.lower()

    def on_service_change(self):
        srv = self.service_var.get()
        self.url_entry.configure(placeholder_text=f"Enter {srv.capitalize()} URL...")

    def reset_history_display(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("0.0", "end")
        self.history_box.insert("0.0", "No recent logs...")
        self.history_box.configure(state="disabled")

    def clear_history(self):
        self.reset_history_display()

    def open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Settings")
        win.geometry("400x300")
        win.attributes("-topmost", True)
        ctk.CTkLabel(win, text="DEFAULT PATH", font=("Inter", 13, "bold")).pack(pady=20)
        lbl = ctk.CTkLabel(win, text=self.default_path, wraplength=300, text_color="gray")
        lbl.pack(pady=10)

        def browse():
            p = filedialog.askdirectory()
            if p:
                self.default_path = p
                lbl.configure(text=p)

        ctk.CTkButton(win, text="SET NEW PATH", command=browse).pack(pady=10)
        ctk.CTkButton(win, text="SAVE", command=win.destroy, fg_color="#7B61FF").pack(pady=10)

    def update_history(self, title):
        self.history_box.configure(state="normal")
        if "No recent logs..." in self.history_box.get("0.0", "end"):
            self.history_box.delete("0.0", "end")
        stamp = datetime.now().strftime("%H:%M")
        self.history_box.insert("0.0", f"[{stamp}] {title[:40]}...\n")
        self.history_box.configure(state="disabled")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a URL")
            return

        save_path = self.default_path
        if self.path_mode == "custom":
            save_path = filedialog.askdirectory()
            if not save_path:
                return

        self.stop_requested = False
        self.bar.set(0)
        self.bar.configure(mode="indeterminate")
        self.bar.start()
        self.prog_label.configure(text="INITIALIZING...", text_color="#7B61FF")

        self.execute_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.details_btn.configure(state="normal")

        self.download_active = True
        threading.Thread(target=self.download_task, args=(url, save_path), daemon=True).start()

    def request_stop(self):
        if not self.download_active:
            return
        if messagebox.askyesno("Confirm Stop", "Stop the current download?"):
            self.stop_requested = True
            self.prog_label.configure(text="STOPPING...", text_color="#FFAA00")
            self.stop_btn.configure(state="disabled")

    def download_task(self, url, save_path):
        redirector = ConsoleRedirect(self.log_queue)
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = redirector
        sys.stderr = redirector

        try:
            ydl_opts = {
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'noplaylist': False,           # allow playlists
                'ignoreerrors': True,          # ← IMPORTANT: continue on errors
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [self.progress_hook],
                'playliststart': 1,            # start from beginning
                'playlistend': None,           # download all
            }

            if self.format_var.get() == "mp3" or self.service_var.get() == "spotify":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                })
            elif self.format_var.get() == "1080":
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

            if self.service_var.get() == "spotify":
                url = f"ytsearch:{url}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.stop_requested:
                    raise Exception("Stopped by user")

                # Extract info and download – ignoreerrors=True will skip problematic entries
                info = ydl.extract_info(url, download=True)

                # If playlist, log successful title (first item or overall)
                if 'entries' in info and info['entries']:
                    successful_titles = [entry.get('title', 'Unknown') for entry in info['entries'] if entry.get('title')]
                    if successful_titles:
                        self.after(0, lambda t=successful_titles[0]: self.update_history(t + " (playlist)"))
                else:
                    title = info.get('title', 'Unknown')
                    self.after(0, lambda t=title: self.update_history(t))

                self.after(0, lambda: self.prog_label.configure(text="COMPLETE", text_color="#00FF88"))

        except Exception as e:
            msg = "Download stopped by user" if self.stop_requested else str(e)
            self.log_queue.put(f"\n[STOP/ERROR] {msg}\n")
            self.after(0, lambda: self.prog_label.configure(text="STOPPED / FAILED", text_color="#FF5555"))

        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            self.after(0, lambda: self.bar.stop())
            self.after(0, lambda: self.bar.configure(mode="determinate"))
            self.after(0, lambda: self.bar.set(0))
            self.after(0, lambda: self.execute_btn.configure(state="normal", text="EXECUTE"))
            self.after(0, lambda: self.stop_btn.configure(state="disabled"))
            self.download_active = False
            self.log_queue.put("\n" + "═" * 80 + "\n\n")

    def progress_hook(self, d):
        if self.stop_requested:
            raise Exception("Interrupted by user")

        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '—')
            eta = d.get('_eta_str', '—')
            self.after(0, lambda: self.prog_label.configure(text=f"DOWNLOADING  •  {percent}  •  {speed}  •  ETA {eta}"))
            self.after(0, lambda: self.bar.configure(mode="determinate"))
            self.after(0, lambda: self.bar.stop())
            try:
                p = float(percent.strip('%')) / 100
                self.after(0, lambda v=p: self.bar.set(v))
            except:
                pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.prog_label.configure(text="PROCESSING..."))

    def show_details_window(self):
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.lift()
            return

        self.log_window = Toplevel(self)
        self.log_window.title("Download Details")
        self.log_window.geometry("900x600")
        self.log_window.configure(bg="#0a0e14")

        ctk.CTkLabel(self.log_window, text="yt-dlp Output", font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.log_text = ctk.CTkTextbox(self.log_window, fg_color="#0a0e14", text_color="#d0d8ff",
                                       font=("Consolas", 11), wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def process_log_queue(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                if self.log_text and self.log_window and self.log_window.winfo_exists():
                    self.log_text.insert("end", line)
                    self.log_text.see("end")
        except Empty:
            pass
        self.after(150, self.process_log_queue)


if __name__ == "__main__":
    app = CyberCrackFlux()
    app.mainloop()