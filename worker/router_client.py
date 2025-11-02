from netmiko import ConnectHandler
import json
# from jinja2 import Environment, FileSystemLoader

def get_interfaces(ip, username, password):
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": username,
        "password": password,
    }

    with ConnectHandler(**device) as conn:
        conn.enable()
        result = conn.send_command("show ip int br")
        conn.disconnect()

    print(json.dumps(result, indent=2))

# def generate_interface_config(router_data):
#     env = Environment(loader=FileSystemLoader("templates"))
#     template = env.get_template("config_interface.j2")
#     return template.render(interfaces=router_data["interfaces"])

# def set_config(ip, username, password):
#     device = {
#         "device_type": "cisco_ios",
#         "host": ip,
#         "username": username,
#         "password": password,
#     }

#     config = generate_interface_config(router_data)
#     commands = config.splitlines()

#     with ConnectHandler(**device) as conn:
#         conn.enable()
#         output = conn.send_config_set(commands)
#         conn.save_config()
#     return output