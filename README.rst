``ppytty``: Present Python on a TTY
===================================

|


``ppytty`` will hopefully be a tool to present Python concepts and code on terminals.

Inspired and motivated by the likes of Brandon Rhodes and David Beazely I set myself to create something to better support many presentations I do, often in training scenarios.

Wishlist
--------

* Support "slides"-like *and* "REPL"-like interfaces.
* Slides will be built out of "things" like:

  * Text blocks.
  * Code blocks (like text blocks, but with auto line numbers + syntax).
  * List blocks (like text blocks, but with bullet per "item").
  * Terminals (via pseudo tty and subproceses with terminal emulation).

* General text blocks will have:

  * Width and height (not-necessarily fixed but constraint based)
  * Background, foreground and other default text attributes like bold/reverse.
  * Support double width/heigth characters.

* Things can be animated:

  * Faded in/out.
  * Moved.

* Things, like terminals, gain/loose keyboard focus.
* Handle terminal resizing nicely.

A few odd ideas
^^^^^^^^^^^^^^^
* Optional render to PDF?
* Support speaker notes (maybe via a named PIPE? or just a file?)
* Allow running a Python REPL after sourcing the contents of a "code thing"
  (maybe the REPL could be passed in the same "external python script" that the code thing takes itself)



Thanks
------

.. marker-start-thanks-dont-remove

- Brandon Rhodes for the Keynote at North Bay Python 2017 (https://www.youtube.com/watch?v=rrMnmLyYjU8) and the "The Dictionary Even Mightier" talk at PyCon 2017 (https://www.youtube.com/watch?time_continue=4&v=66P5FMkWoVU).

- David Beazely for the "Built in Super Heroes" Keynote at PyData Chicago 2016 (https://www.youtube.com/watch?time_continue=1&v=lyDLAutA88s).

.. marker-end-thanks-dont-remove



About
-----

.. marker-start-about-dont-remove

``ppytty`` was created by Tiago Montes.

.. marker-end-about-dont-remove

