#coding=utf-8
from __future__ import with_statement
import fabric
from fabric.api import local, settings, abort, run, cd , env , task ,parallel , serial
from fabric.contrib.console import confirm
from fabric.colors import red
from fabric.contrib.files import exists
from fabric.utils import abort
from fabric.api import hide, run, get




def add_cron(cron):
    run('sudo crontab -l > /tmp/mycron && echo "%s" >> /tmp/mycron && sudo crontab /tmp/mycron && rm /tmp/mycron'%cron)


def exec_remote_cmd(cmd):
    with hide('output','running','warnings'), settings(warn_only=True):
            return run(cmd)

def get_os_version():
    with hide('output'):
        result = exec_remote_cmd('lsb_release -r -s')
        if result.find("14.04") != -1:
            version = "trusty"

        if result.find("16.04") != -1:
            version = "xenial"
        else:
            print "version: %s not support"
            return None
        return version

@task
def setup_dell_dsm():
    version = get_os_version()
    run('echo "deb http://linux.dell.com/repo/community/ubuntu %s openmanage" |sudo tee  /etc/apt/sources.list.d/linux.dell.com.sources.list'%version)
    run('sudo gpg --keyserver pool.sks-keyservers.net --recv-key 1285491434D8786F')
    run('sudo gpg -a --export 1285491434D8786F | sudo apt-key add -')
    run('sudo apt-get update && sudo apt-get install srvadmin-all')
    run('sudo sudo service dataeng start && sudo service dsm_om_connsvc start')
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
    run("sudo apt-get update && sudo apt-get install python-pip wget screen aptitude lrzsz  vim ntpdate unzip unrar apache2-utils git iftop nload -y && sudo aptitude safe-upgrade -y")

@task
def setup_ntp():
    add_cron("*/2 * * * * /usr/sbin/ntpdate 0.ubuntu.pool.ntp.org;/sbin/hwclock -w;")

@task
def setup_docker():
    run("curl -sSL https://get.docker.com/ | sudo sh")
    run('echo "DOCKER_OPTS=\"--registry-mirror=https://docker.mirrors.ustc.edu.cn\""|sudo tee -a /etc/default/docker')
    setup_docker_compose()
@task
def setup_docker_compose():
    if not run("wget https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m` -O docker-compose").failed:
        run("sudo chmod +x ~/docker-compose && sudo mv ~/docker-compose /usr/local/binsudo chmod +x docker-compose && sudo mv ~/docker-compose /usr/local/bin")

@task
def rsa_gen():
    with settings(warn_only=True):
        if run("test -f ~/.ssh/id_rsa.pub").failed:
            run("ssh-keygen")
    run("cat ~/.ssh/id_rsa.pub")
