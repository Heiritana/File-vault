# Python File Vault

An undergraduate Python desktop application developed to explore file encryption, password-based access control, file-integrity checking and local credential storage.

> **Project status:** Academic final-year project (2025). This repository preserves the original submitted implementation. It is provided for educational review and demonstration, not as a production-ready password manager or secure storage product.

## Project context

This project, *Development of file vault system to store confidential files using Python*, was developed as an individual undergraduate final-year project and submitted in April 2025.

The project explored how a desktop application could combine file encryption, a master-password workflow, file-integrity comparison and credential storage in one graphical interface.

The source file `Vault.py` is preserved as the original project implementation. Documentation in this repository describes that implementation.

## Features implemented

* **Master-password setup and login:** creates a master-password record using PBKDF2-HMAC-SHA256 and verifies subsequent login attempts.
* **File encryption:** lets a user select or drag and drop a file for encryption using `pyAesCrypt`.
* **File decryption:** decrypts a selected stored file back into the application's decrypted-files directory.
* **File-integrity comparison:** calculates a SHA-256 digest and compares it with the digest recorded for the file.
* **Credential storage:** provides a simple interface to add and retrieve stored username/password entries.
* **Graphical interface:** built with Tkinter and `tkinterdnd2` for drag-and-drop file selection.
* **Vault reset:** removes the application's vault metadata and its generated encrypted/decrypted files.



## Technologies

|Technology|Use in the project|
|-|-|
|Python|Application implementation|
|Tkinter|Graphical User Interface|
|tkinterdnd2|Drag-and-drop file selection|
|pyAesCrypt|File encryption and decryption|
|PyCryptodome|AES cipher operations for application metadata and credential values|
|`hashlib`|PBKDF2-HMAC-SHA256 key derivation and SHA-256 hashing|
|`json`, `os`, `base64`|Local metadata handling, file operations and data encoding|
|pytest|Used for unit testing as described in the academic report|

## Application structure

The application is implemented in a single Python source file, `Vault.py`, using a class-based structure.

* **MainApp:** creates the main window, manages the application frames, verifies the master password and handles shared encryption/decryption functions.
* **CreatePasswordFrame:** creates the initial master-password record.
* **LoginFrame:** provides the login interface.
* **MainMenu:** provides navigation to the application's features.
* **EncryptFrame:** selects and encrypts files.
* **ViewFrame:** lists encrypted files and provides decryption and SHA-256 comparison functions.
* **CredentialsFrame:** adds, lists and retrieves stored credentials.

## &#x09;Generated local data

When the application is run, it creates local runtime data in its working directory. These files and folders are intentionally **not** part of this source-code repository.

|Runtime item|Purpose|
|-|-|
|`.master\\\_password`|Stores the salt, PBKDF2 iteration count and derived master-password hash|
|`.encrypted\\\_info`|Stores encrypted-file metadata, including the file key and recorded SHA-256 digest|
|`.credentials`|Stores the application's encrypted credential records|
|`encrypted\\\_files/`|Holds files encrypted by the application|
|`decrypted\\\_files/`|Holds files decrypted by the application|

The application attempts to mark some of these items as hidden on Windows. The Windows hidden-file attribute is not an access-control or security boundary.

**Do not commit real vault data, passwords, encryption keys, credential records, personal files or test files containing sensitive information.** The repository's `.gitignore` contains project-specific exclusions for these runtime items.

## Requirements

* Windows (the submitted implementation uses the Windows `attrib` command to set hidden-file attributes).
* A compatible Python 3 installation.
* The external Python packages listed in [`requirements.txt`](requirements.txt).
* Tkinter, which is normally included with standard Windows Python distributions.

The source uses Python syntax introduced in Python 3.8. The original development environment's exact Python version has not yet been independently confirmed in this repository.

## Setup and run

The application can be launched in two ways, depending on the user's technical background.

### Option 1 – Windows executable (recommended for general users)

A standalone Windows executable is available in the repository's [Releases](../../releases) section.

1. Open the latest release.
2. Download `Vault.exe` from the release assets.
3. Run the downloaded executable.

This option allows users to use the application without installing Python or configuring a programming environment.

**Note:** Windows or antivirus software may display a warning because the executable is not digitally signed. Only run it if you trust the source.

### Option 2 – Run from Python source code (for developers)

The following steps describe how to create a fresh environment. A virtual environment from another computer should not be copied into this repository; recreate it locally.

Open PowerShell in the repository directory:

```powershell
# Create a new virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install the external packages
python -m pip install -r requirements.txt

# Launch the application
python .\Vault.py
```

If PowerShell prevents activation, the environment can still be used without activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\Vault.py

```

Use only synthetic, disposable test files when experimenting with the application. The interface includes an option to delete the selected original file after encryption, and the reset function deletes the application's stored vault data.

## Testing and evaluation

The original academic report describes functional, unit, black-box, security and performance testing. It reports that the principal file-encryption, decryption, credential-management and hash-comparison workflows operated during the project tests.

The report also records limitations and observed issues, including:

* Empty master passwords were not rejected during password creation.
* Some errors involving corrupted data were not handled cleanly.
* Reset could leave empty folders behind.
* The application was designed for Windows rather than cross-platform operation.
* Encryption time increased for larger files.

The report records that pytest was used for unit testing. The test suite itself is not included in this repository at this stage, so the reported results should be understood as the results recorded in the original academic report, not as a claim that automated tests have been run against this GitHub copy.

## Security considerations and known limitations

This project is a learning prototype. **Do not use it to store real passwords, confidential documents or other valuable data.**

The original implementation has limitations that would need to be addressed:

1. **Password policy:** the password-creation routine checks that the two entered values match, but does not enforce a minimum length or reject an empty password.
2. **Key derivation parameters:** the source uses PBKDF2-HMAC-SHA256 with 100,000 iterations. These parameters should be reviewed against current password-storage guidance.
3. **Authenticated encryption:** the metadata and credential encryption routines use AES-CBC with padding but do not add a separate authentication tag or MAC to those records. Confidentiality and tamper detection should be designed together.
4. **File-integrity check scope:** SHA-256 is used to compare a selected file with a previously recorded digest. This is not a general security audit of the application or a substitute for authenticated encryption.
5. **Windows-specific behaviour:** the program uses the Windows `attrib` command to hide selected files and folders.
6. **Error handling and recovery:** the academic evaluation identified weaknesses around corrupted data and user-facing error messages.
7. **Destructive operations:** the interface provides an option to delete the original file after encryption; the reset function removes the application's vault metadata and generated files.

These limitations provide a basis for future work.

## Possible future improvements

The original report identified cross-platform support, improved handling of large files, multi-factor authentication and password recovery as possible future work.

Further security-focused improvements would include:

* Enforcing a strong master-password policy.
* Reviewing PBKDF2 parameters and key-management design.
* Using an authenticated-encryption construction for protected metadata and credentials.
* Improving error handling, recovery and data-corruption handling.
* Adding repeatable automated tests to the repository.
* Separating application source, tests and documentation into a clearer project structure.

These are proposed improvements; they are **not implemented features** in the preserved original source.

## Academic authorship and reuse

This repository presents the original source code from an individual undergraduate final-year project. The accompanying academic thesis is retained separately and is not included here because it contains personal academic records and contact details.

No open-source licence is included in this repository. Do not assume that the absence of a licence grants permission to reuse, redistribute or modify the code. Any future licence choice should be made after checking the applicable university coursework and intellectual-property rules.

