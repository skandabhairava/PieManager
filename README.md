
# PIE Project Manager


<p align="center">
  <img width="250" height="250" src="https://cdn.discordapp.com/attachments/731940266570809485/953666263161372782/piepy.png">
</p>

## Pie is a loose structured python project manager.

A Loose structured and easy to use python project manager. Different sets of
commands can be accessed by using the cli inside a project directory or
outside of it.
<hr>
<br>

## Installation

Install PIE Project Manager on pip

```bash
  pip install pie-manager
  pip3 install pie-manager 
```
    
<hr>
<br>

## Changelogs

[Changelogs](CHANGELOG.md)


<hr>
<br>

## CLI Commands

> General

| CLI Command| Description|
| -- | -- |
| -V, --version | Prints the pie version number. |
| --help | Shows the help message for a certain command. |
| changelog | Displays the changelog for the current version of PIE. |

<hr>
<br>

> Outside a project

| CLI Command| Description|
| -- | -- |
| cfg | Edits the config file. |
| delete-project | Deletes a project. |
| listproj | Lists all the projects in the current directory. |
| new | Creates a new python project. |
| pkg | Packages a project. |
| unpkg | Unpacks a project. |

<hr>
<br>

> Inside a project (Directory should contain a "project.json")

| CLI Command| Description|
| -- | -- |
| autoinstall | Automatically installs all modules to the venv, used in the project. |
| install | Installs a package in the virtual environment. |
| list | Displays pip list of the virtual environment. |
| pip | Runs pip commands from the virtual environment. |
| push | Pushes the repository to the specified remote and branch (Assuming Git repo is initialised). |
| reqs | Generates a requirements.txt file for the project. |
| run | Run a project while inside it's directory. |
| show | Displays pip package of the virtual environment. |
| uninstall | Uninstall a package from the virtual environment. |
| ver | Displays or Changes the version of the python project. |