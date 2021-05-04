# APMBot
This demo has been tested in Python3 only (v3.8.1)


<!-- GETTING STARTED -->
### Walkthrough

1. To use this application as it exists in production, [click here](https://webex-apm-demo.herokuapp.com/).
2. Sign in with your Webex account credentials.
3. Toggle the server switch.
[![Switch Screen Shot][switch-screenshot]](https://wxsd-sales.github.io/APMBot/)
4. Check your Webex client. Toggling the switch should have caused the bot to sent you an alert card.
5. Add a comment to the card.
[![Bot Card Screen Shot][bot-screenshot]](https://wxsd-sales.github.io/APMBot/)
6. Submitting the comment should result in an update on the production page after a few seconds:
[![Site Screen Shot][site-screenshot]](https://wxsd-sales.github.io/APMBot/)


A video walkthrough of this application can be found here:
https://drive.google.com/file/d/1MZzoXa_ZOkpHL1qDP_ZcIHwU4C-YhSVl/view?usp=sharing

### Installation

To run this project yourself, you can follow these installation instructions.

1. Clone the repo
   ```sh
   git clone https://github.com/WXSD-Sales/BlurBackground.git
   ```
2. Install the required python modules:
   ```
   pip install pymongo==3.10.1
   pip install pymongo[srv]
   pip install tornado==4.5.2
   pip install requests
   pip install requests-toolbelt
   ```
3. The following Environment variables are required for this demo, set with the appropriate values (see the Environment Variables section below for more details):
      ```
      MY_BOT_ID=1234567890
      MY_BOT_TOKEN=ABCDEFG-1234-567A_ZYX
      MY_SECRET_PHRASE=apmtestexample
      MY_BOT_PORT=10031

      MY_CLIENT_ID=C51234567890
      MY_CLIENT_SECRET=7851234567890
      MY_BASE_URI=https://1234.eu.ngrok.io
      MY_REDIRECT_URI=/auth
      MY_SCOPES=spark%3Akms%20spark%3Apeople_read

      MY_MONGO_URL="mongodb+srv://username:password@your_instance.abcdef.mongodb.net/apm_demo?retryWrites=true&w=majority"
      MY_MONGO_DB=apm_demo
      ```
4. Create the Webhooks (see below).
5. Start the server
   ```
   python apm_bot.py
   ```
   
<!-- ENV VARS -->

## Environment Variables
```
MY_BOT_TOKEN
``` 
1. login to the my-apps section of the [developer portal](https://developer.webex.com/my-apps)
2. Click "Create a New App"
3. Select Bot
4. Fill in the required fields
You will be returned a unique bearer token for the bot.
<br/>

```MY_BOT_ID``` 
This is actually the bot's personId (NOT application_id).  To get the bot's personId, 
1. [click here](https://developer.webex.com/docs/api/v1/people/get-my-own-details).
2. Use the Try It editor on the right side of the page.
3. toggle off the "Use personal access token" switch.
4. paste the bot's token from step 1
5. click Run
The JSON returned will include an "id" property.  This is the bot's personId.
<br/>

```
MY_BASE_URI
```
1. This will need to be a publicly accessible location where your bot will be exposed.  You can use something like [ngrok](https://ngrok.com/) to provide a tunnel from your laptop or desktop to the world.
2. You will use this value again when you create your webhooks, and will use it + ```/auth``` as the redirect_uri when you create the integration for ```MY_CLIENT_ID``` and ```MY_CLIENT_SECRET```.
<br/>

```
MY_REDIRECT_URI=/auth
MY_SCOPES=spark%3Akms%20spark%3Apeople_read
```
These can remain unchanged.
<br/>

```
MY_CLIENT_ID
MY_CLIENT_SECRET
```
1. login to the my-apps section of the [developer portal](https://developer.webex.com/my-apps)
2. Click "Create a New App"
3. Select Integration
4. Fill in the required fields.<br/>
      a. Your redirect_uri value when creating this integration will need to be the ```MY_BASE_URI``` + ```MY_REDIRECT_URI``` values<br/>
      b. For example, if you were to use the values given in the examples from the Installation step, your redirect_uri would be:<br/>
      ```https://1234.eu.ngrok.io/auth```<br/>
You will be returned a unique clientId and clientSecret when the application is created.
<br/>

```
MY_MONGO_URL
```
You will need a MongoDB instance to store data.  You can setup a free cluster using MongoDB [Atlas](https://cloud.mongodb.com).
Notice the url in the example wraps the string in quotation marks ```"```.  Be aware of any special characters when setting the environment variables.
<br/>

```
MY_MONGO_DB=apm_demo
```
This can remain unchanged.  Remember to update the DB in the ```MY_MONGO_URL``` string to match this value.


<!-- WEBHOOKS -->

## Webhooks

This application requires 2 webhooks. To create them through the developer portal [click here](https://developer.webex.com/docs/api/v1/webhooks/create-a-webhook).
1.Use the Try It Editor on the right side of the page
2.Untoggle the "Use my personal access token" switch
3.Paste the bot's token in that field.
4.Enter any name
5.targetUrl: Enter your ```BASE_URI```
6.resource: ```messages```
7.event: ```created```
8.secret: Enter your ```MY_SECRET_PHRASE``` value
<br/>
Repeat this process a second time, to create an attachment Action webhook, will slight differences:
4.Enter any name
5.targetUrl: Enter your ```BASE_URI``` + ```/cards```
6.resource: ```attachmentActions```
7.event: ```created```
8.secret: Enter your ```MY_SECRET_PHRASE``` value


<!-- CONTACT -->

## Contact

Cisco Center of Excellent Developers - wxsd@external.cisco.com

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[switch-screenshot]: static/images/walkthrough/demo-switch.png
[site-screenshot]: static/images/walkthrough/demo-site.png
[bot-screenshot]: static/images/walkthrough/demo-bot-card.png
