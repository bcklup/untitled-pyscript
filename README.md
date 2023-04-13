# README

1.  Clone this repo into profile root directory `~/`

2.  On profile root directory run:`chmod +x autolaunch.sh`

3.  Open `~/.config/lxsession/LXDE-pi/autostart` using nano or vi

4.  Add the following line:
    > `@~/autolaunch.sh`

5.  Modify the script variables with the appropriate pins and threshold values.

6.  Restart Raspi or manually run the script with:
    > `@~/autolaunch.sh`
