# PathPyinder
PathPyinder is a pathfinding algorithm visualizer written in Python. Currently supported algorithms are Breadth-First Search, Depth-First Search, Dijkstra's Algorithm, and the A* (A Star) Algorithm.

---

## Requirements
1. **Python** - Version 3.6 or higher
2. **[PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/)** - GUI wrapper library for tkinter. 
Install via: `pip install PySimpleGUI` or `pip3 install pysimplegui`

---

## Usage
Navigate to the root directory via terminal and launch PathPyinder with: `python pathpyinder.py`. The following GUI should open:

![PathPyinder GUI](https://raw.githubusercontent.com/borisboguslavsky/Pathy/tree/master/assets/pathpyinder_gui.png "PathPyinder GUI")

### **Drawing Mazes:**
There are four types of maze nodes that can be drawn: **Wall**, **Path**, **Start**, **End**. Select which node to draw by clicking the buttons in the *Draw* frame of the GUI, and clicking or dragging somewhere in the maze.

### **Selecting an Algorithm:**
Use the radio buttons in the 'Algorithm' frame to select which algorithm will be used to solve the maze. Keep in mind that Dijkstra's algorithm will look the same as the Breadth-First Search algorithm because all nodes are equally accessible from their neighbor nodes. Dijkstra's algorithm would be more visually discernable from breadth-first search if some nodes were harder to cross than others, and the access priority for those nodes could be set accordingly.

### **Solving Mazes:**
Click the **Solve** button in the *Controls* frame of the GUI to start solving the maze. Keep in mind, a start node and end node have to exist for PathPyinder to attempt solving. You can adjust the speed that the algorithm iterates by using the speed slider. You can also pause the algorithm entirely iterate through it one step at a time using the **Pause** and **Play** buttons under the **Solve** button.

### **Resetting and Clearing Mazes:**
Click the **Reset** button at any time to stop solving, and reset the current maze to it's original, unsolved state.

Click the **Clear** button to stop solving, and erase the entire maze to an empty grid.

### **Saving and Loading Mazes:**
Save and load mazes via **File > Save Maze** and **File > Open Maze** in the menu bar. Mazes are saved as .txt files. There is a mazes directory that includes some pre-built mazes.

---

## Default Settings
You can change some options that PathPyinder initializes with by editing `settings.txt`. This file has three lines in it, which correspond to:
* **Line 1:** The maze to load on startup. Values are formatted as:
  * `mazes/maze_filename.txt`
* **Line 2:** The algorithm that will be selected by default: Valid values are:
  * `bfs`
  * `dfs`
  * `dijkstra`
  * `astar`
* **Line 3:** The default speed at which the algorithm will run. Valid values are:
  * 1
  * 2
  * 3
  * 4
  * 5