#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/keisoku/catkin_ws/src/hsrb_samples/hsrb_vision_samples"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/keisoku/catkin_ws/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/keisoku/catkin_ws/install/lib/python3/dist-packages:/home/keisoku/catkin_ws/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/keisoku/catkin_ws/build" \
    "/usr/bin/python3" \
    "/home/keisoku/catkin_ws/src/hsrb_samples/hsrb_vision_samples/setup.py" \
     \
    build --build-base "/home/keisoku/catkin_ws/build/hsrb_samples/hsrb_vision_samples" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/keisoku/catkin_ws/install" --install-scripts="/home/keisoku/catkin_ws/install/bin"