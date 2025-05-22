#!/bin/bash

# Install script for RTP Camera System

# Update system and install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    python3-pip \
    python3-tk \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    libgirepository1.0-dev \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev

# Install Python packages
pip3 install \
    opencv-python \
    opencv-python-headless \
    numpy \
    Pillow \
    PyGObject

# Verify GStreamer Python bindings
python3 -c "
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)
print('GStreamer version:', Gst.version_string())
"

