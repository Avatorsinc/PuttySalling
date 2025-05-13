# Viking SSH Manager

A Windows GUI application that embeds PuTTY inside a Tkinter window for quick SSH access to store servers (e.g. `pv1234`).

---

## Features

* **Embedded PuTTY**: Launch and reparent PuTTY directly inside the application window (full‑screen within the frame).
* **Store Management**: Enter a 4‑digit store number, connect, save frequent stores, and reconnect with a click.
* **Language Toggle**: UI supports English and Danish—switch on the fly.
* **Custom Branding**: Add a semi‑transparent PNG header/branding image over a light‑blue background.
* **Persistent Settings**: Stores last session, saved store list, PuTTY path, and session name in `config.json`.
* **Info Panel**: Quick FYI popup for workplace management notices or tips.

## Prerequisites

* **Windows 10/11**
* **Python 3.7+**
* **PuTTY** (with a saved session, e.g. `StoreTemplate`, configured for:

  * Terminal → Keyboard: Backspace = Control‑H, Function keys & keypad = Xterm R6
  * Terminal → Features: Disable application keypad mode
  * Window → Appearance: your desired font & size
  * Window → Translation: Remote character set = CP850
  * Connection → SSH → Kex: Warn for Diffie‑Hellman group exchange
* **Required Python packages**:

  ```bash
  pip install pywin32  # for window embedding
  pip install pillow   # (optional) for PNG alpha blending
  ```

## Installation

1. **Clone this repo**:

   ```bash
   git clone https://github.com/Avatorsinc/PuttySalling.git
   cd viking-ssh-manager
   ```

2. **Install dependencies**:

   ```bash
   python -m pip install --upgrade pip
   pip install pywin32 pillow
   ```

3. **Copy files**:

   * Place `putty.exe` and `background.png` (and optional `flag_en.png` / `flag_da.png`) into the project directory.
   * Ensure `PuttySalling.py` (or your renamed script) is in the same folder.

4. **Configure PuTTY**:

   * Open PuTTY GUI, create a session named **StoreTemplate** with the settings listed above, save it.

## Configuration

* **config.json** (auto‑generated) stores:

  ```json
  {
    "putty_path": "putty.exe",
    "session_name": "StoreTemplate",
    "last_store": "1234",
    "saved_stores": ["1234","5678"],
    "info_text": "Your custom FYI here."
  }
  ```
* You can edit these values manually or via the Settings menu in the app.

## Usage

1. **Run** the script:

   ```bash
   python PuttySalling.py
   ```
2. **Enter** a 4‑digit store number and click **Connect**.
3. **Save** a frequently used store to the list and double‑click it to reconnect.
4. **Switch** language between English/Danish via the buttons.
5. **View** any custom info via the **Info** button.

If `background.png` has transparency, it will be alpha‑composited over the light‑blue UI.
Areas not covered by the image remain in the default color.

## Project Structure

```
├── PuttySalling.py      # Main application script
├── background.png       # Optional semi‑transparent header image
├── flag_en.png          # Optional "English" flag icon
├── flag_da.png          # Optional "Dansk" flag icon
├── putty.exe            # PuTTY binary
├── config.json          # Auto‑generated settings file
└── README.md            # This documentation
```

## Contributing

1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/foo`).
3. Commit your changes (`git commit -am 'Add foo feature'`).
4. Push to the branch (`git push origin feature/foo`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
