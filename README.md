# abePinger
First attempt is complete.

Using an UBUNTU EC2 instance, which will ping my 'public-ddns' IP address, then report to my number and will be delayed every 30 minutes, so it does not take up more than 1 text per 30 mins.. unless my IP comes back up and is reachable...

chmod +x ./abePinger.py,

you need to add the following Global variables but don't include them as Twilio's API needs a specific KEY: 

NETWORK_TO_PING = "10.99.99.99"
ABE_NUMBER = "+15551234567"
TWILIO_NUMBER = "+15551237777"

twilio_account_sid = "ACxxxxxxxxxxxx"
twilio_auth_token = "xxxxxxxxxxxxxxx"



I will be expanding this to maybe even gather further facts from my network, like server status, basic TCP conn tests...



If anyone sees this and has a way to do it better, i'm open! still learning Python. 
