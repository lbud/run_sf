# Deployment process to DigitalOcean

## Create the deployer user

Create the `deployer` user and add to the `admin` group:

```
adduser --disabled-password deployer </dev/null
addgroup admin
adduser deployer admin
```

**Be sure to install your ssh public key for both root and deployer users.**

## Edit the sudoers file to allow no password sudo

Edit the `/etc/sudoers` file:

```
visudo
```

Edit the admin group to allow no password:

```
%admin  ALL=(ALL) NOPASSWD:ALL
```

Save the file and restart the sudo service:

```
service sudo restart
```

## Update the OS

Log out as root, and log back in as deployer. Let's upgrade our OS packages and
restart:

```
sudo aptitude update
sudo aptitude safe-upgrade -y
sudo reboot
```

## Install PostgreSQL/PostGIS and supporting files

```
sudo aptitude install postgresql postgis python-dev libpq-dev -y
```

## Install virtualenv and virtualenvwrapper

```
sudo aptitude install virtualenvwrapper -y
```

Log out and log back in to initialize virtualenvwrapper.

## Install Git

```
sudo aptitude install git -y
```

## Install nginx

```
sudo aptitude install nginx -y
```

## Create the project directory infrastructure

```
mkdir -p ~/apps/run_sf/shared/{config,log,pids,sockets}
mkdir -p ~/apps/run_sf/project
```

Check out the code

```
git clone -q git@github.com:lbud/run_sf.git ~/apps/run_sf/project
```

## Set up uWSGI

1. Copy docs/templates/uwsgi.ini to ~/apps/run_sf/shared/config/
2. Copy docs/templates/uwsgi-run_sf.conf to /etc/init/

## Set up Nginx

Copy docs/templates/nginx-default to /etc/nginx/sites-available/default
