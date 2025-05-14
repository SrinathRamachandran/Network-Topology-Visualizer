from jnpr.junos.utils.config import Config
from jnpr.junos.device import Device
from jnpr.junos.exception import ConnectError, CommitError, RpcError
from lxml import etree as et

devices = [
    #insert the dict of the routers to enable
]
def conf_router(device, dev):
    device.bind(config=Config)
    vars_dict = {"dev_conf": dev}
    device.config.load(merge=True, template_vars = vars_dict, template_path='enable_llpd_temp.conf')
    success = device.config.commit()
    print("{0} success = {1}".format(dev["name"], success))
    return

def enable_lldp(device, dev):
    status = "Enabled"
    try:
        response = device.rpc.get_lldp_information()
        status = response.xpath('lldp-global-status/text()')[0]
        if status == "Disabled":
            conf_router(device, dev)
    except RpcError as err:
        #print(err)
        conf_router(device, dev)
    return
    
for dev in devices:
    try:
        with Device(host = dev['mgnt_ip'], user = 'labuser', password = 'Labuser') as device:
            # Configuring LLPD
            enable_lldp(device, dev)
            
    except ConnectError as err:
        print("connection error: ", repr(err))
    except CommitError as err:
        print("Commit Error: ", repr(err))
    except Exception as err:
        print(repr(err))
