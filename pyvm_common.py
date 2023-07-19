import atexit
from pyVim.connect import SmartConnect, Disconnect


def service_instance_connect(**kwargs):
    """
    Determine the most preferred API version supported by the specified server,
    then connect to the specified server using that API version, login and return
    the service instance object.
    """

    service_instance = None

    # form a connection...
    try:
        if kwargs.get('disable_ssl_verification') or kwargs.get('disable_ssl_verification', None) is None:
            service_instance = SmartConnect(
                host=kwargs.get('host'),
                user=kwargs.get('username'),
                pwd=kwargs.get('password'),
                disableSslCertValidation=True
            )
        else:
            service_instance = SmartConnect(
                host=kwargs.get('host'),
                user=kwargs.get('username'),
                pwd=kwargs.get('password')
            )

        # doing this means you don't need to remember to disconnect your script/objects
        atexit.register(Disconnect, service_instance)
    except IOError as io_error:
        print(io_error)

    if not service_instance:
        raise SystemExit("Unable to connect to host with supplied credentials.")

    return service_instance


def service_instance_disconnect(client):
    Disconnect(client)