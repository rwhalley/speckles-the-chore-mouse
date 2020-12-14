import smtplib, ssl
import os
import re
import easyimap
import time
import random
import string
import csv
from email.message import EmailMessage
from datetime import date, datetime
import pandas
import pickle
import email.utils
import time
import copy

from participant import Participant
from chore import Chore

TEST = False


class State:
    def __init__(self,chore_type,chore_text,chore_duration):
        login_creds = pandas.read_csv('email_creds.csv')
        self.login = str(login_creds['email'][0])
        self.password = str(login_creds['password'][0])
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls
        self.day_counter = 0
        self.queue_chore = True
        self.days_left = None
        self.send_out_interval_in_days = 7 # send weekly emails
        self.current_chore = None
        self.chore_type = chore_type
        self.chore_text = chore_text
        self.first_time = True
        self.last_checked = datetime.now()
        self.chore_duration = chore_duration
        self.reminder_sent_today = False


class MailChecker:
    def __init__(self):
        self.mail = None
        login_creds = pandas.read_csv('email_creds.csv')
        self.login = str(login_creds['email'][0])
        self.password = str(login_creds['password'][0])
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls

    def get_mail(self):
        print("Downloading mail...")
        try:
            imapper = easyimap.connect('imap.gmail.com', self.login, self.password)
            self.mail = []
            for mail_id in imapper.listids(limit=100):
                self.mail.append(imapper.mail(mail_id))
            return self.mail
        except Exception as e:
            logf = open("error.log", "w")
            logf.write(f'{datetime.now():%Y-%m-%d %H:%M:%S%z}')
            logf.write("Failed to check mail: {0}\n".format(str(e)))
            logf.close()
            print(e)
        finally:
            return self.mail


class ChoreService:
    def __init__(self,state,mail):
        self.mail = mail
        self.state = state
        self.COMPLETED = 100

    def check_mail(self):
        try:
            print("Parsing mail...")
            print(self.state.chore_type)
            print(self.state.current_chore.email)
            print(self.state.current_chore.chore_id)
            for mail in self.mail:
                splittxt = "> wrote:" #removes lower emails in thread
                text = mail.body.lower().split(splittxt,1)[0]
                email_datetime = datetime.fromtimestamp(time.mktime(email.utils.parsedate(mail.date)))
                #print(mail.title)
                #print(text)
                #print(self.state.current_chore.chore_type)
                #print(datetime.now())
                #print(email_datetime)
                #print(self.state.last_checked)


                if "override" in mail.title \
                        and (datetime.now()-email_datetime).total_seconds()<((datetime.now()-self.state.last_checked).total_seconds()) \
                        and self.state.current_chore.chore_type in text:
                    print("Override")

                    if "yes" in text:
                        df = pandas.read_csv("participants.csv")
                        parsed_from_addr = re.findall('\S+@\S+',str(mail.from_addr))[0].replace('<','').replace('>','')
                        self.state.current_chore.name = df.loc[df.email == parsed_from_addr, 'name'].values[0]
                        self.state.current_chore.email = parsed_from_addr
                        return self.COMPLETED
                    elif "pass" in text:
                        print("Reassign")
                        return "Reassign"

                if  self.state.current_chore.chore_id in mail.title:
                    print(mail.from_addr)
                    print(mail.date)
                    print(mail.to)
                    print(mail.cc)
                    print(mail.title)
                    print(mail.body)
                    print(mail.attachments)

                    if "yes" in text:
                        print("COMPLETED")
                        return self.COMPLETED
                    if "pass" in text:
                        print("REASSIGN")
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
        chore = Chore(random_id,winner.name,winner.email,str(date.today()),self.state.chore_type,self.state.chore_text,self.state.chore_duration,False)
        self.state.current_chore = chore
        self.state.days_left = None
        return chore

    def select_lucky_winner(self):
        winner = None
        with open("participants.csv") as peeps:
            reader = csv.reader(peeps)
            next(reader) # skip header
            choices = list(reader)
            chore_log = pandas.read_csv("chore_log.csv")
            filtered_by_chore = chore_log[chore_log['chore_type'] == self.state.chore_type]
            if len(filtered_by_chore.index)>=2:
                recent_winners = self.get_recent_winners(self.state.chore_type,2)
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
        sender = f'From: Speckles T. Mouse <{self.state.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: YOU COMPLETED THE CHALLENGE: {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'YOU TOOK AWAY MY BEANS AND CHEEZ, but IT LOOKS NICE IN HERE. Ill have to move my party elsewhere for now and listen to sad mouse music Modest Mouse... DONT THINK I WONT BE BACK YOU FOOLS!!!! AND DONT THINK ABOUT GETTING A CAT!!\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)

    def send_reminder(self, chore):
        sender = f'From: Speckles T. Mouse <{self.state.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: REMINDER - {str(self.get_days_left(self.state.current_chore))} days left to {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'Did you complete the {chore.chore_text} challenge? I always eat the beans in the meantime! *PARRP* \n\nRespond with the word "Yes" to let your mouse overlord (me) know you have completed this chore.\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)

    def send_reassign_notification(self,chore):
        sender = f'From: Speckles T. Mouse <{self.state.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: I ATE THE BEANS AND CHORE IS REASSIGNED - {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'You have lost the challenge! The mouse overlord (me) will eat your beans and cheez in the mean time and p00p your showers and oven!.... Your chore was reassigned to another lucky winner..!\n\n You do not need to respond to this email.'

        message = sender+to+subject+text

        self.send_mail(chore,message)

    def send_overdue_reminder(self,chore):
        sender = f'From: Speckles T. Mouse <{self.state.login}>\n'
        to = f'To: <{chore.email}>\n'
        subject = f"Subject: CHORE IS OVERDUE BUT NOT CHEEZE {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'Your challenge is overdue by {str(-int(self.get_days_left(self.state.current_chore)))} cheese cycles (you humans are too silly to know this means what you call days) \n\n Did you {chore.chore_text}? \n\nRespond "yes" to let your mouse overlord (me) know that you crushed this challenge....\n'

        message = sender+to+subject+text

        self.send_mail(chore,message)


    def send_new_chore(self,chore):
        sender = f'From: Speckles T. Mouse <{self.state.login}>\n'
        to = f'To: <{chore.email}>\n'
        overdue_days = int(chore.chore_duration) + int(chore.chore_duration)
        subject = f"Subject: CONGRATULATIONS {chore.chore_text} {str(chore.chore_id)}\n"
        text = f'WINNER!!!11 You have been selected to {chore.chore_text}. You are about to embark on a journey to clean Brambleberry before your mouse overlord (me) takes over the land. Do what it takes... ha ha \n\nYou have {str(chore.chore_duration)} days to complete this challenge! \n\nIn any case I will eat all your beans and cheez and all will be mine... \n\nNote: You do not have to reply to this email right now.\nYou will receive weekly reminders until you complete or reassign the chore.\nReply "yes" to this email when you complete this challenge... \nRespond "pass" to randomly reassign this chore to someone else if you are not going to be around.\nIf you wait {str(overdue_days)} days, your chore will be considered way overdue and automatically be reassigned.'

        message = sender+to+subject+text

        self.send_mail(chore,message)


    def get_days_left(self,chore):
        start_date = datetime.strptime(chore.start_date, "%Y-%m-%d").date()
        current_date = date.today()
        return int(chore.chore_duration) - (current_date - start_date).days

    def check_way_overdue(self):
        if self.get_days_left(self.state.current_chore)<(-int(self.state.current_chore.chore_duration)):
            return True
        else:
            return False

    def check_overdue(self):
        if self.get_days_left(self.state.current_chore)<0:
            self.state.current_chore.overdue = True
            return True
        else:
            self.state.current_chore.overdue = False
            return False

    def update_last_checked_time(self):
        self.state.last_checked = datetime.now()

    def supervise_chores(self):
        print("SUPERVISING")
        # send out chores if first time
        #  Check for email reponses and say thank you!
        #  Send reminder emails for incomplete chores


        # if it's a new day, increase counter
        if self.state.last_checked.date() < datetime.now().date():
            self.state.day_counter+=1
            self.state.day_counter = self.state.day_counter%self.state.send_out_interval_in_days
            self.state.reminder_sent_today = False

        # regardless of counter, check mail

        # if new mail came in, do something about it
        # if it was a pass, it gets reassigned
        # if it was a completion, it also gets put in queue for reassignment
        if self.state.current_chore:
            result = self.check_mail()
            if(result == self.COMPLETED and self.state.current_chore): #  if Chore was completed and say thank you
                self.send_thanks(self.state.current_chore)
                self.state.days_left = self.complete_chore(self.state.current_chore)
                if self.state.days_left<1:
                    self.send_new_chore(self.create_chore()) #  send out chore to new person if it's time
            elif (self.check_way_overdue() and not self.state.day_counter and self.state.current_chore) or (result == "Reassign"):
                self.send_reassign_notification(self.state.current_chore)
                self.state.current_chore = None
                self.send_new_chore(self.create_chore()) # reassign chore
            elif self.check_overdue() and not self.state.day_counter:
                self.send_overdue_reminder(self.state.current_chore)
            elif (self.state.day_counter == (self.state.send_out_interval_in_days-1)) and not self.state.reminder_sent_today:
                self.state.reminder_sent_today = True
                self.send_reminder(self.state.current_chore)
        else:
            self.state.days_left = self.state.days_left-1
            if self.state.days_left<1:
                self.send_new_chore(self.create_chore())



    def complete_chore(self, chore):

        start_date = datetime.strptime(chore.start_date, "%Y-%m-%d").date()
        completion_date = date.today()
        self.state.days_left = int(chore.chore_duration) - (completion_date - start_date).days
        print("DAYS LEFT")
        print(self.state.days_left)
        with open("chore_log.csv", 'a') as chore_log:
            writer = csv.writer(chore_log)
            writer.writerow([chore.chore_id,chore.chore_type,chore.name,chore.email,completion_date])
        self.state.current_chore = None
        print("CHORE COMPLETED!")

        return self.state.days_left

    def send_mail(self,chore, message):

        print(message)

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(self.state.smtp_server,self.state.port)
            server.ehlo() # Can be omitted
            server.starttls(context=context) # Secure the connection
            server.ehlo() # Can be omitted
            server.login(self.state.login, self.state.password)

            server.sendmail(self.state.login, chore.email, message)
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
            myChores = pickle.load(open(pkl_path, 'rb')) # LOAD PICKLE
            mice = []
            checker = MailChecker()
            mail = checker.get_mail()
            for chore in myChores:
                speckles = ChoreService(chore,copy.deepcopy(mail))
                speckles.supervise_chores()
                speckles.update_last_checked_time()
                mice.append(speckles)
            myChores = []
            for mouse in mice:
                myChores.append(mouse.state)
            pickle.dump(myChores,open(pkl_path,'wb'))
            pass
        else:
            myChores = []
            with open("chores.csv", 'r') as chorefile:
                reader = csv.reader(list(chorefile))
                header = next(reader) # skip header
                mice = []
                for row in reader:
                    print(row[0])
                    print(row[1])
                    print(row[2])
                    chore = State(row[0],row[1],row[2])
                    speckles = ChoreService(chore,[])
                    speckles.run()
                    myChores.append(speckles.state) # create a tracker for each chore
                pickle.dump(myChores,open(pkl_path,'wb'))





