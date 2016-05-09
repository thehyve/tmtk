from tmtk.arborist import app
import socket
import argparse
import webbrowser

parser = argparse.ArgumentParser(description='Launch the Arborist')
parser.add_argument('--debug', action="store_true", default=False, help="Run in debug mode")
parser.add_argument('--port', type=int, default=26747,
                    help="Set port to try to listen to. Tries 26747 by default. If busy "
                         "the OS is asked what port to use.")
args = parser.parse_args()


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def try_port(port_number=None):
    if not port_number:
        port = get_open_port()
    else:
        port = port_number

    if not args.debug:
        running_on = 'http://localhost:{}'.format(port)
        webbrowser.open(running_on, new=0, autoraise=True)

    app.run(debug=args.debug, port=port)


try:
    try_port(args.port)
except OSError:
    print("Port taken, asking OS for an available port.")
    try_port()
