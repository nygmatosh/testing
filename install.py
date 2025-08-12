import os
import subprocess
from datetime import datetime


class StartProject:
    def __init__(self):
        self._main_path = "/usr/src/project/"
        self._compose = "docker compose -f docker-compose.yml"
        self._error = False
        os.chdir(self._main_path)

    
    def _log(self, text):
        try:

            now = (datetime.now()).strftime("%d.%m.%Y %H:%M:%S")

            with open("build_logs.txt", "a+", encoding="utf-8") as f:
                f.write(f"[{now} UTC] {text}\n")

        except Exception as e:
            print(f"{text} -> {e}")

    

    def _is_needed_os(self):
        try:

            cmd = os.popen("hostnamectl").read()

            if cmd.find("Operating System: CentOS") >= 0:
                return True
            return False
        
        except Exception as e:
            self._log(f"_is_needed_os -> {e}")
            self._error = True
            return False




    def _is_install_packet(self, name):
        try:

            cmd = os.popen(f"rpm -q '{name}'").read()
            if cmd.find("is not installed") >= 0:
                return False
            return True
        
        except Exception as e:
            self._log(f"_is_install_packet -> {e}")
            self._error = True
            return True
    



    def _is_exists_network(self, name):
        try:

            cmd = os.popen(f"docker network ls | grep '{name}'").read()

            if len(cmd) > 0:
                return True
            return False
        
        except Exception as e:
            self._log(f"_is_exists_network -> {e}")
            self._error = True
            return True
    




    def _install_docker(self):
        try:

            if not self._is_install_packet("docker-ce"):
                os.system("yum check-update")
                os.system("yum install -y yum-utils device-mapper-persistent-data lvm2")
                os.system("yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo")
                os.system("yum install -y docker-ce")
                os.system("systemctl daemon-reload")
                os.system("systemctl enable docker")
                os.system("systemctl start docker")

        except Exception as e:
            self._error = True
            self._log(f"_install_docker -> {e}")



    def _is_active_docker(self):
        try:

            if os.popen("systemctl is-active docker").read().strip() == "inactive":
                os.system("systemctl start docker")

        except Exception as e:
            self._error = True
            self._log(f"_is_active_docker -> {e}")

    


    def _stop_docker_projects(self):
        """Для избежания конфликтов с портами других проектов"""
        try:

            self._is_active_docker()
            os.system("docker stop $(docker ps -a -q)")

        except Exception as e:
            self._error = True
            self._log(f"_stop_docker_projects -> {e}")




    def _create_docker_network(self):
        try:

            if not self._is_exists_network("autod_aster_3"):
                os.system("docker network create --gateway 172.22.0.1 --subnet 172.22.0.0/16 autod_aster_3")

        except Exception as e:
            self._error = True
            self._log(f"_create_docker_network -> {e}")




    def _build_docker_project(self):
        try:

            self._is_active_docker()
            os.system(f"{self._compose} build")

        except Exception as e:
            self._error = True
            self._log(f"_build_docker_project -> {e}")

    


    def _up_d_docker_project(self):
        try:

            self._is_active_docker()
            os.system(f"{self._compose} up -d")

        except Exception as e:
            self._error = True
            self._log(f"_up_d_docker_project -> {e}")




    def _create_env_file(self):
        try:

            path_script = os.path.join(self._main_path, "configs", "create_env.sh")

            if os.path.exists(path_script):
                subprocess.run(["bash", path_script])

        except Exception as e:
            self._error = True
            self._log(f"_create_env_file -> {e}")




    def _flag_first_install(self):
        try:

            if not os.path.exists(".builded"):
                with open(".builded", "w", encoding="utf-8") as bf:
                    bf.write("builded")

        except Exception as e:
            self._log(f"_flag_first_install -> {e}")




    def run(self):
        if not self._is_needed_os():
            print("Сборщик предназначен только на дистрибутив CentOS -> ошибка")
        else:

            self._install_docker()
            self._create_docker_network()
            self._stop_docker_projects()
            self._create_env_file()

            if not self._error:
                self._build_docker_project()
                self._up_d_docker_project()
                self._flag_first_install()
            else:
                print("Сбока приостановлена из-за ошибок, посмотрите лог файл")