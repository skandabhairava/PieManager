import subprocess, os, sys

def test_package():
    packages = ["pip", "pipreqs"]

    try:
        import pip
        import pipreqs
    except Exception as e:
        print("Some packages are not installed. Please install them before continuing.")
        print("Please install these packages:\n", "\n ".join(packages))
        sys.exit(1)

    if os.name == 'nt':
        packages_not_installed = [x for x in ([["git", "--version"]]) if subprocess.run([*x]).returncode != 0]
        os.system("cls")
    else:
        packages_not_installed = [x for x in ([["git", "--version"]]) if subprocess.run([*x]).returncode != 0]
        os.system("clear")

    if packages_not_installed:
        return True
    else:
        return False
