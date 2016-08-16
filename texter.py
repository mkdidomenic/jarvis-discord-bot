#python
from twilio.rest import TwilioRestClient


twilioSID = "AC6ed5bac77615f7e3bdad8919bfc042cb"
twilioToken = "13de1b8833b93c4fac03f28e8b670af4"
twilioNumber = "+18622596185"


def sendSMSMessage(recipient_number, message):
    phone = TwilioRestClient(twilioSID, twilioToken)
    message = phone.messages.create(to=recipient_number, from_=twilioNumber,
                             body=message)

def main():
    phone = TwilioRestClient(twilioSID, twilioToken)
    message = phone.messages.create(to="+12012301817", from_=twilioNumber,
                             body="Hello there!")


if __name__ == '__main__':
    main()
