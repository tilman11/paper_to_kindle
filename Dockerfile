FROM ubuntu:latest
# TODO: install python, pip3 and other utils
RUN /bin/bash
RUN apt update

# make the k2pdf executable:
COPY k2pdf/k2pdfopt /usr/bin/k2pdfopt
RUN chmod a+x /usr/bin/k2pdfopt 

# python stuff
RUN apt install -y python3 python3-pip cron systemctl
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set destination for COPY
WORKDIR /app

# setup cron
COPY cronfile /etc/cron.d/cronfile
RUN chmod 0644 /etc/cron.d/cronfile

# Apply the cron job
#RUN crontab /etc/cron.d/cronfile
RUN mkdir /app/logs
# Start the cron daemon in the foreground
RUN systemctl start cron.service

# copy the application to the working directory.
COPY . .
RUN mkdir -p temp_files/upload

# startup redis worker
#RUN python3 worker.py


# Run
# production
#EXPOSE 8000
#CMD [ "gunicorn", "--bind=0.0.0.0:8000", "wsgi:app" ]
# dev
EXPOSE 4000
CMD python3 app.py worker.py

