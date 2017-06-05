#!/usr/bin/python3
import os
import time
import subprocess
import re
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import Client

#Global Variables:
NETWORK_TO_PING = ""
ABE_NUMBER = "+"
TWILIO_NUMBER = "+"
twilio_account_sid = ""
twilio_auth_token = ""

GLOBAL_TIME_BETWEEN_FAILURE = 1800 # 30 mins in seconds


class PingableAddress:
    """Pingable Address class, which holds attributes such as ping times, the address, etc."""

    def __init__(self, ipaddr_str):  #devconn_obj):
        self.ip = ipaddr_str
        # TODO: Find out what Connection object I created meant?
        # I believe this meant, for future monitoring of tcp service etc like http.
        #self.connection = devconn_obj
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

    def ping(self):
        #print("Pinging {}".format(self.ip))
        results = subprocess.run(["ping", "-c 1", "{}".format(self.ip)], stdout=subprocess.PIPE, encoding='utf_8')

        if results.returncode == 0:
            msRE = re.search(r'time=(?P<ms>\d+.\d+)\s+', results.stdout)
            self.pingMS = msRE.group('ms')
            self.pingable = True
            self.messageDict['msg_recovered'] = "{} has come back up with {} ms response.".format(self.ip, self.pingMS)
            self.messenger(self.messageDict)

        if results.returncode != 0:
            print(self.ip + ' is failing. Sending appropriate message.')
            self.pingable = False
            self.messenger(self.messageDict)

        time.sleep(1)

        self.pingResults = results
        self.pingReturnCode = results.returncode

        # No need to return, since it will update object itself. but for modulizing could allow an IP input with default
        # return results.returncode, msRE.group('ms')

    def sendSMS(self, message):
        self.twilioClient.api.account.messages.create(to=ABE_NUMBER,
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

def main():
    pingforever = True
    ip_addr = PingableAddress('{}'.format(NETWORK_TO_PING))

    while pingforever == True:
        ip_addr.ping()

if __name__ == '__main__':
    main()
