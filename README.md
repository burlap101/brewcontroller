# brewcontroller
My respository for my brewery controller. Works on Rasperry Pi 2 models. Helps with controlling temps for mashing and fermentation. Also has a feature for monitoring hop additions during boil. 
Uses tkinter for the GUI side of the project, multithreading for running the "BrewBrains" concurrently with the GUI within the one instance. 
Logging is included by with logging performed using a format similar to a .csv, which is used for producing trends of how the temperatures have been going and how often fridge/freezer/heat belt is operating using matplotlib and pandas. 
Originally developed using Python2 but has nowe been converted and successfully tested on new brews made. 

