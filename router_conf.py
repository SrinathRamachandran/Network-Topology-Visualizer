from jnpr.junos import Device
from jnpr.junos.exception import ConnectError, CommitError
from jnpr.junos.utils.config import Config

devices = [
    #insert dict of the conf here

]


for dev in devices:
    try:
        with Device(host=dev['mgnt_ip'], user="labuser", password="Labuser") as device:
            device.bind(conf=Config)
            var_dict = {'if_config': dev['if_config']}
            device.conf.load(template_path = 'template.conf', template_vars = var_dict, merge = True)
            success = device.conf.commit()
            print('Success = {0}'.format(success))
    except ConnectError as err:
        print("\nCannot connect to device: {0}".format(err))
    except CommitError as err:
        print("\nCommit error: " + repr(err))
    except Exception as err:
        print(repr(err))
