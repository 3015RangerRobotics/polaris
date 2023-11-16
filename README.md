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
4. `chmod +x setup.sh`
5. `./setup.sh`
6. Either reboot or run `sudo systemctl start polaris` to start

After making changes to config or calibration, run `sudo systemctl restart polaris`