FROM alpine/git as base

# Get the OEG Reporter
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ARG branch=feature/add-wiki-report
RUN git clone --depth=1 git://github.com/hotosm/oeg-reporter.git \
	--branch $branch /usr/src/app

# INSTALLATION
# Install dependencies

FROM python:3.8-buster
ARG GIT_SSH_PRIVATE_KEY
RUN pip install --upgrade pip

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY --from=base /usr/src/app /usr/src/app

# Setup for ssh onto github
RUN mkdir -p /root/.ssh
RUN echo "$GIT_SSH_PRIVATE_KEY" > /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh/id_rsa &&\
	ssh-keyscan github.com >> /root/.ssh/known_hosts

## SETUP
# Setup backend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# INITIALIZATION
EXPOSE 5001
CMD ["python", "manage.py", "runserver", "--port", "5001", "-h", "0.0.0.0"]
