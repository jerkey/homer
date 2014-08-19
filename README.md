#homer
##Human Operated Machine Environment Runtime

it is also an *homage* to Homer Simpson who sits at a giant control panel, pushing buttons to make things happen.

this program allows you to steer a CNC machine around, switch between toolheads (including a camera), and execute g-code files.

the program tracks the coordinates of the machine, including relative positioning of different toolheads, so that for example the camera can be used to visually home the other tools before use.

macros (hotkeys mapped to sequences of hotkeys) are also available.

the program is written in python to encourage modifications during use, for maximum versatility.

##dependancies
you will need Python 2.7 or higher, and pyserial
to get the camera view to work, you also need opencv2

license:  MIT
![homey](https://raw.github.com/jerkey/homer/master/screenshot.png)
![homey](https://raw.github.com/jerkey/homer/master/spinningdesk.gif)
