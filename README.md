# Client-Server Model FTP

Originally made for Durham University's Department of Computer Science's course _Networks and Systems_ under the sub-module _Networks_, as part of the coursework in 2017/2018.

This repository contains an implementation of the [client and server side](https://en.wikipedia.org/wiki/Client%E2%80%93server_model) of a [File Transfer Protocol (FTP)](https://en.wikipedia.org/wiki/File_Transfer_Protocol) application written in Python

This assignment is a precursor to [this other assignment](https://github.com/thesofakillers/Distributed-File-Server) from the same module.

## Repository structure

```bash
.
├── client
│   └── client.py
├── README.md
└── server
    ├── resources
    │   ├── LargeFile.mp4
    │   ├── MediumFile.pdf
    │   └── SmallFile.txt
    └── server.py
```

Client files stored in [./client](client/). Server files stored in [./server/resources](server/resources/).

## Requirements

The [Python 3.6](https://www.python.org/downloads/release/python-360/) scripts can be run on Windows or Linux, ensure that Python 3.4+ is installed and defaulted. The modules necessary for the scripts to run are part of the standard Python library so should already be installed.

## Instructions

Open two terminal windows and change the current directory to [./client](client/) [./server](server/) respectively. Then in the client window  type `python client.py` and in the other type `python server.py`. This will start the client and server respectively.

Throughout, `server.py` provides some diagnostics about what is going on, while `client.py` also provides instructions.

In general, the workflow is:
1. Start `server.py`
2. Start `client.py`
3. Type `CONN` into `client.py` to connect to the server
4. Type one of `UPLD`, `LIST`, `DWLD`, `DELF` or `QUIT` into client.py. Descriptions/Instructions for these are presented when running `client.py`.
5. Repeat as much as you want until you disconnect from the server by typing `QUIT` into `client.py`.
6. Type `QUIT` again to close the `client.py` script. You may repeat steps 2-5.
7. `server.py` continues listening for connections. You can end server.py by typing ctrl+c in linux/MACOS and ctrl+break in Windows.
