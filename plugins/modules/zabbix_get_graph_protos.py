#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) ben@dataraven.co.uk
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

RETURN = r"""
---
hosts:
    description: item
    returned: success
    type: int
    sample: 12345
"""

DOCUMENTATION = r"""
---
module: zabbix_get_graph_protos
short_description: Get graph prototype info
description:
    - This module allows you to search for the graph info of specific graph prototypes on a specific host
author:
    - "Ben Albon (ben@dataraven.co.uk)"
requirements:
    - "python >= 3.9"
options:
    host_id:
        description:
            - id number of the host in Zabbix
        required: true
        type: list
    search:
        description:
            - search paramaters
        required: false
        type: dict
        default: {}
    searchByAny:
        description:
            - return results that match any of the search criteria (rather than all)
        required: false
        type: bool
        default: false
extends_documentation_fragment:
- community.zabbix.zabbix

"""

EXAMPLES = r"""
# If you want to use Username and Password to be authenticated by Zabbix Server
- name: Set credentials to access Zabbix Server API
  ansible.builtin.set_fact:
    ansible_user: Admin
    ansible_httpapi_pass: zabbix

# If you want to use API token to be authenticated by Zabbix Server
# https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/administration/general#api-tokens
- name: Set API token
  ansible.builtin.set_fact:
    ansible_zabbix_auth_key: 8ec0d52432c15c91fcafe9888500cf9a607f44091ab554dbee860f6b44fac895

- name: Get Disk space usage graph prototype
    # set task level variables as we change ansible_connection plugin here
    vars:
        ansible_network_os: community.zabbix.zabbix
        ansible_connection: httpapi
        ansible_httpapi_port: 443
        ansible_httpapi_use_ssl: true
        ansible_httpapi_validate_certs: false
        ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
        ansible_host: zabbix-example-fqdn.org
    zabbix_get_graph_protos:
        host_id: 12345
        search:
            name: "Disk space usage {{ '{\#FSNAME}' }}"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils

class GraphProtos(ZabbixBase):
    def get_graph_protos_by_host_id(self, host_id, search, searchByAny):
        """ get graph prototypes by host id """
        graph_list = self._zapi.graphprototype.get({
            "output": "extend",
            "hostids": host_id,
            "search": search,
            "searchByAny": searchByAny,
        })
        if len(graph_list) <1:
            self._module.fail_json(msg="Graph prototypes not found for hostID %s" % host_id)
        else:
            return graph_list

def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(dict(
        host_id=dict(type="list", required=True),
        search=dict(type="dict", default={}, required=False),
        searchByAny=dict(type="bool", deafault=False, required=False)
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    host_id = module.params["host_id"]
    search = module.params["search"]
    searchByAny = module.params["searchByAny"]

    graphprotos = GraphProtos(module)
    graph_list = graphprotos.get_graph_protos_by_host_id(host_id, search, searchByAny)

    module.exit_json(ok=True, graph_list=graph_list)

    
if __name__ == "__main__":
    main()