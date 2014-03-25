pure sorcery
------------

this rev is a skeleton set of basic functions and a control interface 

they will need extensive revisions and expansions

dear forker,

this source is designed to work as a set of totally modular functions.  for testing, and maybe for sanity the curses-driven engine will be monolithic in its access to all relevant functions, but the subprocess functions should follow the example set by the `ptr.py` or `need.py` examples all methods related to a certain serial device should find themselves in a class object of that device's subprocess.  we can ignore want.c, but it still might come in useful for future versions.  no time now, i'll explain later.


good luck!

P.S.
curses is a fucking nightmare.
