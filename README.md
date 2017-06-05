# current Production: abePingerV2.1-sanitized.py

Usage:

Simple code to monitor an IP address via the 'cloud' and receive text messages. I use this to ping my Dynamic DNS IP address at my home.

By default this program will wait 30 minutes between texts (so it does not rack up much text SMS cost : $0.0074/txt USD for US phones)




Instructions:


1. Create an AWS EC2 instance (I used Ubuntu)
2. Fill in your global variables: 
    - IP address to ping
    - Twilio Phone number
    - Your Message number (ABE_NUMBER), where you want the texts)
    - Twilio Account SID
    - Twilio Auth Token

3. Clone the branch and then execute the current production script. 
4. Run the script on the EC2 instance, but need to make it executable: chmod +x ./abePingerV2.1-sanitized.py

If anyone sees this and has a way to do it better, i'm open! still learning Python. 
