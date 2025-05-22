# 2025 Hydromeda Camera Feed

Uses GStreamer and OpenCV's Retinex to stream images from the ROV and
perform color correction on captured frames.

The rov folder contains files that should be on the ROV controller, while
topside contains files to be run on the topside computer.

To use, copy the rov folder onto the ROV controller. Install GStreamer from install Python 3.11+,
and install the requirements.txt file. Then, run stream.py with sudo, passing
in the IP address of the topside computer as a command-line argument.

Then, copy the topside folder to the topside computer.

Windows:
1. Install GStreamer from the official website.
2. Install Python 3.11+.
3. Install the requirements.txt file using `pip3 install -r requirements.txt`.
4. Run interface.py using `python3 interface.py`.

MacOS:
1. Install GStreamer through homebrew.
2. Follow the steps on this [SO answer](https://stackoverflow.com/a/60469203) to install tkinter and a modified pyenv installation.
3. Install the requirements.txt file using `pip install -r requirements.txt`.
4. Run interface.py using `python interface.py`.

Ubuntu:
1. Run install.sh.
2. Run interface.py using `python interface.py`.
