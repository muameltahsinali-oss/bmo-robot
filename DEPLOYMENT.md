# Deploying BMO to Raspberry Pi

This guide covers several methods to move your project files from your computer to the Raspberry Pi.

## Method 1: SCP (Command Line) - Recommended for Speed

If you are comfortable with the terminal, `scp` (Secure Copy) is the fastest way.

**Prerequisites:**
- Raspberry Pi IP address (e.g., `192.168.1.100`)
- SSH enabled on the Pi

**Command (Run from your PC's terminal):**
```powershell
# Syntax: scp -r <local_path> <user>@<pi_ip>:<remote_path>
scp -r "c:\Users\Muamel\BMO advanture\BMO_Project" pi@192.168.1.100:/home/pi/
```
*Replace `192.168.1.100` with your Pi's actual IP address.*

## Method 2: SFTP (Visual Interface) - Recommended for Ease of Use

Tools like **FileZilla** or **WinSCP** provide a drag-and-drop interface.

1.  **Download & Install** FileZilla or WinSCP.
2.  **Connect**:
    -   **Host**: Your Pi's IP address (e.g., `192.168.1.100`)
    -   **Username**: `pi` (or your custom user)
    -   **Password**: Your Pi's password
    -   **Port**: `22`
3.  **Transfer**: Drag the `BMO_Project` folder from the left (your PC) to the right (Raspberry Pi file system, usually `/home/pi`).

## Method 3: USB Drive - Good for Offline

1.  Copy the `BMO_Project` folder to a USB drive.
2.  Plug the USB drive into the Raspberry Pi.
3.  On the Pi, open a terminal or file manager.
4.  Copy the files:
    ```bash
    # Assuming USB mounts to /media/pi/USB_NAME
    cp -r /media/pi/USB_NAME/BMO_Project /home/pi/
    ```

## Method 4: Git - Best for Version Control

If your project is hosted on GitHub/GitLab:

1.  **On the Pi**, run:
    ```bash
    git clone https://github.com/your-username/BMO_Project.git /home/pi/BMO_Project
    ```
2.  To update later:
    ```bash
    cd /home/pi/BMO_Project
    git pull
    ```

---

## Next Steps

Once files are on the Pi, proceed with the **Installation** steps in [README.md](./README.md).
