# 2025 Hydromeda Camera Feed

Uses GStreamer and OpenCV's Retinex to stream images from the ROV and
perform color correction on captured frames.

The rov folder contains files that should be on the ROV controller, while
topside contains files to be run on the topside computer.

To use, copy the rov folder onto the ROV controller, install Python 3.11+,
and install the requirements.txt file. Then, run stream.py with sudo, passing
in the IP address of the topside computer as a command-line argument.

Then, copy the topside folder to the topside computer, install Python 3.11+,
and install the requirements.txt file. Run interface.py - if running on a Mac,
you may need to install an updated version of tkinter first, see [here](https://stackoverflow.com/a/60469203).
