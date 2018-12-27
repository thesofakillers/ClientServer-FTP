Directory structure
-dzgf42
	-client
		-client.py
		-client files
	-server
		-server.py
		-resources
			-server files
	-README.txt

Client files stored in "dzgf42/client". Server files stored in "server/resources"

The Python3.6 scripts can be run on Windows or Linux, ensure that Python3.4+ is installed and defaulted. The following modules are also necessary for the scripts to run:
-socket
-struct
-timeit
-os
-pickle

Open two terminal windows and change the current directory to dzgf42. Then in one window type "python client.py" and in the other type "python server.py". This will start the client and server respectively.

Throughout, server.py provides some diagnostics about what is going on, while client.py also provides instructions.

In general, the workflow is:
1. Start server.py
2. Start client.py
3. Type "CONN" into client.py to connect to the server
4. Type one of "UPLD", "LIST", "DWLD", "DELF" and "QUIT" into client.py. Descriptions/Instructions for these are presented when running client.py.
5. Repeat as much as you want until you disconnect from the server by typing "QUIT" into client.py.
6. Type "QUIT" again to close the client.py script. You may repeat steps 2-5.
7. server.py continues listening for connections. You can end server.py by typing ctrl+c in linux/MACOS and ctrl+break in Windows.