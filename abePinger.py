#!/usr/bin/python3
import os
import time
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import Client

#Global Variables:

GLOBAL_TIME_BETWEEN_FAILURE = 300 # 30 mins in seconds

def ping(hostname):
    response = os.system("ping -c 1 " + hostname + " > /dev/null 2>&1")

    #time.sleep(2)

    #If response, exit code of ping will be 0...therefore successful...
    # if response == 0:
    #   print(hostname + ' is up!')
    #
    # #if response is something else like "exit 512" if unreachable... will be "down"... true
    # else:
    #   print(hostname + ' is down!')

    return response

def sendSMS(message):
    client = Client(twilio_account_sid, twilio_auth_token)

    #Have to assign to an obj, but not really doing anything yet
    sendSMSobj = client.api.account.messages.create(to=ABE_NUMBER,
                                                    from_=TWILIO_NUMBER,
                                                    body=message)

def main():
    abeNetwork = True
    thirty_mins_per_text = None
    thirty_mins_future = None
    initial_fail_text_msg = False
    message_got_sent = False

    message_thirty_minute_failure = "{} is still down since last text.".format(NETWORK_TO_PING)
    message_initial_failure_text = "{} has gone down, will keep pinging see if it comes back up. Investigate circuit.".format(NETWORK_TO_PING)
    message_host_recovered = "{} has come back up, with pings of xxx ms".format(NETWORK_TO_PING)

    # I need a way to return down here, after SMS is out.. like a loop around here... could i do it by class? or objecting?
    # or a larger while loop that never changes main status...
    while abeNetwork == True:

        print("Pinging {}".format(NETWORK_TO_PING))
        ping_results = ping(NETWORK_TO_PING)

        #Since variable is initialized to None, it keeps its value from if ping results to bad fail code!
        #print(str(thirty_mins_per_text))

        if ping_results == 0:
            time.sleep(1)
            #print("Host remains up")
            #Revert initial_fail_text_msg, back to False every ping... so initial if, can ping .. etc
            initial_fail_text_msg = False
            if message_got_sent == True:
                sendSMS(message_host_recovered)
                print(message_host_recovered)
                #Reset states, to not send multiple texts... has to be a better way :(
                message_got_sent = False
                thirty_mins_future = None
                thirty_mins_per_text = None

        if ping_results != 0:

            #Initialize times, if they started at None, and floor division time not picky about decimals.
            if thirty_mins_per_text == None:
                thirty_mins_per_text = (time.time() // 1)
                if thirty_mins_future == None:
                    thirty_mins_future = thirty_mins_per_text + GLOBAL_TIME_BETWEEN_FAILURE

            #if less than 30... we send  message but only if it hasn't already been sent...
            if thirty_mins_per_text < thirty_mins_future:
                thirty_mins_per_text = (time.time() // 1)

                #If initial failed pings isn't sent, sends text, but then won't go again until its reset
                if initial_fail_text_msg == False:
                    sendSMS(message_initial_failure_text)
                    print(message_initial_failure_text)
                    #Sets to True, so it won't keep sending until after 30s, of which it sends in that if conditional
                    #... This will be set to False, in the ping going successful so if it flaps back and forth
                    # i will be notified!
                    initial_fail_text_msg = True
                    message_got_sent = True

                #Logic here, is that if time is less than future, you can start time again, but if time then
                # is equal to over 30 mins... it will then send out text....
                if thirty_mins_per_text > thirty_mins_future:
                    sendSMS(message_thirty_minute_failure)
                    print(message_thirty_minute_failure)
                #print(str(thirty_mins_per_text) + ' is the current time')
                #print("host is down, Sending a Text")
                #sendSMS("Host {} is down, please investigate".format(NETWORK_TO_PING))

            #Once thirty minutes have passed.. and greater than original start, we set objects to None, so timers
            # can start all over again...
            if thirty_mins_per_text > thirty_mins_future:
                #print("30 seconds past, re-initializing times, to None")
                thirty_mins_future = None
                thirty_mins_per_text = None




if __name__ == '__main__':
    main()


