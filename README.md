A small script to generate a screen in Zabbix.
It is far from perfect. But it is a lot faster then manually adding several graphs to a screen.

Usage:
- Fill in the [common]  section in the config file
- In the screen section, you can enter a name for the screen. If the name allready exists, you will be prompter to give a new name

When you start this script, it will first try to connect to the Zabbix API. If successfull, it will display the available hostgroups. Select a hostgroup for which you want to build a screen.
The script will then fetch all hosts and associated graphs and display them in a menu (build with curses).

You can navigate the graphs per host and select them just by pressing the spacebar. If you want specific graphs on the left or right side of the screen, you can press 'l' or 'r' to place them there. Be sure to have an equal amount of 'l' and 'r' graphs. The script hasn't got logic (yet) to place it properly. I've build the 'l' and 'r' logic for a specific screen which I wanted (2 switches, 1 completely on the left, the other 1 on the right).

Feel free to improve this script (which it needs :) )


Possible future features:
- Better logic for left and right placed graphs
- Order of graphs
- colspan/rowspan support
