import subprocess, os, sys

def test_package():
    packages = []

    try:
        import pip
    except Exception as e:
        packages.append("pip")

    try:
        import pipreqs
    except Exception as e:
        packages.append("pipreqs")

    try:
        import yaspin
    except Exception as e:
        packages.append("yaspin")

    try:
        import colorama
    except Exception as e:
        packages.append("colorama")

    if len(packages) > 0:
        print("Some packages are not installed. Please install them before continuing.")
        print("Please install these packages:\n", "\n ".join(packages))
        sys.exit(1)

    packages_not_installed = [x for x in ([["git", "--version"]]) if subprocess.run([*x]).returncode != 0]
    if os.name == 'nt':
        os.system("cls")
    else:
        os.system("clear")

    if packages_not_installed:
        return True
    else:
        return False
