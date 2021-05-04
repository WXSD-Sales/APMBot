############################################################
# Dockerfile to build APMBot
############################################################
#sudo docker build -f Dockerfile -t apmbot .  #sometimes need to build without cache
#sudo docker run -p 10031:10031 -i -t apmbot
#docker tag apmbot registry.heroku.com/webex-apm-demo/web
#docker push registry.heroku.com/webex-apm-demo/web
#heroku container:release web
###########################################################################

#TODO: MONDAY:
#4. setup a real remote git origin on WXSDSales (not heroku git)

#5. Footer (wxsd@external.cisco.com)
#6. Header APM Notification Bot
#9. Add Comments & Logs Header section
#7. Hardcode server IP, Incident ID (consistent naming on both sides)
#8. Add Help message that tells what to do.

FROM python:3.7.4

# File Author / Maintainer
MAINTAINER "Taylor Hanson <tahanson@cisco.com>"

# Copy the application folder inside the container
ADD . .

# Set the default directory where CMD will execute
WORKDIR /

# Get pip to download and install requirements:
RUN pip install pymongo==3.10.1
RUN pip install pymongo[srv]
RUN pip install tornado==4.5.2
RUN pip install requests
RUN pip install requests-toolbelt

# Set the default command to execute
# when creating a new container
CMD ["python","-u","apm_bot.py"]
