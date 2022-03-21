# Pie Project Manager Changelog
<hr>

> v1.0.3

```diff
! Fixed a critical bug with 'run' and extra cli arguments <cli.py>
```

<hr>

> v1.0.2

```diff
+ Added a yaspin spinner <cli.py>
+ Added yaspin related statements to yaspin specific functions. Increases code length, might reduce code runtime while using other commands
```

<hr>

> v1.0.1

```diff
+ Updated code for package check to make it more accurate <sysreqs.py>
+ Added yaspin and colorama to package check <sysreqs.py>
+ Fixed issue where deleting project files which contains readonly files inside will crash the program(Windows) <cli.py>
```

<hr>

> v1.0.0

```diff
+ Official release on pypi
- Will no longer be hosted on "https://test.pypi.org/project/pie-manager/"
```

<hr>

> v0.1.12

```diff
+ Added project deletion command
```

> v0.1.12.2

```diff
! Fixed captcha issue
! Added Project check while deletion
```

<hr>

> v0.1.11

```diff
+ Added CHANGELOG history file
+ Added yaspin for loading bar display
+ Refactored most of the code for yaspin and better readability
- Removed output from shell/terminal run commands(ex: git, pip, etc.)
! Fixed a few wordings in pie --help
# Fixed minor gramatical issues
```

<hr>