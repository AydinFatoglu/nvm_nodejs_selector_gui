import os
import sys
import shutil
import ctypes
import winreg
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time


class LoadingWindow:
    """Loading bar penceresi"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NVM Installer")
        self.root.resizable(False, False)
        self.root.overrideredirect(False)
        
        # Pencere boyutu
        window_width = 400
        window_height = 150
        
        # Ekran ortasına konumlandır
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ana frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        self.title_label = ttk.Label(
            main_frame, 
            text="⏳ NVM for Windows Installing...", 
            font=("Segoe UI", 12, "bold")
        )
        self.title_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, 
            length=350, 
            mode='determinate'
        )
        self.progress.pack(pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Hazırlanıyor...")
        self.status_label = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            font=("Segoe UI", 9)
        )
        self.status_label.pack()
        
        self.root.update()
    
    def update_progress(self, value, status_text):
        """Progress bar güncelle"""
        self.progress['value'] = value
        self.status_var.set(status_text)
        self.root.update()
        time.sleep(0.3)  # Yavaş doldurma efekti
    
    def close(self):
        """Pencereyi kapat"""
        self.root.destroy()


def show_centered_messagebox(title, message, msg_type="info"):
    """Ekran ortasında mesaj kutusu göster"""
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi gizle
    
    # Ekran ortasına konumlandır
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"+{screen_width//2}+{screen_height//2}")
    
    # Mesaj kutusunu göster
    if msg_type == "info":
        messagebox.showinfo(title, message, parent=root)
    elif msg_type == "error":
        messagebox.showerror(title, message, parent=root)
    elif msg_type == "warning":
        messagebox.showwarning(title, message, parent=root)
    
    root.destroy()


def is_admin():
    """Admin yetkisi kontrolü"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def set_environment_variable(name, value, user=False):
    """Ortam değişkeni ayarla (System veya User)"""
    try:
        if user:
            # User environment variables
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
        else:
            # System environment variables (admin gerekli)
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
        
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        print(f"[+] Ortam değişkeni ayarlandı: {name} = {value}")
        return True
    except Exception as e:
        print(f"[-] Hata ({name}): {e}")
        return False


def get_environment_variable(name, user=False):
    """Ortam değişkenini oku"""
    try:
        if user:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ
            )
        else:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_READ
            )
        
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except:
        return ""


def update_path_variable(new_paths, user=False):
    """PATH değişkenine yeni yollar ekle"""
    current_path = get_environment_variable("Path", user)
    
    # Zaten eklenmişse ekleme
    paths_to_add = []
    for p in new_paths:
        if p.lower() not in current_path.lower():
            paths_to_add.append(p)
    
    if paths_to_add:
        new_path = current_path.rstrip(';') + ';' + ';'.join(paths_to_add)
        return set_environment_variable("Path", new_path, user)
    else:
        print("[*] PATH zaten güncel")
        return True


def create_settings_file(nvm_home, nvm_symlink, arch=64):
    """settings.txt dosyası oluştur"""
    settings_path = os.path.join(nvm_home, "settings.txt")
    
    content = f"""root: {nvm_home}
path: {nvm_symlink}
proxy: none
arch: {arch}
"""
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[+] settings.txt oluşturuldu: {settings_path}")


def broadcast_environment_change():
    """Ortam değişkeni değişikliğini sisteme bildir"""
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        
        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result)
        )
        print("[+] Ortam değişkenleri güncellendi (broadcast)")
    except Exception as e:
        print(f"[!] Broadcast hatası: {e}")


def main():
    print("=" * 60)
    print("  NVM for Windows - Otomatik Manual Kurulum")
    print("=" * 60)
    
    # Admin kontrolü
    if not is_admin():
        print("\n[!] Bu script admin yetkisi gerektirir!")
        print("[*] Admin olarak yeniden başlatılıyor...")
        
        # Admin olarak yeniden başlat
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    
    # Loading penceresi oluştur
    loading = LoadingWindow()
    loading.update_progress(5, "Başlatılıyor...")
    
    # Dinamik kullanıcı yolları
    username = os.getenv("USERNAME")
    user_profile = os.getenv("USERPROFILE")  # C:\Users\<kullanıcı>
    appdata_roaming = os.getenv("APPDATA")   # C:\Users\<kullanıcı>\AppData\Roaming
    
    print(f"\n[*] Kullanıcı: {username}")
    print(f"[*] User Profile: {user_profile}")
    
    loading.update_progress(10, f"Kullanıcı: {username}")
    
    # NVM dizinleri
    nvm_home = os.path.join(appdata_roaming, "nvm")
    nvm_symlink = os.path.join(appdata_roaming, "nvm", "nodejs")
    
    print(f"\n[*] NVM_HOME: {nvm_home}")
    print(f"[*] NVM_SYMLINK: {nvm_symlink}")
    
    loading.update_progress(15, "Dizinler belirleniyor...")
    
    # Script/EXE'nin bulunduğu klasör
    # PyInstaller ile exe yapıldığında sys.executable exe'nin yolunu verir
    if getattr(sys, 'frozen', False):
        # EXE olarak çalışıyor
        script_dir = os.path.dirname(sys.executable)
    else:
        # Python script olarak çalışıyor
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    loading.update_progress(20, "Dosyalar kontrol ediliyor...")
    
    # Gerekli dosyaları kontrol et (minimum gereksinim)
    required_files = ["nvm.exe"]
    missing_files = []
    
    for f in required_files:
        if not os.path.exists(os.path.join(script_dir, f)):
            missing_files.append(f)
    
    if missing_files:
        loading.close()
        error_msg = f"nvm.exe script ile aynı klasörde bulunamadı!\n\nLütfen nvm-noinstall.zip içeriğini şu klasöre çıkarın:\n{script_dir}"
        print(f"\n[!] HATA: {error_msg}")
        show_centered_messagebox("NVM Kurulum Hatası", error_msg, "error")
        sys.exit(1)
    
    loading.update_progress(25, "NVM klasörü oluşturuluyor...")
    
    # NVM klasörünü oluştur
    os.makedirs(nvm_home, exist_ok=True)
    print(f"[+] Klasör oluşturuldu: {nvm_home}")
    
    loading.update_progress(30, "Dosyalar kopyalanıyor...")
    
    # Tüm dosyaları NVM klasörüne kopyala (script/exe hariç)
    print("\n[*] Dosyalar kopyalanıyor...")
    copied_files = []
    
    items_to_copy = [item for item in os.listdir(script_dir)]
    total_items = len(items_to_copy)
    
    for idx, item in enumerate(items_to_copy):
        src = os.path.join(script_dir, item)
        dst = os.path.join(nvm_home, item)
        
        # Kendimizi (exe/py) kopyalama
        if item.lower().endswith(('.py', '.exe')) and 'nvm' not in item.lower():
            continue
        if item.lower() == os.path.basename(sys.executable).lower():
            continue
            
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            copied_files.append(item)
            print(f"[+] Kopyalandı: {item}")
        elif os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            copied_files.append(item + "/")
            print(f"[+] Klasör kopyalandı: {item}/")
        
        # Progress güncelle (30-50 arası)
        progress = 30 + int((idx + 1) / total_items * 20)
        loading.update_progress(progress, f"Kopyalanıyor: {item}")
    
    loading.update_progress(55, "settings.txt oluşturuluyor...")
    
    # settings.txt oluştur
    create_settings_file(nvm_home, nvm_symlink)
    
    loading.update_progress(60, "Ortam değişkenleri ayarlanıyor...")
    
    # Ortam değişkenlerini ayarla (System level)
    print("\n[*] Ortam değişkenleri ayarlanıyor...")
    
    set_environment_variable("NVM_HOME", nvm_home, user=False)
    loading.update_progress(65, "NVM_HOME ayarlandı...")
    
    set_environment_variable("NVM_SYMLINK", nvm_symlink, user=False)
    loading.update_progress(70, "NVM_SYMLINK ayarlandı...")
    
    # System PATH'e sadece NVM_HOME ekle (nvm.exe için)
    update_path_variable(["%NVM_HOME%"], user=False)
    loading.update_progress(75, "System PATH güncellendi...")
    
    # User level için de ayarla
    set_environment_variable("NVM_HOME", nvm_home, user=True)
    set_environment_variable("NVM_SYMLINK", nvm_symlink, user=True)
    
    # User PATH'e NVM_HOME ekle
    update_path_variable([nvm_home], user=True)
    loading.update_progress(80, "User PATH güncellendi...")
    
    # Eğer kurulu Node versiyonu varsa, ilkini PATH'e ekle
    first_node_version = None
    for item in os.listdir(nvm_home):
        item_path = os.path.join(nvm_home, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "node.exe")):
            first_node_version = item
            break
    
    if first_node_version:
        node_path = os.path.join(nvm_home, first_node_version)
        # User PATH'in başına Node yolunu ekle
        current_user_path = get_environment_variable("Path", user=True)
        new_user_path = node_path + ";" + current_user_path
        set_environment_variable("Path", new_user_path, user=True)
        loading.update_progress(85, f"Node {first_node_version} PATH'e eklendi...")
        print(f"[+] İlk Node versiyonu PATH'e eklendi: {first_node_version}")
    else:
        loading.update_progress(85, "Kurulu Node versiyonu yok...")
    
    # Değişiklikleri broadcast et
    broadcast_environment_change()
    loading.update_progress(95, "Değişiklikler uygulanıyor...")
    
    loading.update_progress(100, "✅ Kurulum tamamlandı!")
    time.sleep(0.5)
    
    # Loading penceresini kapat
    loading.close()
    
    # Kurulum özeti (sadeleştirilmiş)
    node_info = f"Node {first_node_version} aktif" if first_node_version else "Node kurulu değil"
    
    summary_message = f"""✅ KURULUM TAMAMLANDI!

📁 NVM_HOME:
{nvm_home}

🔧 PATH'e eklendi:
• {nvm_home}
{f"• {os.path.join(nvm_home, first_node_version)}" if first_node_version else ""}

🟢 {node_info}

📋 Sonraki Adımlar:
1. Yeni CMD veya PowerShell aç
2. nvm install lts (Node indirmek için)
3. Node Selector GUI ile versiyon değiştir"""

    print("\n" + "=" * 60)
    print("  KURULUM TAMAMLANDI!")
    print("=" * 60)
    print(summary_message)
    
    # Mesaj kutusu göster
    show_centered_messagebox("NVM Kurulum Tamamlandı", summary_message, "info")
    
if __name__ == "__main__":
    main()
