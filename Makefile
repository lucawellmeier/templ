INSTALL_PATH=${HOME}/.local/bin

install:
	chmod +x templ.py
	ln -sf templ.py ${INSTALL_PATH}/templ

