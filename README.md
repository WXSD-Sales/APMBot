# DatadogDemo
This demo has been tested in Python3 only (v3.7.4)

A video walkthrough of this application can be found here:
https://drive.google.com/file/d/1MZzoXa_ZOkpHL1qDP_ZcIHwU4C-YhSVl/view?usp=sharing

# 1
You will need to install the following third party python modules:
```
pip install tornado==4.5.2
```

The following Environment variables are required for this demo, set with the appropriate values:
```
MY_BOT_ID=1234567890
MY_BOT_TOKEN=ABCDEFG-1234-567A_ZYX
MY_SECRET_PHRASE=datadogtestexample
MY_BOT_PORT=8080
DD_API_KEY=abcdefghijklmnop
DD_APPLICATION_KEY=31415826753492031
DD_CREATOR_ID=abcdefgh-12ab-34cd-56ef-ijklmnopqrstu
```

To run this, you can simply run:
```
python datadog_reply.py
```

Using the bot's token, you can get the bot's personId here:
https://developer.webex.com/docs/api/v1/people/get-my-own-details


The DD_API_KEY and DD_APPLICATION_KEY Values need to be setup through Datadog:
https://docs.datadoghq.com/api/latest/authentication/


You can use the Datadog API (https://docs.datadoghq.com/api/latest/users/) to find an appropriate DD_CREATOR_ID value (this will be the user who creates the incident in Datadog).


# 2
You will need to create at least one Webex [webhook](https://developer.webex.com/docs/api/guides/webhooks) to your bot's hosted location + /cards, example:
https://yoursite.com/cards - required fields:
```
      "name": "Attachment Actions Webhook",
      "targetUrl": "https://yoursite.com/cards",
      "resource": "attachmentActions",
      "event": "created",
```

# 3
In addition, you will need a webhook on the Datadog side (https://app.datadoghq.com/account/settings#integrations/webhooks).  The webhook payload you setup should look like this:
```
URL: https://webexapis.com/v1/messages
```
You will need to replace the roomId with a valid Webex [Room (space)](https://developer.webex.com/docs/api/v1/rooms)
```
{
  "roomId": "XXXX",
  "markdown": "DataDog Example Alert",
  "attachments": [
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": 
{
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "TextBlock",
            "size": "Medium",
            "weight": "Bolder",
            "text": "Alert!"
        },
        {
            "type": "FactSet",
            "facts": [
                {
                    "title": "ID",
                    "value": "$ID"
                }
            ]
        },
        {
            "type": "FactSet",
            "facts": [
                {
                    "title": "HOSTNAME",
                    "value": "$HOSTNAME"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "$EVENT_MSG",
            "wrap": true
        },
        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Acknowledge",
                    "data":{"id":"$ID", "submit":"ack"}
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "View",
                    "url":"$LINK"
                },
                {
                    "type": "Action.ShowCard",
                    "title": "New Incident",
                    "card":{"type": "AdaptiveCard",
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "version": "1.2",
                            "body": [
                                    {
                                        "id":"title",
                                        "type": "Input.Text",
                                        "placeholder": "Incident Title",
                                        "spacing": "default"
                                    },
                                    {
                                        "type": "ActionSet",
                                        "actions": [
                                            {
                                                "type": "Action.Submit",
                                                "title": "Create Incident",
                                                "data": {
                                                    "hostname": "$HOSTNAME",
                                                    "url": "$LINK",
                                                    "submit": "inc"
                                                }
                                            }
                                        ]
                                    }
                                ]
                        }
                }
            ]
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
}
]
}
```
You will also need to specify Custom Headers, where the Bearer Token value is replaced by the one you get from [creating a bot of your own.](https://developer.webex.com/my-apps)
```
{"Content-Type":"application/json", "Authorization":"Bearer XXXX_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"}
```
