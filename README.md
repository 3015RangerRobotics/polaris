# polaris
 Custom implementation of 6328's Northstar

## Default orange pi login 
DO NOT CHANGE
* Username: `orangepi`
* Password: `orangepi`

## Setup
1. Clone this repo in the home directory
2. Add a calibration.json file
3. Make required changes to config.json
4. Change the hostname in `/etc/hostname` to match the device id in config.json
5. `chmod +x setup.sh`
6. `./setup.sh`
7. `sudo reboot now`

After making changes to config or calibration, run `sudo systemctl restart polaris`

## To update
1. `sudo systemctl stop polaris`
2. `git pull`
3. `sudo systemctl start polaris`