🟩 Plugin Refresh Watcher

A lightweight Python tool designed for Minecraft plugin development.
This script automatically start your Minecraft server whenever ANY plugin JAR inside the plugins/ folder is updated.

Perfect for developers working with Paper, Purpur, Spigot, or Bukkit who want a fast and automated plugin testing workflow.

🚀 Features

* 🔄 Automatically starts server.jar when any .jar inside plugins/ changes
* 📁 some optional configuration — portable and path-independent
* 🪟 Runs the server in the same terminal (nogui)
* 🧪 Designed specifically for Minecraft plugin development
* ⚡ Fast feedback loop for testing new builds
* 🛑 Safe for development (not production)

  📁 Folder Structure

Place this script in the same folder as your Minecraft server.jar:

Install dependencies (watchdog, psutil)

pip install -r requirements.txt
* pwatchercfg.json is optional


