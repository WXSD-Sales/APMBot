############################################################
# Dockerfile to build APMBot
############################################################
#sudo docker build -f Dockerfile -t apmbot .  #sometimes need to build without cache
#sudo docker run -p 10031:10031 -i -t apmbot
#docker tag apmbot registry.heroku.com/webex-apm-demo/web
#docker push registry.heroku.com/webex-apm-demo/web
#heroku container:release web
###########################################################################

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
