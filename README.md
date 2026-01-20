# NVM for Windows - No Admin Edition

A simple tool to manage Node.js versions on Windows. Works in corporate environments without requiring admin privileges.

---

## What Is This?

When working with Node.js, different projects may require different versions. Normally NVM for Windows handles this using symlinks, but it asks for admin password every time you switch versions. This is especially frustrating on company computers.

This tool does the same job with a different approach. Instead of symlinks, it works through the PATH variable. This means you don't need admin privileges to switch versions. Just select the version you want from the GUI, open a new terminal, and start working.

---

## How To Use

For the initial setup, run `nvm_installer.exe`. This is only needed once and sets up the environment variables. After that, use commands like `nvm install 20` in the terminal to download the Node versions you need.

When you want to switch versions, open `nvm_gui.exe`. Your installed versions will appear in the list. Click the one you want and press the "Set / Use" button. The selected version will be active when you open a new terminal window.

---

## Important Note

Don't use the `nvm use` command in the terminal because it still requires admin privileges. Always use the GUI tool instead. The `nvm install` and `nvm list` commands work normally, just prefer the GUI over `nvm use`.
