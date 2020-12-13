# speckles-the-chore-mouse

<img src="./img/speckles.png" alt="Apodemus_sylvaticus_bosmuis" style="zoom:40%;" />

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

### Frequently Asked Questions:

#### How often does it send out emails?

Speckles checks mail multiple times a day using crontab on a Raspberry Pi.

#### Speckles didn't respond, what do I do?

You may need to wait! If you still don't get a response, check your email carefully to make sure your response is typed exactly!

### How to host Speckles in your home: Raspberry Pi Wireless Zero W Instructions

Speckles works well when loaded onto a Raspberry Pi Wireless Zero W connected to your local network.

Plug in your raspberry pi with a fresh install of raspbian.

#### Login to your Raspberry Pi From your Computer

Ssh into your raspberry pi from your computer while connected to your local wifi.

`ssh pi@raspberrypi.local`

(default password is "raspberry" - make sure to change it to a strong password since we will be storing email credentials on the machine using the `passwd` command)

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

Or if you don't like using `vi`, `magic-wormhole` the files from your computer's local terminal to your ssh terminal :)

`sudo apt-get install magic-wormhole`

`wormhole send email_creds.csv` (on computer's local terminal)

`wormhole receive` (on your ssh terminal)

#### Setup Crontab 

Crontab allows Speckles to check the mail periodically every day:

`crontab -e`

The following will run the script once every 10 minutes:

`*/10 * * * * /usr/bin/python ~Code/speckles-the-chore-mouse/main.py`

The following will run the script once daily:

`@daily python /home/pi/speckles-the-chore-mouse/main.py`

Congrats! You are now running speckles on a raspberry pi!

