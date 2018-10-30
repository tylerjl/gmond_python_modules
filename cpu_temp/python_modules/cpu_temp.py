#!/usr/bin/env python2
import os

descriptors = list()
sysdirs = [
    ('/sys/devices/platform/', 'coretemp'),
    ('/sys/class/thermal/', 'thermal_zone'),
]
handler_dict = dict()

def metric_init(params):
    global descriptors
    temp_list = []
    for (sysdir, prefix) in sysdirs:
        try:
            temp_list = temp_list + [i for i in os.listdir(sysdir) if i.startswith(prefix)]
        except OSError:
            print 'No dir named' + sysdir + ', skipping'
    if not temp_list:
        print 'No temperature directories found'
        os._exit(1)
    for temp_dir in temp_list:
        coreinput_list = [i for i in os.listdir(sysdir + coretemp) if i.endswith('_input')]
        try:
            with open(sysdir + coretemp + '/temp1_label','r') as f:
                phy_id_prefix = f.read().split()[-1]
        except IOError:
            print 'No temp1_label file'
            os._exit(1)
        for coreinput in coreinput_list:
            build_descriptor(coretemp,coreinput,phy_id_prefix)
    return descriptors

def build_descriptor(coretemp,coreinput,phy_id_prefix):
    global handler_dict
    if coreinput == 'temp1_input':
        name = 'cpu_temp_physical_' + phy_id_prefix
        description = 'Physical CPU id ' + phy_id_prefix + ' Temperature'
        groups = 'cpu_temp_physical'
        handler_dict[name] = sysdir + coretemp + '/temp1_input'
    else:
        with open(sysdir + coretemp + '/' + coreinput[:-6] + '_label','r') as f:
            coreid = f.read().split()[-1]
        name = 'cpu_temp_core_' + phy_id_prefix + '_' + coreid
        description = 'Physical CPU id ' + phy_id_prefix + ' Core ' + coreid + ' Temperature'
        groups = 'cpu_temp_core'
        handler_dict[name] = sysdir + coretemp + '/' + coreinput
    call_back = metric_handler
    d = {'name': name,
        'call_back': call_back,
        'time_max': 60,
        'value_type': 'float',
        'units': 'C',
        'slope': 'both',
        'format': '%.1f',
        'description': description,
        'groups': groups
        }
    try:
        call_back(name)
        descriptors.append(d)
    except:
        print 'Build descriptor Failed'

def metric_handler(name):
    try:
        with open(handler_dict.get(name),'r') as f:
            temp = f.read()
    except:
        temp = 0
    temp_float = int(temp) / 1000.0
    return temp_float

def metric_cleanup():
    pass

if __name__ == '__main__':
     metric_init({})
     for d in descriptors:
         v = d['call_back'](d['name'])
         print 'value for %s is %.1f %s' % (d['name'],v,d['units'])
         for k,v in d.iteritems():
             print k,v
