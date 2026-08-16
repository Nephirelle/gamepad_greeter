# gamepad_greeter
Gamepad_greeter is a greeter for the greetd daemon, written in Python using the pygame-ce library. Its main purpose is to provide a login screen which can be fully controlled with a gamepad to allow a couch gaming setup making as little use of mouse and keyboard as possible. 

![Screenshot 1](https://github.com/Nephirelle/gamepad_greeter/blob/main/gamepad_greeter_1.png?raw=true)

![Screenshot 2](https://github.com/Nephirelle/gamepad_greeter/blob/main/gamepad_greeter_2.png?raw=true)

## Restrictions

### Desktop Environment
This script only starts the XFCE 4 desktop environment after successful login and does not support a dynamic choice of the desktop environment, yet. Should you not use XFCE 4, change the following line in game.py - GameController.__on_password_entered(self, passwd : str) to the startup parameters for the desktop environment of your choice:

```python
    self._auth_service.start_session(["startxfce4"], [])
```

### Controllers 
This greeter was tested with a DualSense Wirless Controller (PlayStation 5) and an 8BitDo Ultimate 2 gamepad. But it might run with other controllers, too.


## Installation
1. [Install and activate greetd](https://wiki.archlinux.org/title/Greetd)
2. [Install cage-kiosk](https://github.com/cage-kiosk/cage)
3. Copy the gamepad-greeter folder to /opt/
4. Install the required Python dependencies listed in requirements.txt or create a corresponding venv

### Testing
You can test the greeter with some test users and without calling the greetd daemon by setting the --test parameter:
    
    python3 /opt/gamepad_greeter/main.py --test

### Configure Greetd
 Edit the `/etc/greetd/config.toml` file:

```toml
[terminal]
# The VT to run the greeter on. Can be "next", "current" or a number
# designating the VT.
vt = 1

# The default session, also known as the greeter.
[default_session]

# `agreety` is the bundled agetty/login-lookalike. You can replace `/bin/sh`
# with whatever you want started, such as `sway`.
# command = "agreety --cmd /bin/sh"
command = "cage -s -- /your/python/path/python3 /opt/gamepad_greeter/main.py"

# The user to run the command as. The privileges this user must have depends
# on the greeter. A graphical greeter may for example require the user to be
# in the `video` group.
user = "greeter"
```

Make sure the line
    
```toml
command = "cage -s -- /your/py/path/python3 /opt/gamepad_greeter/main.py"
```

gives the correct path for the python installation of your environment or venv.

### Tip
If something goes wrong and you do not see the greeter when starting your computer, you can still log in by calling the terminal with Ctrl + Alt + F3. Just enter your credentials and call your desktop environment manually.