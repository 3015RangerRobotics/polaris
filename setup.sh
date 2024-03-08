# Install pre-reqs
sudo apt update
sudo apt install -y python3-pip
sudo apt install -y --no-install-recommends python3-pil gstreamer1.0-gl gstreamer1.0-opencv gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools libgstreamer-plugins-base1.0-dev libgstreamer1.0-0 libgstreamer1.0-dev

# Build OpenCV w/ gstreamer
git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/opencv/opencv-python.git
cd opencv-python

export ENABLE_HEADLESS=1
export CMAKE_ARGS="-DWITH_GSTREAMER=ON"

sudo pip3 install --upgrade pip wheel
sudo pip3 wheel . --verbose
sudo pip3 install opencv_python*.whl

# Install other python deps
sudo pip3 install --extra-index-url https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2024/simple/ robotpy

# Cleanup
cd ..
rm -rf opencv-python/

# Create the polaris service
sudo cp polaris.service /lib/systemd/system/polaris.service
sudo cp /lib/systemd/system/polaris.service /etc/systemd/system/polaris.service
sudo chmod 644 /etc/systemd/system/polaris.service
sudo systemctl daemon-reload
sudo systemctl enable polaris.service