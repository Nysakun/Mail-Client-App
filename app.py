"""
Simple Mail Client — Tkinter UI.
Flow: Login screen -> Main app (Compose tab + Inbox tab).
Run with: python app.py
"""

import tkinter as tk
from tkinter import messagebox, ttk
import threading
from email_service import send_email, verify_login, fetch_inbox


class MailApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Mail Client")
        self.geometry("650x550")

        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.pack(fill="both", expand=True)
        self.main_frame = None

    def on_login_success(self, email_addr, app_password):
        self.login_frame.pack_forget()
        self.main_frame = MainFrame(self, email_addr, app_password)
        self.main_frame.pack(fill="both", expand=True)


class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success

        tk.Label(self, text="Login", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Label(self, text="Email:").pack()
        self.email_entry = tk.Entry(self, width=35)
        self.email_entry.pack(pady=5)

        tk.Label(self, text="App Password:").pack()
        self.pwd_entry = tk.Entry(self, width=35, show="*")
        self.pwd_entry.pack(pady=5)

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=5)

        tk.Button(self, text="Login", command=self.attempt_login, width=15).pack(pady=15)

        tk.Label(
            self,
            text="Use a Gmail App Password, not your normal password.\n"
                 "(Google Account -> Security -> 2-Step Verification -> App Passwords)",
            fg="gray", wraplength=420, justify="center"
        ).pack(pady=10)

    def attempt_login(self):
        email_addr = self.email_entry.get().strip()
        password = self.pwd_entry.get().strip()

        if not email_addr or not password:
            self.status_label.config(text="Please enter both fields.")
            return

        self.status_label.config(text="Checking credentials...", fg="blue")

        def do_verify():
            success, msg = verify_login(email_addr, password)
            if success:
                self.after(0, lambda: self.on_success(email_addr, password))
            else:
                self.after(0, lambda: self.status_label.config(text=msg, fg="red"))

        threading.Thread(target=do_verify, daemon=True).start()


class MainFrame(tk.Frame):
    def __init__(self, master, email_addr, app_password):
        super().__init__(master)
        self.email_addr = email_addr
        self.app_password = app_password
        self.emails_cache = []

        tk.Label(self, text=f"Logged in as: {email_addr}", font=("Arial", 10, "italic")).pack(pady=5)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.compose_tab = tk.Frame(notebook)
        self.inbox_tab = tk.Frame(notebook)
        notebook.add(self.compose_tab, text="Compose")
        notebook.add(self.inbox_tab, text="Inbox")

        self.build_compose_tab()
        self.build_inbox_tab()

    # ---------- Compose ----------
    def build_compose_tab(self):
        f = self.compose_tab
        tk.Label(f, text="To:").pack(anchor="w", padx=10, pady=(10, 0))
        self.to_entry = tk.Entry(f, width=65)
        self.to_entry.pack(padx=10)

        tk.Label(f, text="Subject:").pack(anchor="w", padx=10, pady=(10, 0))
        self.subject_entry = tk.Entry(f, width=65)
        self.subject_entry.pack(padx=10)

        tk.Label(f, text="Body:").pack(anchor="w", padx=10, pady=(10, 0))
        self.body_text = tk.Text(f, width=65, height=14)
        self.body_text.pack(padx=10, pady=5)

        self.send_status = tk.Label(f, text="", fg="green")
        self.send_status.pack()

        tk.Button(f, text="Send", command=self.handle_send, width=15).pack(pady=10)

    def handle_send(self):
        to_addr = self.to_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", "end").strip()

        if not to_addr or not subject:
            self.send_status.config(text="To and Subject are required.", fg="red")
            return

        self.send_status.config(text="Sending...", fg="blue")

        def do_send():
            success, msg = send_email(self.email_addr, self.app_password, to_addr, subject, body)
            color = "green" if success else "red"
            self.after(0, lambda: self.send_status.config(text=msg, fg=color))

        threading.Thread(target=do_send, daemon=True).start()

    # ---------- Inbox ----------
    def build_inbox_tab(self):
        f = self.inbox_tab
        tk.Button(f, text="Refresh Inbox", command=self.refresh_inbox).pack(pady=10)

        list_frame = tk.Frame(f)
        list_frame.pack(fill="both", expand=True, padx=10)

        self.email_listbox = tk.Listbox(list_frame, width=85, height=10)
        self.email_listbox.pack(side="left", fill="both", expand=True)
        self.email_listbox.bind("<<ListboxSelect>>", self.show_selected_email)

        scrollbar = tk.Scrollbar(list_frame, command=self.email_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.email_listbox.config(yscrollcommand=scrollbar.set)

        tk.Label(f, text="Email content:").pack(anchor="w", padx=10, pady=(10, 0))
        self.email_body_view = tk.Text(f, width=85, height=10, state="disabled")
        self.email_body_view.pack(padx=10, pady=5)

    def refresh_inbox(self):
        self.email_listbox.delete(0, "end")

        def do_fetch():
            success, result = fetch_inbox(self.email_addr, self.app_password, limit=15)

            def update_ui():
                if success:
                    self.emails_cache = result
                    for mail in self.emails_cache:
                        display = f"{mail['from']}  |  {mail['subject']}"
                        self.email_listbox.insert("end", display)
                else:
                    messagebox.showerror("Error", result)

            self.after(0, update_ui)

        threading.Thread(target=do_fetch, daemon=True).start()

    def show_selected_email(self, event):
        selection = self.email_listbox.curselection()
        if not selection:
            return
        mail = self.emails_cache[selection[0]]
        content = f"From: {mail['from']}\nDate: {mail['date']}\nSubject: {mail['subject']}\n\n{mail['body']}"
        self.email_body_view.config(state="normal")
        self.email_body_view.delete("1.0", "end")
        self.email_body_view.insert("1.0", content)
        self.email_body_view.config(state="disabled")


if __name__ == "__main__":
    app = MailApp()
    app.mainloop() 