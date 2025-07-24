import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel
from PIL import Image, ImageTk
from user_registration import UserRegistrationApp
from encryption import encrypt_file_aes, encrypt_aes_key_with_rsa, generate_rsa_key_pair, generate_aes_key
from decryption_file import decrypt_file_aes, decrypt_aes_key_with_rsa

import os

registered_users = {}  # Store registered users' details (username: (password, email, phone, profile_image_path))
encryption_keys = {}  # Store encryption keys for each user (username: RSA private key)


class MainApp:
    def __init__(self, master):

        self.master = master
        master.title("Cloud File Manager")

        # Load background image
        background_image = Image.open(r"C:/Users/91772\Pictures\img\background.png")
        self.background_photo = ImageTk.PhotoImage(
            background_image.resize((master.winfo_screenwidth(), master.winfo_screenheight()), Image.LANCZOS))
        background_label = tk.Label(master, image=self.background_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.username = ""

        # Specify the path where you want to create the folders
        self.base_folder = 'C:/Users/91772/Desktop/march15'

        # Create folders for storing encrypted and decrypted files
        self.encrypted_folder = os.path.join(self.base_folder, "encrypted")
        self.decrypted_folder = os.path.join(self.base_folder, "decrypted")

        # Create the folders
        os.makedirs(self.encrypted_folder, exist_ok=True)
        os.makedirs(self.decrypted_folder, exist_ok=True)

        # Heading
        heading_label = tk.Label(master, text="Secure File Storage Using Hybrid Cryptography", font=("Helvetica", 24), fg="white",
                                 bg="black")
        heading_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        # Login window
        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("Login")

        tk.Label(self.login_window, text="Username:").grid(row=0, column=0, sticky="e")
        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_window, text="Password:").grid(row=1, column=0, sticky="e")
        self.password_entry = tk.Entry(self.login_window, show='*')
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_window, text="Login", command=self.validate_login).grid(row=2, columnspan=2, pady=5)

        # Hide login window initially
        self.login_window.withdraw()
        # Register button
        register_button = tk.Button(master, text="Register", command=self.register_user, width=20)
        register_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        # Login button
        login_button = tk.Button(master, text="Login", command=self.show_login, width=20)
        login_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    def register_user(self):
        registration_window = tk.Toplevel(self.master)
        UserRegistrationApp(registration_window, registered_users)

    def show_login(self):
        self.login_window.deiconify()

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in registered_users and registered_users[username][0] == password:
            self.username = username
            self.login_window.withdraw()
            self.show_file_manager()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def show_file_manager(self):
        file_manager_window = tk.Toplevel(self.master)
        file_manager_window.title("File Manager")

        file_manager_window.config(bg="light blue")
        tk.Button(file_manager_window, text="Upload and Encrypt File", command=self.upload_file).pack(pady=10)
        tk.Button(file_manager_window, text="Decrypt File", command=self.decrypt_button_clicked).pack(pady=5)

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            aes_key = generate_aes_key()
            input_file_path = file_path

            # Specify the directory where the encrypted file will be saved
            encryption_folder = os.path.join(self.base_folder, "encrypted", self.username)
            os.makedirs(encryption_folder, exist_ok=True)

            # File paths
            encrypted_file_name = os.path.basename(file_path) + ".enc"
            output_file_path = os.path.join(encryption_folder, encrypted_file_name)

            # Encrypt the file with AES
            encrypt_file_aes(input_file_path, aes_key, output_file_path)

            # Key storage paths
            keys_folder = os.path.join(encryption_folder, 'keys')
            os.makedirs(keys_folder, exist_ok=True)
            private_key_path = os.path.join(keys_folder, 'private.pem')
            public_key_path = os.path.join(keys_folder, 'public.pem')
            aes_key_enc_path = os.path.join(keys_folder, 'aes_key.enc')

            # Generate RSA keys and encrypt AES key
            generate_rsa_key_pair(private_key_path, public_key_path)
            encrypt_aes_key_with_rsa(aes_key, public_key_path, aes_key_enc_path)

            messagebox.showinfo("Success", "File encrypted and uploaded successfully.")
        else:
            messagebox.showerror("Error", "No file selected.")

    def decrypt_button_clicked(self):
        # Ask the user to select the encrypted file
        selected_file_path = filedialog.askopenfilename(title="Select Encrypted File")
        if not selected_file_path:
            messagebox.showerror("Error", "No file selected.")
            return

        # Ask the user to select the encrypted AES key
        aes_key_enc_path = filedialog.askopenfilename(title="Select Encrypted AES Key")
        if not aes_key_enc_path:
            messagebox.showerror("Error", "No encrypted AES key selected.")
            return

        # Ask the user to select the RSA private key
        private_key_path = filedialog.askopenfilename(title="Select RSA Private Key")
        if not private_key_path:
            messagebox.showerror("Error", "No RSA private key selected.")
            return

        # Call the decryption functions
        aes_key = decrypt_aes_key_with_rsa(aes_key_enc_path, private_key_path)
        output_file_path = os.path.join(self.decrypted_folder,
                                        os.path.basename(selected_file_path)[:-4])  # Remove '.enc' extension
        decrypt_file_aes(selected_file_path, aes_key, output_file_path)

        # Show a message indicating that decryption is complete
        messagebox.showinfo("Decryption Complete", "File decrypted successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
