import click, sys, os, subprocess, json, shutil, random, zipfile, errno, stat
from string import ascii_letters
from colorama import init, Fore
init(convert=True)
from typing import Union
from . import fileio, click_fix

__app_name__ = "pie-manager"
__version__ = "1.0.3"
PATH = fileio.check_config()

_ENTRY_POINT = 1

@staticmethod
def _hide_cursor():
    ...

@staticmethod
def _show_cursor():
    ...

def handle_remove_readonly(func, path, exc):
    """
    Thanks to https://stackoverflow.com/questions/1213706/what-user-do-python-scripts-run-as-in-windows for the fix
    """
    if func in (os.rmdir, os.remove, os.unlink) and exc[1].errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise exc

def in_project(main_cmd:str, sub_cmd:Union[str, int], sub_cmd_list:list, sp=None, hide=False):
    if os.path.exists("project.json"):
        with open("project.json", "r") as f:
            project = json.loads(f.read())
            os.chdir(project["working_directory"])
            if sub_cmd == _ENTRY_POINT:
                sub_cmd = project["entry_point"]
            if os.name == 'nt':
                call = [f"../venv/Scripts/{main_cmd}", sub_cmd] if sub_cmd else [f"../venv/Scripts/{main_cmd}"]
                call.extend(sub_cmd_list)
                subprocess.run(call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if hide else subprocess.run(call)
            else:
                call = [f"../venv/bin/{main_cmd}", sub_cmd] if sub_cmd else [f"../venv/bin/{main_cmd}"]
                call.extend(sub_cmd_list)
                subprocess.run(call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if hide else subprocess.run(call)
    else:
        if sp:
            sp.text = f"{Fore.RED}> No project.json found in working directory.{Fore.RESET}"
            sp.color = "red"
            sp.fail("X  ")
        else:
            click.echo(Fore.RED + "> No project.json found in working directory." + Fore.RESET)

def is_in_project():
    if os.path.exists("project.json"):
        return True
    else:
        return False

@click.group(cls=click_fix.GroupWithCommandOptions)
@click.option("--version", "-V", is_flag=True, help="Prints the pie version number.")
def main(version):
    """A Loose structured and easy to use python project manager. Different sets of commands can be accessed by using the cli inside a project directory or outside of it."""
    if version:
        click.echo("Pie - A Loose structured and easy to use python project manager. Version: "+__version__)
        sys.exit(0)

def cfg():
    """Edits the config file."""
    fileio.del_config()
    fileio.check_config()

@click.argument("run", nargs=-1, required=False)
def run(run):
    """Run a project while inside it's directory."""
    in_project("python", _ENTRY_POINT, run)

@click.argument("install", nargs=-1, required=False)
def install(install):
    """Installs a package in the virtual environment."""
    in_project("pip", "install", install)

@click.argument("plist", nargs=-1, required=False)
def plist(plist):
    """Displays pip list of the virtual environment."""
    in_project("pip", "list", plist)

@click.argument("show", nargs=-1, required=False)
def show(show):
    """Displays pip package of the virtual environment."""
    in_project("pip", "show", show)

@click.argument("uninstall", nargs=-1, required=False)
def uninstall(uninstall):
    """Uninstall a package from the virtual environment."""
    in_project("pip", "uninstall", uninstall)

@click.argument("pip", nargs=-1, required=False)
def pip(pip):
    """Runs pip commands from the virtual environment."""
    in_project("pip", "", pip)

def captcha(text:str) -> str:
    """Generates a captcha."""
    captcha = ""
    for _ in range(5):
        captcha += random.choice(ascii_letters)
    return text + "-" + captcha

@click.argument("project_name", nargs=1, required=True)
def delete_project(project_name):
    """Deletes a project. The name of the command is long as to not delete the project on accident."""
    if os.path.exists(project_name + "/project.json"):
        captcha_text = captcha(project_name).upper()
        click.echo(Fore.RED + "> Please type this captcha to confirm project deletion: " + Fore.GREEN + captcha_text + Fore.RESET)
        input_captcha:str = click.prompt(Fore.GREEN + "> Enter captcha" + Fore.RESET, type=str)
        if input_captcha.upper() == captcha_text:
            shutil.rmtree(project_name, onerror=handle_remove_readonly, ignore_errors=False)
            click.echo(Fore.GREEN + "> Project successfully deleted." + Fore.RESET)
        else:
            click.echo(Fore.RED + "> Wrong captcha. Deletion of project aborted" + Fore.RESET)
    else:
        click.echo(Fore.RED + f"> Project {project_name} not found." + Fore.RESET)

@click.argument("project", nargs=1, required=True)
@click.option("--force", "-F", is_flag=True, help="Force overwrites existing project file(.pie).")
def pkg(project, force):
    """Packages a project."""

    if force:
        if os.path.exists(f"{project}.pie"):
            os.remove(f"{project}.pie")

    if os.path.exists(project + ".pie"):
        click.echo(Fore.RED + f"Project file({project}.pie) with that name already exists in this directory." + Fore.RESET)
        sys.exit(0)
    
    if os.path.exists(project + "/project.json"):

        from yaspin import yaspin, Spinner
        from yaspin.core import Yaspin
        sp = Spinner(["-", "\\", "|", "/"], 130)
        
        if os.name == "nt":
            Yaspin._show_cursor = _show_cursor
            Yaspin._hide_cursor = _hide_cursor

        with yaspin(sp, text=f"{Fore.YELLOW}> Packaging project{Fore.RESET}", color="blue", attrs=["bold"]) as sp:    
            os.chdir(project)
            reqs([], sp)
            os.chdir("..")

            try:
                with open(project + "/project.json", "r") as f:
                    project_dict = json.loads(f.read())
                    with zipfile.ZipFile(f"{project_dict['name']}.zip", "w") as zip:
                        os.chdir(project)
                        for root, dirs, files in os.walk("./"):
                            if ("venv" in root) or (".git" in root):
                                continue
                            for file in files:
                                zip.write(os.path.join(root, file))
            except Exception as e:
                sp.text = f"{Fore.RED}> Failed to package project: {e}{Fore.RESET}"
                sp.color = "red"
                sp.fail("X  ")
                sys.exit(1)

            os.chdir("..")
            os.rename(project + ".zip", project + ".pie")

            sp.text = f"{Fore.GREEN}> Project successfully packaged as {project}.pie{Fore.RESET}"
            sp.color = "green"
            sp.ok("√ ")
    else:
        click.echo(f"{Fore.RED}> Project '{project}' does not exist.{Fore.RESET}")

@click.argument("project", nargs=1, required=True, type=str)
@click.option("--force", "-F", is_flag=True, help="Force overwrits existing project.")
def unpkg(project:str, force):
    """Unpacks a project."""

    if project.endswith(".pie"):
        if os.path.exists(project):

            if force:
                if os.path.isdir(project[:-4]):
                    shutil.rmtree(project[:-4], onerror=handle_remove_readonly, ignore_errors=False)

            if os.path.isdir(project[:-4]):
                click.echo(Fore.RED + f"Project '{project[:-4]}' is already open in this directory." + Fore.RESET)
                sys.exit(0)

            from yaspin import yaspin, Spinner
            from yaspin.core import Yaspin
            sp = Spinner(["-", "\\", "|", "/"], 130)

            if os.name == "nt":
                Yaspin._show_cursor = _show_cursor
                Yaspin._hide_cursor = _hide_cursor

            with yaspin(sp, text=f"{Fore.YELLOW}> Un-Packaging project{Fore.RESET}", color="blue", attrs=["bold"]) as sp:
                try:
                    os.rename(project, project[:-4] + ".zip")

                    shutil.unpack_archive(project[:-4] + ".zip", project[:-4])
                    os.rename(project[:-4] + ".zip", project)

                    sp.write(f"{Fore.GREEN}> Project successfully un-packed as '{project[:-4]}'{Fore.RESET}")
                    sp.text = f"{Fore.GREEN}> Initialising a Virtual environment{Fore.RESET}"

                    os.chdir(project[:-4])

                    if os.name == 'nt':
                        subprocess.run(["python", "-m", "venv", "venv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.run(["python3", "-m", "venv", "venv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    sp.write(Fore.GREEN + "> Virtual Environment initialised" + Fore.RESET)
                    sp.text = f"{Fore.GREEN}> Installing requirements{Fore.RESET}"

                    in_project("pip", "install", ["-r", "../requirements.txt"], sp, hide=True)
                    sp.write(Fore.GREEN + "> Installed requirements" + Fore.RESET)

                    sp.text = f"{Fore.GREEN}> Package successfully completed unpackaging!{Fore.RESET}"
                    sp.color = "green"
                    sp.ok("√ ")
                except Exception as e:
                    sp.text = f"{Fore.RED}> Failed to un-package project: {e}{Fore.RESET}"
                    sp.color = "red"
                    sp.fail("X ")
        else:
            click.echo(f"{Fore.RED}> Project '{project}' does not exist.{Fore.RESET}")
    else:
        click.echo(f"{Fore.RED}> A pie project always endswith '.pie'.{Fore.RESET}")

@click.argument("ver", nargs=-1, required=False)
def ver(ver):
    """Displays or Changes the version of the python project."""
    if os.path.exists("project.json"):
        with open("project.json", "r") as f:
            project = json.loads(f.read())
            click.echo("> Current version: " + project["version"])
            if ver:
                project["version"] = ver[0]
                with open("project.json", "w") as f:
                    f.write(json.dumps(project, indent=4))
                click.echo("> New version: " + project["version"])
    else:
        click.echo(f"{Fore.RED}> No project.json found in working directory.{Fore.RESET}")

@click.option("--install", "-I", is_flag=True, help="Install the requirements.txt file.")
def reqs(install, sp=None):
    """Generates a requirements.txt file for the project. If --install is passed, it will install the requirements.txt file."""

    if install:
        if os.path.exists("requirements.txt"):
            in_project("pip", "install", ["-r", "../requirements.txt"], sp, hide=True)
        else:
            if sp:
                sp.write(Fore.RED + "> No requirements.txt found in working directory." + Fore.RESET)
            else:
                click.echo(Fore.RED + "> No requirements.txt found in working directory." + Fore.RESET)

        sys.exit(0)

    if os.path.exists("project.json"):
        run = subprocess.run(["pipreqs", "--force"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        if run == 0:
            if sp:
                sp.write(Fore.GREEN + "> Requirements.txt generated." + Fore.RESET)
            else:
                click.echo(Fore.GREEN + "> Requirements.txt generated." + Fore.RESET)
        else:
            if sp:
                sp.write(Fore.RED + "> Requirements.txt generation failed." + Fore.RESET)
            else:
                click.echo(Fore.RED + "> Requirements.txt generation failed." + Fore.RESET)
    else:
        if sp:
            sp.write(Fore.RED + "> No project.json found." + Fore.RESET)
        else:            
            click.echo(Fore.RED + "> No project.json found in working directory." + Fore.RESET)

def autoinstall():
    """Automatically installs all modules to the venv, used in the project."""
    reqs([])
    reqs(["--install"])

@click.argument("commit_message", nargs=1, required=True)
@click.option("--remote", "-R", is_flag=False, help="Remote to push repository to.", default="origin")
@click.option("--branch", "-B", is_flag=False, help="Branch to push repository to.", default="main")
def push(commit_message, remote, branch):
    """Pushes the repository to the specified remote and branch. Assuming git remote and branch are set."""
    if os.path.exists("project.json"):
        CONFIG:dict = fileio.get_config()
        if CONFIG["git_installed"]:
            try:

                from yaspin import yaspin, Spinner
                from yaspin.core import Yaspin
                sp = Spinner(["-", "\\", "|", "/"], 130)

                if os.name == "nt":
                    Yaspin._show_cursor = _show_cursor
                    Yaspin._hide_cursor = _hide_cursor

                with yaspin(sp, text=f"{Fore.YELLOW}> Pushing repository{Fore.RESET}", color="blue", attrs=["bold"]) as sp:
                    
                    if subprocess.run(["git", "add", "."], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                        sp.write(f"{Fore.GREEN}> Repository added to index{Fore.RESET}")

                        if subprocess.run(["git", "commit", "-m", commit_message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                            sp.write(f"{Fore.GREEN}> Repository committed{Fore.RESET}")

                            if subprocess.run(["git", "push", remote, branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                                sp.text = f"{Fore.GREEN}> Repository pushed{Fore.RESET}"
                                sp.color = "green"
                                sp.ok("√ ")

                            else:
                                sp.text = f"{Fore.RED}> Repository push failed{Fore.RESET}"
                                sp.color = "red"
                                sp.fail("X  ")

                        else:
                            sp.text = f"{Fore.RED}> Repository commit failed{Fore.RESET}"
                            sp.color = "red"
                            sp.fail("X  ")

                    else:
                        sp.text = f"{Fore.RED}> Repository add failed{Fore.RESET}"
                        sp.color = "red"
                        sp.fail("X  ")

            except Exception as e:
                click.echo(Fore.RED + f"> {e}")
        else:
            click.echo(Fore.RED + "> Git is not installed." + Fore.RESET)
    else:
        click.echo(Fore.RED + "> No project.json found in working directory." + Fore.RESET)

@click.argument('name', required=True, type=str)
@click.argument('short_description', required=True, type=str)
def new(name, short_description):
    """
    Creates a new python project.
    """

    if os.path.exists(name):
        click.echo(Fore.RED + "Project already exists." + Fore.RESET)
        sys.exit(1)

    from yaspin import yaspin, Spinner
    from yaspin.core import Yaspin
    sp = Spinner(["-", "\\", "|", "/"], 130)

    if os.name == "nt":
        Yaspin._show_cursor = _show_cursor
        Yaspin._hide_cursor = _hide_cursor

    with yaspin(sp, text=f"{Fore.YELLOW}> Creating project{Fore.RESET}", color="blue", attrs=["bold"]) as sp:
        os.mkdir(name)
        os.mkdir(name + '/src')

        sp.write(f"{Fore.GREEN}> Directories Created{Fore.RESET}")

        os.chdir(name)

        CONFIG:dict = fileio.get_config()

        with open("src/" + name + ".py", "w"):
            sp.write(f"{Fore.GREEN}> Created '{name}.py'{Fore.RESET}")
        with open("README.md", "w") as f:
            f.write(f"# {name}\n\n{short_description}")
            sp.write(f"{Fore.GREEN}> Created 'README.md'{Fore.RESET}")
        with open(".gitignore", "w") as f:
            f.write(fileio.git_ignore)
            sp.write(f"{Fore.GREEN}> Created '.gitignore'{Fore.RESET}")
        with open("project.json", "w") as f:
            config = {
                "name": name,
                "short_description": short_description,
                "version": "0.0.1",
                "author": CONFIG["dev"],
                "email": CONFIG["email"],
                "author_github": CONFIG["github"],
                "entry_point": name + ".py",
                "working_directory":"src",
                "github": "",
                "license": "MIT",
            }
            f.write(json.dumps(config, indent=4))

            sp.write(f"{Fore.GREEN}> Created 'project.json'{Fore.RESET}")
        with open("requirements.txt", "w") as f:
            sp.write(f"{Fore.GREEN}> Created 'requirements.txt'{Fore.RESET}")

        sp.write(f"{Fore.GREEN}> Required Files Created{Fore.RESET}")

        sp.text = f"{Fore.YELLOW}> Initialising local git repo{Fore.RESET}"
        if CONFIG["git_installed"]:
            subprocess.run(["git", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sp.write(f"{Fore.GREEN}> Local git repo initialised{Fore.RESET}")

        sp.text = f"{Fore.YELLOW}> Initialising a Virtual Environment{Fore.RESET}"
        if os.name == 'nt':
            subprocess.run(["python", "-m", "venv", "venv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["python3", "-m", "venv", "venv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        sp.write(f"{Fore.GREEN}> Virtual Environment initialised{Fore.RESET}")
        sp.text = f"{Fore.GREEN}> Project '{name}' successfully created{Fore.RESET}"
        sp.color = "green"
        sp.ok("√ ")

def listproj():
    """Lists all the projects in the current directory."""
    projects = []
    for folder in os.listdir():
        if os.path.isdir(folder):
            if os.path.exists(folder + "/project.json"):
                projects.append(folder)
    click.echo(Fore.GREEN + "> Projects in this directory: " + str(projects) + Fore.RESET)

@main.command()
def changelog():
    """Displays the changelog for the current version of PIE."""
    click.echo(fileio.changelog)

def register_commands():
    in_project_commands = [run, install, uninstall, plist, show, pip, ver, reqs, push, autoinstall]
    out_project_commands = [pkg, unpkg, cfg, new, listproj, delete_project]
    if is_in_project():
        for command in in_project_commands:
            if command == plist:
                cmd = click.decorators.command(name="list")(command)
            elif command == run:
                cmd = click.command(name="run", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))(command)
            else:
                cmd = click.decorators.command()(command)
            main.add_command(cmd)
    else:
        for command in out_project_commands:
            cmd = click.decorators.command()(command)
            main.add_command(cmd)

def entry_point():
    args = sys.argv
    arg = args[1:]
    if len(arg) > 0:
        if os.path.isdir(arg[0]):
            if os.path.exists(arg[0]+"/project.json"):
                with open(arg[0]+"/project.json", "r") as f:
                    project = json.loads(f.read())
                    os.chdir(arg[0] + "/" + project["working_directory"])
                    if os.name == 'nt':
                        call = [f"../venv/Scripts/python", project["entry_point"]]
                        call.extend(arg[1:])
                        subprocess.run(call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        sys.exit(0)
                    else:
                        call = [f"../venv/bin/python", project["entry_point"]]
                        call.extend(arg[1:])
                        subprocess.run(call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        sys.exit(0)
        if os.path.isfile(arg[0]):
            if arg[0].endswith(".py"):
                if os.name == 'nt':

                    call = [f"python", arg[0]]
                    call.extend(arg[1:])
                    subprocess.run(call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    sys.exit(0)
                else:

                    call = [f"python3", arg[0]]
                    call.extend(arg[1:])
                    subprocess.run(call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    sys.exit(0)

    register_commands()
    main()

if __name__ == "__main__":
    entry_point()