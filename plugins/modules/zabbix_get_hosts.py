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
module: zabbix_get_hosts
short_description: Get host(s) info
description:
    - This module allows you to search for hosts based on a filter expression
author:
    - "Ben Albon (ben@dataraven.co.uk)"
requirements:
    - "python >= 3.9"
options:
    filter:
        description:
            - search paramaters
        required: false
        type: dict
        default: {}
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

- name: Get CPU item info
    # set task level variables as we change ansible_connection plugin here
    vars:
        ansible_network_os: community.zabbix.zabbix
        ansible_connection: httpapi
        ansible_httpapi_port: 443
        ansible_httpapi_use_ssl: true
        ansible_httpapi_validate_certs: false
        ansible_zabbix_url_path: "zabbixeu"  # If Zabbix WebUI runs on non-default (zabbix) path ,e.g. http://<FQDN>/zabbixeu
        ansible_host: zabbix-example-fqdn.org
    zabbix_get_hosts:
        filter:
            host: "Zabbix server"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.zabbix.plugins.module_utils.base import ZabbixBase
import ansible_collections.community.zabbix.plugins.module_utils.helpers as zabbix_utils

class Hosts(ZabbixBase):
    def get_hosts(self, filter, groupid, templateid):
        """ get host info """
        hosts_list = self._zapi.host.get({
            "filter": filter,
            "groupids": groupid,
            "templateids": templateid
        })
        if len(hosts_list) <1:
            self._module.fail_json(msg="Hosts not found using filter %s" % filter)
        else:
            return hosts_list

    def get_groupid(self, group_name):
        """ get template id from template name """
        group_info = self._zapi.hostgroup.get({
            "filter": {"name": group_name}
        })
        if len(group_info) <1:
            self._module.fail_json(msg="Host group: %s not found" % group_name)
        else:
            return group_info[0]["groupid"]

    def get_templateid(self, template_name):
        """ get template id from template name """
        template_info = self._zapi.template.get({
            "filter": {"host": template_name}
        })
        if len(template_info) <1:
            self._module.fail_json(msg="Template: %s not found" % template_name)
        else:
            return template_info[0]["templateid"]

def main():
    argument_spec = zabbix_utils.zabbix_common_argument_spec()
    argument_spec.update(dict(
        filter=dict(type="dict", default={}, required=False),
        group_name=dict(type="str", default="", required=False),
        template_name=dict(type="str", default="", required=False)
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    filter = module.params["filter"]
    group_name = module.params["group_name"]
    template_name = module.params["template_name"]

    hosts = Hosts(module)
    if group_name != "":
        groupid = hosts.get_groupid(group_name)
    else:
        groupid = ""
    if template_name != "":
        templateid = hosts.get_templateid(template_name)
    else:
        templateid = ""
    hosts_list = hosts.get_hosts(filter, groupid, templateid)

    module.exit_json(ok=True, host_list=hosts_list)

    
if __name__ == "__main__":
    main()