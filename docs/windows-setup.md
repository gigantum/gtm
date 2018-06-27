# Developing on Windows

We have tested and support using conda as the package manager on Windows in
addition to the python.org version (including the one installed by `choco`).
Please install conda _For local user only (recommended)_.  This allows the
local user to manipulate the conda environment.  Then you can run conda out of
the anaconda shell.  It is recommended to add conda to your path.  In `Edit the
System Environmental Variables -> Environment Variables` edit the `PATH`
variable and add:

```
%USERPROFILE%\Anaconda3
%USERPROFILE%\Anaconda3\Scripts
```

Developing on windows has two additional depencies.  First, Windows requires
python extensions for windows.  One must install an additional package (though
this is installed automatically with the python docker module 3.*).

```
pip install pypiwin32
```

The second requirement applies only to **devloper** mode in which the code from
the host machine is linked into the labmanager docker container.  Windows does
not allow links by non-administrative users by default.  On windows, navigate
the following path from the launcher:

```
Local Security Policy ->
    Local Policies->
        User Rights Assignment->
            Create symbolic links
```

Double click on this and then select ```Add user or Group```.  In the box that
says "Enter the object names to select...." put

```
Everyone
```

Then you must restart your machine.  This policy is overly broad.  It is really
only the Docker user that needs to make links, but this is a reasonable
solution to allow Docker this ability.
