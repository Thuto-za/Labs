from twilio.rest import Client

sid = ""
authToken = ""
client = Client(sid, authToken)

message = client.messages.create(to="whatsapp:+27649494279",
    from_="whatsapp:+14155238886",
    body="Code Jana twilio test."
)
print(message.sid)