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
module: zabbix_get_graphs
short_description: Get graph info
description:
    - This module allows you to search for the graph info of specific graphs on a specific host
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

- name: Get CPU jumps graph
    # set task level variables as we change ansible_connection plugin here
    vars:
        ansible_network_os: community.zabbix.zabbix
        ansible_connection: httpapi
        ansible_httpapi_port: 443
        ansible_httpapi_use_ssl: true
        ansible_httpapi_validate_certs: false
        ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
        ansible_host: zabbix-example-fqdn.org
    zabbix_get_graphs:
        host_id: 12345
        search:
            name: "CPU jumps"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils

class Graphs(ZabbixBase):
    def get_graphs_by_host_id(self, host_id, search, searchByAny):
        """ get graphs by host id """
        graph_list = self._zapi.graph.get({
            "output": "extend",
            "hostids": host_id,
            "search": search,
            "searchByAny": searchByAny,
            "sortfield": "graphid"
        })
        if len(graph_list) <1:
            self._module.fail_json(msg="Graphs not found for hostID %s using search %s" % (host_id , search))
        else:
            return graph_list

def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(dict(
        host_id=dict(type="list", required=True),
        search=dict(type="dict", default={}, required=False),
        searchByAny=dict(type="bool", default=False, required=False)
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    host_id = module.params["host_id"]
    search = module.params["search"]
    searchByAny = module.params["searchByAny"]

    graphs = Graphs(module)
    graph_list = graphs.get_graphs_by_host_id(host_id, search, searchByAny)

    module.exit_json(ok=True, graph_list=graph_list)

    
if __name__ == "__main__":
    main()