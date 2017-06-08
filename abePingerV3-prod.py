#!/usr/bin/python3
import time
import subprocess
import re
import multiprocessing
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import Client

"""Version 3: Implement 'threading' but as multi-processes to allow multiple IPs to be monitored."""


GLOBAL_TIME_BETWEEN_FAILURE = 60 # 1800 # 30 mins in seconds
SEND_SMS = False

class PingableAddress:
    """Pingable Address class, which holds attributes such as ping times, the address, etc."""

    def __init__(self, ipaddr_str, phoneNumber):
        self.ip = ipaddr_str
        self.sendTextdict = {
            'bool_msg_sent' : False,
            'bool_msg_recovered_sent' : False,
            'bool_msg_down_thirty_mins' : False,
            'time_msg_sent' : None,
            'time_msg_sent_plus_thirty' : None,
            'initial_fail_msg' : False,
        }
        self.pingable = False
        self.pingResults = None
        self.pingReturnCode = None
        self.pingMS = None
        self.messageDict = {
            'msg_down_thirty_mins' : "{} is still down since last text.".format(self.ip),
            'msg_initial_failure' : "{} has gone down. Investigate circuit.".format(self.ip),
            'msg_recovered' : "{} has come back up".format(self.ip)
        }
        self.twilioClient = Client(twilio_account_sid, twilio_auth_token)
        self.phoneTextNotification = phoneNumber

    def ping(self):
        print("Pinging {}".format(self.ip))
        #Class function variables (used to be results =) but it is shared amongst ALL threads  etc...
        self.pingResults = subprocess.run(["ping", "-c 1", "{}".format(self.ip)], stdout=subprocess.PIPE) # Python3.6 encoding='utf_8')

        if self.pingResults.returncode == 0:
            msRE = re.search(r'time=(?P<ms>\d+.\d+)\s+', self.pingResults.stdout)
            self.pingMS = msRE.group('ms')
            self.pingable = True
            self.messageDict['msg_recovered'] = "{} has come back up with {} ms response.".format(self.ip, self.pingMS)
            self.messenger(self.messageDict)

        if self.pingResults.returncode != 0:
            #
            # print(self.ip + ' is failing. Calling Messenger Function.')
            self.pingable = False
            self.messenger(self.messageDict)

        time.sleep(1)

        self.pingReturnCode = self.pingResults.returncode

        # No need to return, since it will update object itself. but for modulizing could allow an IP input with default
        # return results.returncode, msRE.group('ms')

    def sendSMS(self, message):
        if SEND_SMS == True:
            self.twilioClient.api.account.messages.create(to=self.phoneTextNotification,
                                                            from_=TWILIO_NUMBER,
                                                            body=message)

    def messenger(self, message_obj):
        """Messenger is ran with object attributes, just call it from pinger and will send out message IF needed."""

        if self.pingable:
            if self.sendTextdict['bool_msg_sent'] == True:
                print(message_obj['msg_recovered'])
                self.sendSMS(message_obj['msg_recovered'])
                self.sendTextdict['bool_msg_recovered_sent'] = True

            #Pingable Clean ups:
            if self.sendTextdict['bool_msg_recovered_sent']:
                self.sendTextdict['bool_msg_sent'] = False
                self.sendTextdict['bool_msg_recovered_sent'] = False

        if not self.pingable:
            if self.sendTextdict['bool_msg_sent']:
                if self.sendTextdict['time_msg_sent'] == None:
                    self.sendTextdict['time_msg_sent'] = (time.time() // 1)
                    if self.sendTextdict['time_msg_sent_plus_thirty'] == None:
                        self.sendTextdict['time_msg_sent_plus_thirty'] = self.sendTextdict[
                                                                             'time_msg_sent'] + GLOBAL_TIME_BETWEEN_FAILURE
                self.sendTextdict['time_msg_sent'] = (time.time() // 1)
                if self.sendTextdict['time_msg_sent'] > self.sendTextdict['time_msg_sent_plus_thirty']:
                    print(message_obj['msg_down_thirty_mins'])
                    self.sendSMS(message_obj['msg_down_thirty_mins'])
                    self.sendTextdict['bool_msg_down_thirty_mins'] = True

            if not self.sendTextdict['bool_msg_sent']:
                print(message_obj['msg_initial_failure'])
                self.sendSMS(message_obj['msg_initial_failure'])
                self.sendTextdict['bool_msg_sent'] = True
                if self.sendTextdict['time_msg_sent'] == None:
                    self.sendTextdict['time_msg_sent'] = (time.time() // 1)
                    if self.sendTextdict['time_msg_sent_plus_thirty'] == None:
                        self.sendTextdict['time_msg_sent_plus_thirty'] = self.sendTextdict[
                                                                         'time_msg_sent'] + GLOBAL_TIME_BETWEEN_FAILURE

            if self.sendTextdict['bool_msg_down_thirty_mins']:
                self.sendTextdict['bool_msg_down_thirty_mins'] = False
                self.sendTextdict['time_msg_sent'] = None
                self.sendTextdict['time_msg_sent_plus_thirty'] = None

def pingWorker(ip_addr):
    """thread worker function, will allow concurrency for IP addresses to ping."""
    pingforever = True
    while pingforever == True:
        ip_addr.ping()

def main():

    processesList = []
    #spawn 2 pings
    #Must be multi-processig, i think the multi-threading use same bash process ,and something goes hay-wire.. idk
    for p in range(2):
        ip_addr = PingableAddress(ipDict[p],phoneDict[p])
        p = multiprocessing.Process(target=pingWorker, args=(ip_addr,))
        processesList.append(p)
        p.start()

    print("Runs before processes start... for processes!" + str(processesList))

if __name__ == '__main__':
    main()