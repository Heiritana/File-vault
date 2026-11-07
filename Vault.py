import base64
import hashlib
import json
import os
import pyAesCrypt
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from tkinterdnd2 import *
from tkinter import ttk
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


# Class to initialize all frames and to manage interactions
class MainApp(Tk):
    def __init__(self):
        super().__init__()
        self.title('File Vault')
        self.geometry('530x330')
        self.configure(bg='#f0f0f0')
        self.encrypted_files = []
        self.frames = {}
        self.setup_styles()
        self.setup_frames()
        self.switch_frame('CreatePasswordFrame' if not self.password_file_exists() else 'LoginFrame')

    def setup_styles(self):
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10))

    def setup_frames(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        for F in (CreatePasswordFrame, LoginFrame, MainMenu, EncryptFrame, ViewFrame, CredentialsFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def password_file_exists(self):
        return os.path.exists(".master_password")

    def switch_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

        if hasattr(frame, 'update_list'):
            frame.update_list()

    def verify_password(self, password):
        try:
            with open(".master_password", "r") as f:
                data = json.load(f)
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(data['salt']), data['iterations'])
            return hashlib.sha256(key).hexdigest() == data['hash']
        except Exception as e:
            messagebox.showerror("Error", f"Password verification failed: {str(e)}")
            return False

    def reset_application(self):
        for frame_name, frame in self.frames.items():
            if hasattr(frame, 'entry_password'):
                frame.entry_password.delete(0, END)
            if hasattr(frame, 'entry_new'):
                frame.entry_new.delete(0, END)
            if hasattr(frame, 'entry_confirm'):
                frame.entry_confirm.delete(0, END)
        try:
            for file in [".master_password", ".encrypted_info", ".credentials"]:
                if os.path.exists(file):
                    os.remove(file)

            script_dir =  os.getcwd()
            for folder in ["encrypted_files", "decrypted_files"]:
                folder_path = os.path.join(script_dir, folder)
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(folder_path)

            self.encrypted_files.clear()
            messagebox.showinfo("Success", "All data have been reset.")
            self.switch_frame('CreatePasswordFrame')
        except Exception as e:
            messagebox.showerror("Error", f"Reset failed: {str(e)}")

    def encrypt_data(self, data, password):
        try:
            salt, iv = get_random_bytes(16), get_random_bytes(16)
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(pad(json.dumps(data).encode(), AES.block_size))
            return base64.b64encode(salt + iv + encrypted).decode()
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")
            return None

    def decrypt_data(self, encrypted_data, password):
        try:
            data = base64.b64decode(encrypted_data)
            salt, iv, encrypted = data[:16], data[16:32], data[32:]
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return json.loads(unpad(cipher.decrypt(encrypted), AES.block_size).decode())
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
            return None


# Class to link the others classes
class BaseFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller


# Class to manage the password creation and storage
class CreatePasswordFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="Create Master Password", font=("Arial", 16)).grid(row=0, column=0, pady=20, columnspan=2)
        ttk.Label(self, text="New Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_new = ttk.Entry(self, show="*")
        self.entry_new.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self, text="Confirm Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_confirm = ttk.Entry(self, show="*")
        self.entry_confirm.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self, text="Create Password", command=self.create_password).grid(row=3, column=0, columnspan=2, pady=10)

    def create_password(self):
        new_password, confirm_password = self.entry_new.get(), self.entry_confirm.get()
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords don't match!")
            return
        try:
            salt, iterations = get_random_bytes(16), 100000
            key = hashlib.pbkdf2_hmac('sha256', new_password.encode(), salt, iterations)
            key_hash = hashlib.sha256(key).hexdigest()
            with open(".master_password", "w") as f:
                json.dump({"salt": base64.b64encode(salt).decode(), "iterations": iterations, "hash": key_hash}, f)
            os.system('attrib +h ".master_password"')
            messagebox.showinfo("Success", "Password created!")
            self.controller.switch_frame('LoginFrame')
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")


# Class to handle the login feature
class LoginFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        ttk.Label(self, text="File Vault Login", font=("Arial", 16)).grid(row=0, column=0, pady=20, columnspan=2)
        ttk.Label(self, text="Master Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self, text="Login", command=self.verify_password).grid(row=2, column=0, columnspan=2, pady=10)

    def verify_password(self):
        if self.controller.verify_password(self.entry_password.get()):
            self.controller.switch_frame('MainMenu')
        else:
            messagebox.showerror("Error", "Incorrect password!")

# Class containing the main menu of the application
class MainMenu(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        left_frame = ttk.Frame(self)
        ttk.Label(left_frame, text="File Operations", font=("Arial", 12)).pack(pady=5)
        for text, frame in [("Encrypt File", 'EncryptFrame'), ("View Files", 'ViewFrame'),
                            ("Credentials", 'CredentialsFrame'), ("Reset", self.reset), ("Logout", 'LoginFrame')]:
            ttk.Button(left_frame, text=text, command=(lambda f=frame: controller.switch_frame(f) if isinstance(f, str) else f())).pack(fill=X, pady=2)
        left_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

    def reset(self):
        password = simpledialog.askstring("Verify", "Enter master password to reset:", show='*')
        if password and self.controller.verify_password(password):
            self.controller.reset_application()
        else:
            messagebox.showerror("Error", "Incorrect password")

# Class to take file input and encrypting it with aes
class EncryptFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        file_frame = ttk.LabelFrame(self, text="File Selection")
        self.entry_sv = StringVar(value='Drop files here or click "Browse"')
        self.entry = Entry(file_frame, textvar=self.entry_sv, width=60)
        self.entry.pack(pady=5, padx=5, side=LEFT)
        self.entry.drop_target_register(DND_FILES)
        self.entry.dnd_bind('<<Drop>>', self.drop)
        ttk.Button(file_frame, text="Browse", command=self.choose_file).pack(pady=5, padx=5, side=LEFT)
        file_frame.pack(fill=X, padx=10, pady=10)
        options_frame = ttk.LabelFrame(self, text="Options")
        self.delete_original = BooleanVar()
        ttk.Checkbutton(options_frame, text="Delete original after encryption", variable=self.delete_original).pack(anchor=W)
        options_frame.pack(fill=X, padx=10, pady=5)
        button_frame = ttk.Frame(self)
        ttk.Button(button_frame, text="Encrypt", command=self.encrypt).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=lambda: controller.switch_frame('MainMenu')).pack(side=LEFT, padx=5)
        button_frame.pack(pady=10)

    def choose_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.entry_sv.set(os.path.basename(self.file_path))

    def drop(self, event):
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.file_path = file_path
            self.entry_sv.set(os.path.basename(file_path))

    def encrypt(self):
        if not hasattr(self, 'file_path'):
            messagebox.showerror("Error", "No file selected")
            return

        password = simpledialog.askstring("Password", "Enter master password:", show='*')
        if not password or not self.controller.verify_password(password):
            messagebox.showerror("Error", "Incorrect password")
            return

        try:
            script_dir = os.getcwd()
            encrypted_dir = os.path.join(script_dir, "encrypted_files")
            os.makedirs(encrypted_dir, exist_ok=True)
            os.system(f'attrib +h "{encrypted_dir}"')
            encrypted_filename = os.path.basename(self.file_path) + ".aes"
            encrypted_path = os.path.join(encrypted_dir, encrypted_filename)
            key = os.urandom(32)
            key_base64 = base64.b64encode(key).decode('utf-8')
            sha256 = hashlib.sha256()
            with open(self.file_path, 'rb') as f:
                while chunk := f.read(65536):
                    sha256.update(chunk)
            file_hash = sha256.hexdigest()
            pyAesCrypt.encryptFile(self.file_path, encrypted_path, key_base64, 64 * 1024)

            encrypted_info = {
                "encrypted_path": encrypted_path,
                "key": key_base64,
                "hash": file_hash,
                "original_file": os.path.basename(self.file_path)
            }

            existing_data = []
            if os.path.exists(".encrypted_info"):
                with open(".encrypted_info", "r") as f:
                    encrypted_existing = f.read()
                existing_data = self.controller.decrypt_data(encrypted_existing, password)
                if existing_data is None:
                    messagebox.showerror("Error", "Failed to decrypt existing data. Aborting.")
                    return
            existing_data.append(encrypted_info)
            encrypted_data = self.controller.encrypt_data(existing_data, password)
            if encrypted_data is None:
                return

            with open(".encrypted_info", "w") as f:
                f.write(encrypted_data)
            os.system('attrib +h ".encrypted_info"')

            if self.delete_original.get():
                os.remove(self.file_path)

            messagebox.showinfo("Success", "File encrypted!")
            self.controller.switch_frame('MainMenu')
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Class to give the option to choose an encrypted file and then decrypt it or verify the hash
class ViewFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        list_frame = ttk.LabelFrame(self, text="Encrypted Files")
        self.listbox = Listbox(list_frame, width=80, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        button_frame = ttk.Frame(self)
        for text, cmd in [("Refresh", self.update_list), ("Decrypt Selected", self.decrypt_file),
                          ("Verify Hash", self.verify_hash), ("Back", lambda: controller.switch_frame('MainMenu'))]:
            ttk.Button(button_frame, text=text, command=cmd).pack(side=LEFT, padx=5)
        button_frame.pack(pady=5)

    def update_list(self):
        self.listbox.delete(0, END)
        if os.path.exists(".encrypted_info"):
            password = simpledialog.askstring("Password", "Enter master password:", show='*')
            if not password or not self.controller.verify_password(password):
                messagebox.showerror("Error", "Incorrect password")
                return
            try:
                with open(".encrypted_info", "r") as f:
                    encrypted_data = f.read()
                existing_data = self.controller.decrypt_data(encrypted_data, password)
                if existing_data is None:
                    self.listbox.insert(END, "Failed to decrypt data")
                    return
                for index, item in enumerate(existing_data, 1):
                    self.listbox.insert(END, f"{index}. {os.path.basename(item['encrypted_path'])}")
            except Exception as e:
                self.listbox.insert(END, "Corrupted data file")
        else:
            self.listbox.insert(END, "No encrypted files found")

    def verify_hash(self):
        try:
            password = simpledialog.askstring("Password", "Enter master password:", show='*')
            if not password or not self.controller.verify_password(password):
                messagebox.showerror("Error", "Incorrect password")
                return

            with open(".encrypted_info", "r") as f:
                encrypted_data = f.read()
            existing_data = self.controller.decrypt_data(encrypted_data, password)
            if existing_data is None:
                return

            index = self.listbox.curselection()[0]
            info = existing_data[index]
            stored_hash = info["hash"]
            original_file = filedialog.askopenfilename(title="Select the original file to verify")
            if not original_file:
                return

            sha256 = hashlib.sha256()
            with open(original_file, 'rb') as f:
                while chunk := f.read(65536):
                    sha256.update(chunk)
            calculated_hash = sha256.hexdigest()

            if calculated_hash == stored_hash:
                messagebox.showinfo("Success", "Hashes match!")
            else:
                messagebox.showerror("Error", "Hashes don't match!")
        except Exception as e:
            messagebox.showerror("Error", f"Verification failed: {str(e)}")

    def decrypt_file(self):
        try:
            index = self.listbox.curselection()[0]
            password = simpledialog.askstring("Password", "Enter master password:", show='*')
            if not password or not self.controller.verify_password(password):
                messagebox.showerror("Error", "Incorrect password")
                return

            with open(".encrypted_info", "r") as f:
                encrypted_data = f.read()
            existing_data = self.controller.decrypt_data(encrypted_data, password)
            if existing_data is None:
                raise ValueError("Failed to decrypt data")

            info = existing_data[index]
            password = simpledialog.askstring("Password", "Enter master password:", show='*')
            if not password or not self.controller.verify_password(password):
                messagebox.showerror("Error", "Incorrect password")
                return

            script_dir = os.getcwd()
            decrypted_dir = os.path.join(script_dir, "decrypted_files")
            os.makedirs(decrypted_dir, exist_ok=True)
            original_filename = info['original_file']
            decrypted_path = os.path.join(decrypted_dir, original_filename)
            pyAesCrypt.decryptFile(info['encrypted_path'], decrypted_path, info["key"], 64 * 1024)
            messagebox.showinfo("Success", f"File decrypted to:\n{decrypted_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")

# Class to handle the creation and management of credentials
class CredentialsFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        list_frame = ttk.LabelFrame(self, text="Stored Credentials")
        self.listbox = Listbox(list_frame, width=60, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        button_frame = ttk.Frame(self)
        for text, cmd in [("Add", self.add), ("Copy Password", self.copy),
                          ("Back", lambda: controller.switch_frame('MainMenu'))]:
            ttk.Button(button_frame, text=text, command=cmd).pack(side=LEFT, padx=5)
        button_frame.pack(pady=5)
        self.load()

    def load(self):
        self.listbox.delete(0, END)
        if not os.path.exists(".credentials"):
            return

        password = simpledialog.askstring("Password", "Enter master password:", show='*')
        if not password or not self.controller.verify_password(password):
            messagebox.showerror("Error", "Incorrect password")
            return

        try:
            with open(".credentials", "r") as f:
                creds = self.controller.decrypt_data(f.read(), password)
            if creds:
                for cred in creds:
                    self.listbox.insert(END, cred['username'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load credentials: {str(e)}")

    def add(self):
        username, password = simpledialog.askstring("Username", "Enter username:"), simpledialog.askstring("Password", "Enter password:", show='*')
        master_pwd = simpledialog.askstring("Master Password", "Verify:", show='*')

        if not all([username, password, master_pwd]) or not self.controller.verify_password(master_pwd):
            return

        try:
            creds = self.load_credentials(master_pwd) or []
            iv = get_random_bytes(16)
            encrypted_password = self.encrypt_credential_password(password, master_pwd, iv)
            creds.append({"username": username, "iv": base64.b64encode(iv).decode(), "password": encrypted_password})

            encrypted_data = self.controller.encrypt_data(creds, master_pwd)
            with open(".credentials", "w") as f:
                f.write(encrypted_data)
            os.system('attrib +h ".credentials"')
            self.load()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_credentials(self, master_pwd):
        if os.path.exists(".credentials"):
            with open(".credentials", "r") as f:
                return self.controller.decrypt_data(f.read(), master_pwd)
        return []

    def encrypt_credential_password(self, password, master_pwd, iv):
        with open(".master_password", "r") as f:
            data = json.load(f)
        key = hashlib.pbkdf2_hmac('sha256', master_pwd.encode(), base64.b64decode(data['salt']), data['iterations'])
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(cipher.encrypt(pad(password.encode(), AES.block_size))).decode()

    def copy(self):
        try:
            index = self.listbox.curselection()[0]
            master_pwd = simpledialog.askstring("Master Password", "Enter master password:", show='*')
            if not master_pwd or not self.controller.verify_password(master_pwd):
                return

            creds = self.load_credentials(master_pwd)
            if creds:
                cred = creds[index]
                decrypted_password = self.decrypt_credential_password(cred, master_pwd)

                self.controller.clipboard_clear()
                self.controller.clipboard_append(decrypted_password)
                messagebox.showinfo("Success", "Password copied to clipboard")
        except IndexError:
            messagebox.showerror("Error", "No credential selected")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")

    def decrypt_credential_password(self, cred, master_pwd):
        with open(".master_password", "r") as f:
            data = json.load(f)
        key = hashlib.pbkdf2_hmac('sha256', master_pwd.encode(), base64.b64decode(data['salt']), data['iterations'])
        cipher = AES.new(key, AES.MODE_CBC, base64.b64decode(cred['iv']))
        return unpad(cipher.decrypt(base64.b64decode(cred['password'])), AES.block_size).decode()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()