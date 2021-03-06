"""Miscellaneous utility functions."""
from __future__ import print_function
from __future__ import unicode_literals

import sys
import io
import os

# Dictionary mapping 'show run' for vendors with different command
SHOW_RUN_MAPPER = {
    'juniper': 'show configuration',
    'juniper_junos': 'show configuration',
    'extreme': 'show configuration',
    'hp_comware': 'display current-configuration',
    'huawei': 'display current-configuration',
    'fortinet': 'show full-configuration',
    'cisco_wlc': 'show run-config',
    'enterasys': 'show running-config',
    'dell_force10': 'show running-config',
    'avaya_vsp': 'show running-config',
    'avaya_ers': 'show running-config',
    'brocade_vdx': 'show running-config',
    'brocade_nos': 'show running-config',
    'brocade_fastiron': 'show running-config',
    'brocade_netiron': 'show running-config',
}

# Expand SHOW_RUN_MAPPER to include '_ssh' key
new_dict = {}
for k, v in SHOW_RUN_MAPPER.items():
    new_key = k + '_ssh'
    new_dict[k] = v
    new_dict[new_key] = v
SHOW_RUN_MAPPER = new_dict

# Default location of netmiko temp directory for netmiko tools
NETMIKO_BASE_DIR = '~/.netmiko'


def load_yaml_file(yaml_file):
    """Read YAML file."""
    try:
        import yaml
    except ImportError:
        sys.exit("Unable to import yaml module.")
    try:
        with io.open(yaml_file, encoding='utf-8') as fname:
            return yaml.load(fname)
    except IOError:
        sys.exit("Unable to open YAML file: {0}".format(yaml_file))


def load_devices():
    """Find and load .netmiko.yml file."""
    yaml_devices_file = find_cfg_file()
    return load_yaml_file(yaml_devices_file)


def find_cfg_file(file_name=None):
    """Look for .netmiko.yml in current dir, then ~/.netmiko.yml."""
    base_file = '.netmiko.yml'
    check_files = [
        base_file,
        os.path.expanduser('~') + '/' + base_file,
    ]
    if file_name:
        check_files.insert(0, file_name)
    for test_file in check_files:
        if os.path.isfile(test_file):
            return test_file
    raise IOError("{File not found in current dir or home dir.".format(base_file))


def display_inventory(my_devices):
    """Print out inventory devices and groups."""
    inventory_groups = ['all']
    inventory_devices = []
    for k, v in my_devices.items():
        if isinstance(v, list):
            inventory_groups.append(k)
        elif isinstance(v, dict):
            inventory_devices.append((k, v['device_type']))

    inventory_groups.sort()
    inventory_devices.sort(key=lambda x: x[0])
    print("\nDevices:")
    print('-' * 40)
    for a_device, device_type in inventory_devices:
        device_type = "  ({})".format(device_type)
        print("{:<25}{:>15}".format(a_device, device_type))
    print("\n\nGroups:")
    print('-' * 40)
    for a_group in inventory_groups:
        print(a_group)
    print()


def obtain_all_devices(my_devices):
    """Dynamically create 'all' group."""
    new_devices = {}
    for device_name, device_or_group in my_devices.items():
        # Skip any groups
        if not isinstance(device_or_group, list):
            new_devices[device_name] = device_or_group
    return new_devices


def obtain_netmiko_filename(device_name):
    """Create file name based on device_name."""
    _, netmiko_full_dir = find_netmiko_dir()
    return "{}/{}.txt".format(netmiko_full_dir, device_name)


def write_tmp_file(device_name, output):
    file_name = obtain_netmiko_filename(device_name)
    with open(file_name, "w") as f:
        f.write(output)
    return file_name


def ensure_dir_exists(verify_dir):
    """Ensure directory exists. Create if necessary."""
    if not os.path.exists(verify_dir):
        # Doesn't exist create dir
        os.makedirs(verify_dir)
    else:
        # Exists
        if not os.path.isdir(verify_dir):
            # Not a dir, raise an exception
            raise ValueError("{} is not a directory".format(verify_dir))


def find_netmiko_dir():
    """Check environment first, then default dir"""
    try:
        netmiko_base_dir = os.environ['NETMIKO_DIR']
    except KeyError:
        netmiko_base_dir = NETMIKO_BASE_DIR
    netmiko_base_dir = os.path.expanduser(netmiko_base_dir)
    if netmiko_base_dir == '/':
        raise ValueError("/ cannot be netmiko_base_dir")
    netmiko_full_dir = "{}/tmp".format(netmiko_base_dir)
    return (netmiko_base_dir, netmiko_full_dir)


def write_bytes(out_data):
    """Write Python2 and Python3 compatible byte stream."""
    if sys.version_info[0] >= 3:
        if isinstance(out_data, type(u'')):
            return out_data.encode('ascii', 'ignore')
        elif isinstance(out_data, type(b'')):
            return out_data
    else:
        if isinstance(out_data, type(u'')):
            return out_data.encode('ascii', 'ignore')
        elif isinstance(out_data, type(str(''))):
            return out_data
    msg = "Invalid value for out_data neither unicode nor byte string: {0}".format(out_data)
    raise ValueError(msg)
