import pymsteams


class MsTeams:
    MY_TEAMS_WEBHOOK = None

    def __init__(self, webhook_url):
        self.MY_TEAMS_WEBHOOK = webhook_url

    def create_ms_teams_notify_object(self):
        try:
            return pymsteams.connectorcard(self.MY_TEAMS_WEBHOOK)
        except:
            print("Failed to create MS Teams instance - No notifications will be send")

    def send_simple_notification(self, text):
        try:
            ms_teams_connectorcard = self.create_ms_teams_notify_object()
            ms_teams_connectorcard.text(str(text))
            ms_teams_connectorcard.send()
        except:
            print(f'Failed to send a message "{str(text)}" to Teams')

    def send_detailed_notification(self, text, title, activity_title, activity_image_url, activity_text):
        try:
            ms_teams_connectorcard = self.create_ms_teams_notify_object()
            # create the section
            ms_teams_card_section = pymsteams.cardsection()
            # Section Title
            ms_teams_card_section.title(title)
            # Activity Elements
            ms_teams_card_section.activityTitle(activity_title)
            ms_teams_card_section.activityImage(activity_image_url)
            ms_teams_card_section.activityText(activity_text)
            ms_teams_connectorcard.addSection(ms_teams_card_section)
            ms_teams_connectorcard.text(text)
            ms_teams_connectorcard.send()
        except:
            print('Failed to notify MS Teams')

# TODO More options
# # Facts are key value pairs displayed in a list.
# myMessageSection.addFact("this", "is fine")
# myMessageSection.addFact("this is", "also fine")
#
# # Section Text
# myMessageSection.text("This is my section text")
#
# # Section Images
# myMessageSection.addImage("http://i.imgur.com/c4jt321l.png", ititle="This Is Fine")
#
# # Add your section to the connector card object before sending
# myTeamsMessage.addSection(myMessageSection)
# myTeamsMessage.text("@OlegSigalov dsdfsdf")
# myTeamsMessage.send()
