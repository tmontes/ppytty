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
* Scripts are build out of slides.


Thanks
------

.. marker-start-thanks-dont-remove

- Brandon Rhodes for...

- David Beazely for ...

.. marker-end-thanks-dont-remove



About
-----

.. marker-start-about-dont-remove

``ppytty`` was created by Tiago Montes.

.. marker-end-about-dont-remove

