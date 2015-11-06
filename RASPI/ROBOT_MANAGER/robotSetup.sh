#!/bin/bash
# LA RUTA IDEAL PARA ESTE FICHERO /home/ubuntu/ros_workspace/aristarko/src/robotManager


# ESTE SCRIPT PRETENDE FACILITAR VARIAS TAREAS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   - Si no se inserta ninguna opción, mostrara información de los comandos disponobles.
#   - ros: Se instalara automaticamente ROS version:Indigo
#   - workspace: Se creara el espacio de trabajo y paquete con los nombres introducidos en las siguientes variables
#   - init: carga el archivo robot como arranque
#   - atajo: carga comandos en el bash_aliases para sustituir comandos más largos

# IDEAS FUTURAS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   - REALIZAR BACKUP DEL SISTEMA
#   - OBTENER FUENTES (SRC) DIRECTAMENTE DESDE GIT
#   - DESREGISTRAR EL ARCHIVO ROBOT DE INICIO



# Cargamos el archivo de configuración
ROBOT_DIR=`dirname $0` # Con este comando obtenemos ubicación de este Script
echo ${ROBOT_DIR}"/config"
source ${ROBOT_DIR}"/config" # Cargamos el archivo config que se encuentra en el mismo directorio que este script


# ESPACIO PARA FUNCIONES POSTERIORMENTE UTILIZADAS

    function install_ros {
    # INSTALACION DE ROS
        read -p "¿Desea realizar una instalación de ROS [(Y)es || (N)o]? " -n 1
        echo # Para mover la respuesta una linea abajo
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            # Ajustamos la configuración regional del sistema
            sudo update-locale LANG=C LANGUAGE=C LC_ALL=C LC_MEScd GES=POSIX

            # Añadimos el repositorio, la clave y actualizamos
            sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu trusty main" > /etc/apt/sources.list.d/ros-latest.list'
            wget https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -O - | sudo apt-key add -
            sudo apt-get update

            # Instalamos ROS en su version INDIGO
            sudo apt-get install ros-indigo-ros-base

            # Instalamos Python-rosdep y lo inicializamos
            sudo apt-get install python-rosdep
            sudo apt-get install python-rosinstall
            sudo rosdep init
            rosdep update

            # Cargamos el source que apunta a ROS en el bashrc del
            # Pregunta si se desea modificar el fichero '/etc/modules'
            read -p "¿Desea modificar el fichero '~/.bashrc' para cargar ROS (source /opt/ros/indigo/setup.bash) ? [(Y)es || (N)o]" -n 1
            echo    # (optional) move to a new line
            if [[ $REPLY =~ ^[Yy]$ ]]
            then
                echo "# Cargamos ROS" >> ~/.bashrc
                echo "source "${RUTA_SETUP_GLOBAL} >> ~/.bashrc
                source ~/.bashrc # Actualizamos
            fi
        fi
    }


    function install_workspace {

        # WORKSPACE
        # Una vez instalado ROS vamos a configurar el workspace y el proyecto
        read -p "¿Desea configurar su workspace de ROS, de acuerdo al fichero config? [(Y)es || (N)o]" -n 1
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then

            # Indicamos a ROS que cree el workspace en la ruta especificada
            rosws init ${RUTA_ROS_WS} ${RUTA_ROS}

            # Cargamos el source del Workspace en el bash
            echo "source "${RUTA_SETUP_WS} >> ~/.bashrc
            source ${RUTA_ROS_WS} # Actualizamos

            # Nos aseguramos de que queda cargado
            roscd
            source setup.bash

            # Creamos el paquete
            cd ${RUTA_ROS_WS}
            roscreate-pkg ${NAME_PAQUETE} std_msgs rospy roscpp
            rospack profile

        fi

    }


    function autoarranque {
    # TODO chmod 777
        read -p "¿Desea modificar cargar el archivo robotManager como auto-arranque? [(Y)es || (N)o]" -n 1
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            # Inicio de ROS
            # configuramos el inicio de la maquina
            sudo cp $ROBOT_DIR"/robotManager.sh" /etc/init.d/robotManager.sh
            sudo update-rc.d robotManager.sh defaults 99
        fi
    }


    # Esta funcion configura la maquina para el empleo de comunicacion i2c
    function install_i2c {
        read -p "¿Desea instalar las dependencias para I2C? [(Y)es || (N)o]" -n 1
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
             # Instalamos los paquetes necesarios
            sudo apt-get install python-smbus
            sudo apt-get install i2c-tools

            # Pregunta si se desea modificar el fichero '/etc/modules' para dar al kernel soporte I2C
            read -p "¿Desea modificar el fichero '/etc/modules' para dar al KERNEL soporte I2C ? [(Y)es || (N)o]" -n 1
            echo    # (optional) move to a new line
            if [[ $REPLY =~ ^[Yy]$ ]]
            then
                echo | sudo tee -a /etc/modules
                echo "# I2C Kernel support" | sudo tee -a /etc/modules
                echo "i2c-bcm2708" | sudo tee -a /etc/modules
                echo "i2c-dev" | sudo tee -a /etc/modules
            fi

        fi
    }


    function install_utils {

        echo "Instalar utilidades"

    }


    function download_git {

        read -p "¿Desea descar el proyecto desde el repositorio GIT? [(Y)es || (N)o]" -n 1
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then

            read -p "Introduzca el nombre de la maquina [BBB or PI]: "
            MAQUINA=$REPLY
            read -p "Introduzca el nombre de la RAMA git que desea instalar, dejar en blanco si prefiere la rama Master"
            RAMA=$REPLY

            # Creamos una carpeta temporal
            mkdir "TEMP_GIT"
            cd "TEMP_GIT"

            # Descargamos el Proyecto
            git clone http://crm.in-nova.org:1863/root/ARISTARKO.git

            # Cambiamos de rama si no deseamos la rama Master
            if [ ! -z ${RAMA} ]
            then
                git checkout ${RAMA}
            fi

            # Ahora copiamos nuestro proyecto al SRC
            if [ ${MAQUINA}=="BBB" ]
            then
                cp -r ARISTARKO/BBB_SLAVE_ENCLUSTRA/src/* ${RUTA_CODIGO}
                cp -r ARISTARKO/ROBOT_MANAGER ${RUTA_CODIGO}
            elif [ ${MAQUINA}=="PI" ]
            then
                cp -r ARISTARKO/PI_MASTER/src/* ${RUTA_CODIGO}
                cp -r ARISTARKO/ROBOT_MANAGER ${RUTA_CODIGO}
            fi

            cd ..
            rm -r TEMP_GIT

        fi
    }


    function install_atajos {

        read -p "¿Desea configurar atajos (comandos) ? [(Y)es || (N)o]" -n 1
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            echo "alias robotSetup='bash "${RUTA_ROBOT_MANAGER}"/robotSetup.sh'" >> ~/.bash_aliases
            echo "alias RUTA_CODIGO='cd "${RUTA_CODIGO}"'"  >> ~/.bash_aliases
        fi

    }




# NUCLEO DEL SCRIPT
# En funcion del argumento introducido se realizará una de las siguientes opciones
case "$1" in

    install)
        read -p "Antes de continuar la instalación completa debería de comprobar el archivo config.\n¿Desea continuar? [(Y)es || (N)o]" -n 1
        echo    # (optional) move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            # Instala ROS
            install_ros
            # Configura el workspace
            install_workspace
            # Instala I2C en la maquina
            install_i2c
            # Configura el autoarranque si la maquina es MASTER (Mirar config)
            autoarranque
            # Descarga el proyecto de GITLAB
            download_git
            # Descarga programas utiles
            install_utils
            # Configura los atajos de la terminal
            install_atajos
        fi
    ;;

    ros)
        # Instala ROS en el sistema.
        install_ros
    ;;

    workspace)
        # Configura el workspace de config.
        install_workspace
    ;;

    i2c)
        # Ejecuta la funcion install_i2c la cual configura la maquina para poder emplear i2c
        install_i2c
    ;;


    init)
        # Copaia el fichero robotManager y lo configura como autoranque
        autoarranque
    ;;


    # Con esta opción modificamos el fichero bash_aliases para poder atajos
    atajo)
        install_atajos
    ;;


    # Descargamos el proyecto del repositorio GIT
    # El segundo argumento es la maquina que deseamos copiar (PI or BBB)
    # El tercer parametro es el nombre de la rama (opcional si queremos master).
    backup)
        download_git
    ;;

    utils)
        install_utils
    ;;

    #Si no hemos introducido ninguna de las opciones disponibles nos imprimira esta informacion util
    *)
        echo
        echo "Introduzca como parametro:"
        echo "  * install: Instalación completa."
        echo "  * ros: para una instalacion de ROS."
        echo "  * workspace: para una instalacion de ros_workspace y el paquete aristarko."
        echo "  * init: para configurar el autoarranque de ros y nodo proporcionado por robotManager."
        echo "  * atajo: para escribir en bash_aliases comandos que sustituyan a otros más largos"
        echo "  * backup: para descargar el codigo de los repositorios."
        echo "  * utils: descarga paquetes utiles para la BBB y PI como puede ser el GPIO."
        echo
    ;;

esac