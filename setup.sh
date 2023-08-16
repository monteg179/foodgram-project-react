#!/bin/bash

OUT=setup.out
ERR=setup.err

docker_image_prune() {
    echo -n "Docker image prune ..."
    sudo docker image prune -af 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_build() {
    echo -n "Docker compose build ..."
    docker compose build -q 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_pull() {
    echo -n "Docker compose pull ..."
    docker compose pull -q 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_up() {
    echo -n "Docker compose up ..."
    docker compose up -d --wait db backend gateway 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_down() {
    echo -n "Docker compose down ..."
    docker compose down 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_remove() {
    echo -n "Docker compose remove ..."
    docker compose down -v 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_init() {
    echo -n "Docker compose up [frontend] service ..."
    docker compose up frontend 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
        return $error
    fi
    echo -n "[backend] service: waiting [db] service "
    while ! sudo docker compose exec backend nc -zv db 5432 >/dev/null 2>&1
    do
        echo -n "."
        sleep 1
    done
    echo " completed"
    echo -n "[backend] service: django makemigrations ..."
    docker compose exec backend \
        python manage.py makemigrations 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
        return $error
    fi
    echo -n "[backend] service: django migrate ..."
    docker compose exec backend \
        python manage.py migrate 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
        return $error
    fi
    echo -n "[backend] service: import ingredients ..."
    docker compose exec backend \
        python manage.py ingredients data/ingredients.csv 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
        return $error
    fi
    echo -n "[backend] service: import tags ..."
    docker compose exec backend \
        python manage.py tags data/tags.csv 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
        return $error
    fi    
    # echo -n "[backend] service: import database ..."
    # docker compose exec backend \
    #     python manage.py importdb --format csv --path data/import/csv 1> $OUT 2>$ERR
    # error=$?
    # if [ $error -eq 0 ]; then
	#     echo " completed"
    # else
	#     echo " error($error)"
    #     return $error
    # fi
    echo -n "[backend] service: django collectstatic ..."
    docker compose exec backend \
        python manage.py collectstatic 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
        return $error
    fi
    echo -n "[backend] service: copy static ..."
    docker compose exec backend \
        cp -r /app/collected_static/. /staticfiles/static/ 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

case "$1" in
	install)
	    docker_compose_build && docker_compose_up && docker_compose_init
		if [ $? -ne 0 ]; then
			exit 1
		fi
		;;
	uninstall)
        docker_compose_remove && docker_image_prune
		if [ $? -ne 0 ]; then
			exit 1
		fi
		;;
	deploy)
		docker_compose_down && docker_image_prune && docker_compose_pull && docker_compose_up && docker_compose_init
		if [ $? -ne 0 ]; then
			exit 1
		fi
		;;
    *)
        echo "Usage: sudo bash $0 {install | uninstall | deploy}"
        exit 1
        ;;
esac

exit 0