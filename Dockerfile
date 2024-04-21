FROM ubuntu:latest
# TODO: install python, pip3 and other utils
RUN /bin/bash
RUN apt update

# make the k2pdf executable:
COPY k2pdf/k2pdfopt /usr/bin/k2pdfopt
RUN chmod a+x /usr/bin/k2pdfopt 

# python stuff
RUN apt install -y python3 python3-pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set destination for COPY
WORKDIR /app

# copy the application to the working directory.
COPY . .
RUN mkdir -p temp_files/upload
# i think the temp_files/uploads folder is missing

EXPOSE 8000

# Run
CMD [ "gunicorn", "--bind=0.0.0.0:8000", "wsgi:app" ]