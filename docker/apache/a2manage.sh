#!/bin/sh

# Usage:
# ./a2manage.sh a2dismod proxy.*
# ./a2manage.sh a2enmod proxy proxy_fcgi ssl

MODS_A_CONF_PATH="/etc/apache2/*.conf"
MODS_B_CONF_PATH="/etc/apache2/conf.d/*.conf"

function a2enmod {
    while test $# -gt 0; do
        MODULE="$1"
        echo "Enabling module $MODULE"
        sed -i "/^#LoadModule ${MODULE}_module/s/^#//g" $MODS_A_CONF_PATH
        sed -i "/^#LoadModule ${MODULE}_module/s/^#//g" $MODS_B_CONF_PATH
        shift
    done
}

function a2dismod {
    while test $# -gt 0; do
        MODULE="$1"
        echo "Disabling module $MODULE"
        sed -i "/^LoadModule ${MODULE}_module/s/^/#/g" $MODS_A_CONF_PATH
        sed -i "/^LoadModule ${MODULE}_module/s/^/#/g" $MODS_B_CONF_PATH
        shift
    done
}

if [ "$1" == "a2enmod" ]; then
    a2enmod "${@:2}"
    exit 0
fi

if [ "$1" == "a2dismod" ]; then
    a2dismod "${@:2}"
    exit 0
fi

echo "a2manage: Unknown command $1"
exit 1
