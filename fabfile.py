#coding=utf-8
from __future__ import with_statement
import fabric
from fabric.api import local, settings, abort, run, cd , env , task ,parallel , serial
from fabric.contrib.console import confirm
from fabric.colors import red
from fabric.contrib.files import exists
from fabric.utils import abort


def add_cron(cron):
    run('sudo crontab -l > /tmp/mycron && echo "%s" >> /tmp/mycron && sudo crontab /tmp/mycron && rm /tmp/mycron'%cron)

@task
def setup_all():
    setup_dns()
    setup_timezone()
    setup_common_pg()
    setup_docker()


@task
def setup_dns():
    run("echo 'nameserver 114.114.114.114' |sudo tee -a /etc/resolv.conf && echo 'nameserver 61.147.37.1' |sudo tee -a /etc/resolvconf/resolv.conf.d/base && echo 'nameserver 114.114.114.114' |sudo tee -a /etc/resolvconf/resolv.conf.d/base && sudo /etc/init.d/resolvconf restart")

@task
def setup_timezone():
    run("echo 'Asia/Shanghai' |sudo tee  /etc/timezone")

@task
def setup_common_pg():
    run('sudo sed -i "s/http:\/\/archive\.ubuntu\.com/http:\/\/mirrors.163.com/" /etc/apt/sources.list  && sudo sed -i "s/http:\/\/us\.archive\.ubuntu\.com/http:\/\/mirrors.163.com/" /etc/apt/sources.list')
    run("sudo apt-get update && sudo apt-get install wget screen aptitude lrzsz  vim ntpdate unzip unrar apache2-utils git iftop nload -y && sudo aptitude safe-upgrade -y")

@task
def setup_ntp():
    add_cron("*/2 * * * * /usr/sbin/ntpdate 0.ubuntu.pool.ntp.org;/sbin/hwclock -w;")

@task
def setup_docker():
    run("curl -sSL https://get.docker.com/ | sudo sh")
    if not run("wget https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m` -O docker-compose").failed:
        run("sudo chmod +x docker-compose && sudo mv ./docker-compose /usr/local/binsudo chmod +x docker-compose && sudo mv ./docker-compose /usr/local/bin")

@task
def rsa_gen():
    print("host:%s  %s"%(env.host , hostnames.get(env.host)))
    with settings(warn_only=True):
        if run("test -f ~/.ssh/id_rsa.pub").failed:
            run("ssh-keygen")
    run("cat ~/.ssh/id_rsa.pub")
