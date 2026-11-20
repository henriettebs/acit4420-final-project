# ACIT4420-final-project
## BusBidder Spain 
A flexible bus-booking and weighted offer-ranking platform.

### Requirements
Python version: 3.14.7<br>
Environment: (.venv)<br>
Required libraries: [customtkinter, csv, uuid, datetime, os, sys, random, unittest, re, MagicMock, patch, SimpleNameSpace]<br>
Program entry point: acit4420-final-project/src<br>
Input-file location: acit4420-final-project/src/bus_bidder/data<br>
Output-file location: acit4420-final-project/src/bus_bidder/data<br>

### Exact installation and running instructions
The application is run by using the ```python``` command
To enter a venv environment, run the following command:
```
python -m venv .venv
source .venv/bin/activate
```
Start the application:
```
cd acit4420-final-project/src
python main.py 
```

Run the tests:
```
cd acit4420-final-project/src
python -m unittest discover -s tests -t .
```
