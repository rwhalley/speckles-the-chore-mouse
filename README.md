# speckles-the-chore-mouse

<img src="/Users/richwhalley/Documents/GitHub/speckles-the-chore-mouse/img/Apodemus_sylvaticus_bosmuis.jpg" alt="Apodemus_sylvaticus_bosmuis" style="zoom:10%;" />

Automate chores for 4 or more people by interacting with Speckles The Chore Mouse via email!

## Instructions

### General Use Instructions
#### If you completed a chore
Send a message to Speckles via email with the word "Yes" in it.
#### If you want your chore reassigned to someone else
Send a message to Speckles via email with the word "pass" in it.

### Special Use: Override
If you did someone else's chore or you want to reassign someone else's chore, you can use override.
#### If you did someone else's chore
Create a new email to speckles with the word "override" in the email title
Then type "yes" and the chore type. So if the chore was "bathroom", you would type "yes bathroom" in the email text.
#### If you want to reassign someone else's chore
Create a new email to speckles with the word "override" in the email title
Then type "pass" and the chore type. So if the chore was "bathroom", you would type "pass bathroom" in the email text.

### How often does it send out emails?

Every day at a specified time using crontab on a Raspberry Pi.

### Speckles didn't respond, what do I do?

The script only runs once a day, so you may need to wait! If you still don't get a response, check your email carefully to make sure your response is typed exactly!

### How to host Speckles: Raspberry Pi Wireless Zero W Instructions

Speckles works well when loaded onto a Raspberry Pi Wireless Zero W connected to your local network.

Plug in your raspberry pi with a fresh install of raspbian.

#### Login to your Raspberry Pi From your Computer

Ssh into your raspberry pi from your computer while connected to your local wifi.

`ssh pi@raspberrypi.local`

(default password is raspberry)

#### Install Git and Clone Repo

`sudo apt-get install git`

`git clone https://github.com/rwhalley/speckles-the-chore-mouse`

#### Install Python Package Manager and Setup a Virtual Environment

`sudo apt install python3-pip`

`pip3 install virtualenv`

`export PATH="/home/pi/.local/bin:$PATH"`

`speckles-the-chore-mouse $ virtualenv specklesvenv`

`speckles-the-chore-mouse/specklesenv $ source bin/activate`

#### Install dependencies for Speckles

`pip3 install -r requirements.txt`

#### Configure Speckes

Use `vi` to fill out `email_creds.csv`, `chores.csv`, `participants.csv`

Or `magic-wormhole` the files from your computer's local terminal to your ssh terminal :)

`sudo apt-get install magic-wormhole`

`wormhole send email_creds.csv` (on computer's local terminal)

`wormhole receive` (on your ssh terminal)

#### Setup Crontab 

Crontab allows Speckles to check the mail once every day:

`crontab -e`

Append:

`@daily python /home/pi/speckles-the-chore-mouse/main.py`



