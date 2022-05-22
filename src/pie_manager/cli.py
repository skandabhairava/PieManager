from colorama import Fore, init
import os, shutil, sys, requests

init(convert=True)

__app_name__ = "pie-manager"

def parent_dir(path: str):
    return_ = os.path.abspath(os.path.join(path, os.pardir))
    print("Installing pie in '" + return_ + "'.")
    return return_

def main():
    pie = shutil.which("pie")
    if pie is not None:
        os.remove(pie)

    pie_manager_path = shutil.which("pie_manager")
    if pie_manager_path is None:
        print(Fore.RED + "Please reinstall Pie Manager." + Fore.RESET)
        exit()

    #pie_manager_path = ".\\cli.py"

    new_pie = os.path.join(parent_dir(pie_manager_path), "pie")

    install_info = "https://api.github.com/repos/skandabhairava/pie-rust/releases/latest"

    # if os is windows
    if os.name == "nt":
        install_name = "windows-pie.exe"
        extension = ".exe"
    # if os is linux
    elif os.name == "posix":
        install_name = "linux-pie"
        extension = ""
    # if os is mac
    elif os.name == "mac":
        install_name = "macos-pie"
        extension = ""

    #install pie from link into pie-manager directory
    print(Fore.GREEN + "Installing Pie..." + Fore.RESET)
    r = requests.get(install_info, stream=True)
    
    release = r.json()
    for asset in release["assets"]:
        if asset["name"] == install_name:
            r = requests.get(asset["url"], stream=True, headers={"Accept": "application/octet-stream"})
            break
    
    with open(new_pie+extension, "wb") as f:
        f.write(r.content)
    os.chmod(new_pie+extension, 0o755)
        
def many_in_check(*list, iterable=None):
    if iterable is None:
        return False

    for item in iterable:
        if item in list:
            return True

    return False

def entry_point():
    if many_in_check("-U", "--upgrade", "--install", "-I", iterable=(i for i in sys.argv)):
        main()
    else:
        print(Fore.RED + "Please use '--upgrade' '-U', '--install', '-I' to install/upgrade pie." + Fore.RESET)

if __name__ == "__main__":
    entry_point()