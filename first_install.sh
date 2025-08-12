#!/bin/bash

FILE=/usr/src/project/.builded

if [ ! -f "$FILE" ]; then
    echo "Подготавливаю сервер к первой установке"

    sed -i s/SELINUX=enforcing/SELINUX=disabled/g /etc/selinux/config
    sudo sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
    sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
    sudo dnf -y update
    sudo dnf -y install nano wget unzip python3
    sleep 3

fi

echo "Вызываю основной скрипт установки проекта"
python3 /usr/src/project/install.py