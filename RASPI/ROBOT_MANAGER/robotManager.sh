#!/bin/bash -e

# El siguiente proceso generalmente es automatizado por el script robotSetup.sh init
#
#   Este es el fichero debe de colocarse en la ruta /etc/init.d/
#
#   Deberá ser creado un enlace simbolico en los runlevels del sistema.
#       sudo update-rc.d robot defaults 99
#
#   Si queremos borrar el enlace simbolico en los en los runlevels del sistema.
#       sudo update-rc.d -f robot remove



# Variable que contiene la ruta hacia la carpeta robotmanager donde se encuentran los script.
RUTA_MANAGER="/home/ubuntu/ros_workspace/wearable/ROBOT_MANAGER"
# Carga el archivo config de robotManager el cual contiene variables.
source ${RUTA_MANAGER}"/config"


# LOS SIGUIENTES COMANDOS SIRVEN PARA REGISTRAR LOS RESULTADOS DE ESTE SCRIPT EN DOS FICHEROS
# EN EL FICHERO STDOUT.LOG SE REGISTRAN LOS MENSAJES DE PANTALLA Y EN STDOUT LOS MENSAJES DE ERROR
# EN EL CASO DE NO QUERER GUARDARLOS EN FICHERO Y PODER VERLOS POR PANTALLA PONER DEBUG EN FALSE.

    # Esta funcion añade a las lineas de stdout y stderr el tiempo en el que se ha ejecutado el registro
    stamp ()
    {
      local LINE
      while IFS='' read -r LINE; do
        echo "[ $(date '+%d-%m-%Y %H:%M:%S') ] $$ "${LINE}
      done
    }

    # Si el modo debug esta activado -> escribiremos los resultados en dos logs
    # Un log (stdout) muestra los resultados o impresiones en pantalla
    # Otro log (stderr) muestra los errores obtenidos
    if [ "$DEBUG" = true ] ; then

        # Introducimos una cabecera en los log
        /bin/echo | tee -a ${LOG_ERR} ${LOG_OUT}
        /bin/echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - | tee -a ${LOG_ERR} ${LOG_OUT}
        /bin/echo "NUEVA SESION: $(date '+%d-%m-%Y %H:%M:%S')" | tee -a ${LOG_ERR} ${LOG_OUT}
        /bin/echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - | tee -a ${LOG_ERR} ${LOG_OUT}
        /bin/echo | tee -a ${LOG_ERR} ${LOG_OUT}

        # Con los siguientes comandos redirigimos a stderr.log y stdout.log si DEBUG es true
        exec {STDOUT}>&1
        exec {STDERR}>&2
        exec 2> >(exec {STDOUT}>&-; exec {STDERR}>&-; exec &>> ${LOG_ERR}; stamp)
        exec > >(exec {STDOUT}>&-; exec {STDERR}>&-; exec >> ${LOG_OUT}; stamp)
        # exec > mytest.log 2>&1 # Si queremos que out y err esten en un mismo fichero

    fi



# A CONTINUACION SE EJECUTA EL SCRIPT EL CUAL SE ENCUENTRA DIVIDIDO EN PARTES MEDIANTE UN CASE
# PARA REALIZAR DIFERENTES ACCIONES SEGUN SEA EL INICIO, REINICIO O APAGADO DEL MICRO

case "$1" in

   # En el caso de que el sistema arranque:
   start)

        # archivo_configuracion es la ruta del archivo donde se encuentran las variables de la maquina.
        archivo_configuracion="/home/ubuntu/ros_workspace/aristarko/src/robotManager/config"

        # Cargamos el archivo de configuración
        echo
        echo "CARGAMOS EL ARCHIVO CONFIG"
        echo "Ruta de ROS: "${RUTA_SETUP_GLOBAL}
        echo "Ruta de WORKSPACE: "${RUTA_SETUP_WS}
        echo "IP_MASTER: "${IP_MASTER}
        echo "IP_MAQUINA: "${IP_LOCAL}


        # ARRANCAMOS ROS
        source ${RUTA_SETUP_GLOBAL}
        source ${RUTA_SETUP_WS}

        # INDICAMOS IP LOCAL E IP DEL MASTER
        export ROS_MASTER_URI='http://'$IP_MASTER':11311'
        export ROS_IP=$IP_LOCAL
        export ROS_PACKAGE_PATH=${RUTA_ROS_PKG}:/opt/ros/indigo/share:/opt/ros/indigo/stacks

        # Para resolver error especial de BBB (Carlos)
        # Volvemos a cargar el setup de ROS porque se borran algunas configuraciones
        # source ${RUTA_ROS}

        # Si la ip_master es la misma que ip_maquina
        # Vamos a inicializar ros en un proceso aparte con &
        if [ $IP_MASTER==$IP_LOCAL ]
        then
            echo
            echo "Como IP_MASTER == IP_MAQUINA INICIAMOS ROS"
            roscore &
        fi

        # Ejecutamos los archivos python necesarios
        while [ "x${EXE_PYTHON[count]}" != "x" ]
        do
           echo
           echo "Vamos a ejecutar los archivos python"
           echo ${EXE_PYTHON[count]}
           /usr/bin/python2.7 ${EXE_PYTHON[count]} &
           count=$(( $count + 1 ))
        done

    ;;


  # En caso de que la maquina se apague.
  stop)

    echo "Stopping robot"
    echo "robotManager -> me estoy apagando"

    #killall nodes
    for i in $( rosnode list ); do
    rosnode kill $i;
    done

    #stop roscore
    killall roscore
    killall python
    ;;


  # En caso de reinicio
  restart)
    echo Reinicio del Sistema >> /home/ubuntu/reinicio
    ;;


  # Resto de casos
  *)
    echo "Usage: /etc/init.d/robot{start|stop}"
    exit 1
    ;;


esac

exit 0
