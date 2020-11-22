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
