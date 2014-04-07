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
