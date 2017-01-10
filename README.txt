This program is designed to dynamically generate text boxes for a string of any length. 
In the top-level game loop, I define the character objects and text for each desired
succession of character text, and I call a function to convert the string into however
many boxes are needed. That method then calls a display method. 
The person talking is indicated by the portrait and name, stored in the character I pass
into the text-to-boxes function.
The location of the character name in the text box, the portrait, and the name are all dependent
on the character.
Also note that the little cursor appears as long as there is more text to be read. For the last 
individual person's line, you need to pass in true for the optional parameter called lastBox. This
will tell the display function to mark the last box of the last character dialogue bit as not needing
to blit the cursor to the screen. 