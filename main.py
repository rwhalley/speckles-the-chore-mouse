import smtplib, ssl
import os
import easyimap
import time
import random
import string
import csv
from email.message import EmailMessage
from datetime import date, datetime
import pandas
import pickle

from participant import Participant
from chore import Chore

TEST = False

class ChoreService:
    def __init__(self,chore_type,chore_text,chore_duration):
        login_creds = pandas.read_csv('email_creds.csv')
        self.login = str(login_creds['email'][0])
        self.password = str(login_creds['password'][0])
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls
        self.day_counter = 0
        self.days_left = None
        self.send_out_interval_in_days = 7 # send weekly emails
        self.current_chore = None
        self.chore_type = chore_type
        self.chore_text = chore_text
        self.first_time = True
        self.chore_duration = chore_duration
        self.run()

    def check_mail(self):
        try:
            print("Checking mail...")
            imapper = easyimap.connect('imap.gmail.com', self.login, self.password)
            for mail_id in imapper.listids(limit=100):
                mail = imapper.mail(mail_id)

                if  self.current_chore.chore_id in mail.title:
                    print(mail.from_addr)
                    print(mail.to)
                    print(mail.cc)
                    print(mail.title)
                    print(mail.body)
                    print(mail.attachments)
                    if "yes" in mail.body.lower():
                        return "Completed"
                    if "pass" in mail.body.lower():
                        return "Reassign"
                return False
        except Exception as e:
            logf = open("error.log", "w")
            logf.write(f'{datetime.now():%Y-%m-%d %H:%M:%S%z}')
            logf.write("Failed to check mail: {0}\n".format(str(e)))
            logf.close()
            print(e)
        finally:
            pass

    def create_chore(self):
        print("CHORE CREATED")
        random_id = ''.join([random.choice(string.ascii_letters
            + string.digits) for n in range(8)])
        winner = self.select_lucky_winner()
        chore = Chore(random_id,winner.name,winner.email,str(date.today()),self.chore_type,self.chore_text,self.chore_duration,False)
        self.current_chore = chore
        self.days_left = None
        return chore

    def select_lucky_winner(self):
        winner = None
        with open("participants.csv") as peeps:
            reader = csv.reader(peeps)
            next(reader) # skip header
            choices = list(reader)
            chore_log = pandas.read_csv("chore_log.csv")
            filtered_by_chore = chore_log[chore_log['chore_type'] == self.chore_type]
            if filtered_by_chore.count>=2:
                recent_winners = self.get_recent_winners(self.chore_type,2)
                choices = [x for x in choices if x not in recent_winners]
            winner = random.choice(choices)
            winner = Participant(winner[0],winner[1])
            print("winner")
            print(winner)
        return winner

    def get_recent_winners(self, chore_type, num_winners ):  # Figure out who recently did chores and leave them out
        chore_log = pandas.read_csv("chore_log.csv")
        filtered_by_chore = chore_log[chore_log['chore_type'] == chore_type]
        #filtered_by_chore = pandas.to_datetime(filtered_by_chore.date)
        #print(filtered_by_chore)
        sorted_by_date = filtered_by_chore.sort_values(by='date')
        print(sorted_by_date)
        last_two = sorted_by_date.tail(2)
        names = last_two['name'].to_list()
        return names



    def send_thanks(self, chore):
        sender = f'From: Speckles T. Mouse <{self.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: YOU COMPLETED THE CHALLENGE: {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'YOU TOOK AWAY MY BEANS AND CHEEZ, but IT LOOKS NICE IN HERE. Ill have to move my party elsewhere for now and listen to sad mouse music Modest Mouse... DONT THINK I WONT BE BACK YOU FOOLS!!!! AND DONT THINK ABOUT GETTING A CAT!!\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)

    def send_reminder(self, chore):
        sender = f'From: Speckles T. Mouse <{self.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: REMINDER - {str(self.get_days_left(self.current_chore))} days left to {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'Did you complete the {chore.chore_text} challenge? I always eat the beans in the meantime! *PARRP* Respond with the word "Yes" to let your mouse overlord (me) know you crushed this motherf---BEEEP chore.\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)

    def send_reassign_notification(self,chore):
        sender = f'From: Speckles T. Mouse <{self.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: I ATE YOUR BEANS AND CHORE IS REASSIGNED - {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'You have lost the challenge! The mouse overlord (me) will eat your beans and cheez in the mean time and p00p your showers and oven!.... Your chore was reassigned to someone else!\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)

    def send_overdue_reminder(self,chore):
        sender = f'From: Speckles T. Mouse <{self.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: CHORE IS OVERDUE BUT NOT CHEEZE {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'Your challenge is overdue by {str(-int(self.get_days_left(self.current_chore)))} cheese cycles (you humans are too silly to know this means what you call days) Did you {chore.chore_text}? Respond "yes" to let your mouse overlord (me) know that you crushed this challenge....\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)


    def send_new_chore(self,chore):
        sender = f'From: Speckles T. Mouse <{self.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: CONGRATULATIONS {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'WINNER!!!11 You have been selected to {chore.chore_text}. You are about to embark on a journey to save Brambleberry from your mouse overlord (me). Do you what it takes... ha ha You have {str(chore.chore_duration)} days to completed this challenge! In any case I will eat all your beans and cheez and all will be sad... but you will have fewer smelly farts. Reply "yes" to this email when you complete this challenge...\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)


    def get_days_left(self,chore):
        start_date = datetime.strptime(chore.start_date, "%Y-%m-%d").date()
        current_date = date.today()
        return int(chore.chore_duration) - (current_date - start_date).days

    def check_way_overdue(self):
        if self.get_days_left(self.current_chore)<(-int(self.current_chore.chore_duration)):
            return True
        else:
            return False

    def check_overdue(self):
        if self.get_days_left(self.current_chore)<0:
            return True
        else:
            return False

    def supervise_chores(self):
        print("SUPERVISING")
        # send out chores if first time
        #  Check for email reponses and say thank you!
        #  Send reminder emails for incomplete chores


        self.day_counter+=1
        self.day_counter = self.day_counter%self.send_out_interval_in_days

        if self.current_chore:
            is_chore_overdue = self.check_overdue()
            is_chore_way_overdue = self.check_way_overdue()
            if(self.check_mail() == "Completed"): #  if Chore was completed and say thank you
                self.send_thanks(self.current_chore)
                days_left = self.complete_chore(self.current_chore)
                if days_left<1:
                    self.send_new_chore(self.create_chore()) #  send out chore to new person if it's time
            elif (is_chore_way_overdue and not self.day_counter) or (self.check_mail() == "Reassign"):
                self.send_reassign_notification(self.current_chore)
                self.current_chore = None
                self.send_new_chore(self.create_chore()) # reassign chore
            elif is_chore_overdue and not self.day_counter:
                self.send_overdue_reminder(self.current_chore)
            elif not self.day_counter:
                self.send_reminder(self.current_chore)
            else:
                pass
        else:
            self.days_left = self.days_left-1
            if self.days_left<1:
                    self.send_new_chore(self.create_chore())



    def complete_chore(self, chore):

        start_date = datetime.strptime(chore.start_date, "%Y-%m-%d").date()
        completion_date = date.today()
        self.days_left = int(chore.chore_duration) - (completion_date - start_date).days
        with open("chore_log.csv", 'a') as chore_log:
            writer = csv.writer(chore_log)
            writer.writerow([chore.chore_id,chore.chore_type,chore.name,completion_date])
        self.current_chore = None
        print("CHORE COMPLETED!")

        return self.days_left

    def send_mail(self,chore, message):

        print(message)

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(self.smtp_server,self.port)
            server.ehlo() # Can be omitted
            server.starttls(context=context) # Secure the connection
            server.ehlo() # Can be omitted
            server.login(self.login, self.password)

            server.sendmail(self.login, chore.email, message)
            print("Message sent!")

        except Exception as e:
            logf = open("error.log", "w")
            logf.write(f'{datetime.now():%Y-%m-%d %H:%M:%S%z}')
            logf.write("Failed to send mail: {0}\n".format(str(e)))
            logf.close()
            print(e)
        finally:
            server.quit()

    def run(self):
        self.send_new_chore(self.create_chore())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pkl_path = 'data.pkl'
    if TEST:
        pass
    else:
        if os.path.exists(pkl_path): # IF PICKLE EXISTS
            myChores = pickle.load(open(pkl_path, 'wb')) # LOAD PICKLE
            for chore in myChores:
                chore.supervise_chores()
            pickle.dump(myChores,open(pkl_path,'wb'))
            pass
        else:
            myChores = []
            with open("chores.csv", 'r') as chorefile:
                reader = csv.reader(list(chorefile))
                header = next(reader) # skip header
                for row in reader:
                    myChores.append(ChoreService(row[0],row[1],row[2])) # create a tracker for each chore
                pickle.dump(myChores,open(pkl_path,'wb'))





