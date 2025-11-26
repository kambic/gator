from fabric import Connection

hosts = [
    "encoding01",
    "encoding02",
    "encoding03",
    "encoding04",
    "encoding05",
    "encoding06",
    "encoding07",
    "encoding08",
    "encoding09",
    "encoding10",
]


# Function to get password from a file
def get_password_from_file(file_path='.password'):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()  # Remove any extra spaces or newlines
    except Exception as e:
        print(f"Error reading password file: {e}")
        return None


def set_group(user, group):
    """
    This function adds a user to a group using 'usermod'.
    :param user: The username to add.
    :param group: The group to add the user to.
    """
    # Add the user to the group
    with Connection('your-server.com') as c:
        c.sudo(f'usermod -aG {group} {user}')
        print(f"User {user} has been added to group {group}.")


def check_hostname_with_sudo():
    password = get_password_from_file()
    for host in hosts:
        try:
            with Connection(host) as c:
                res = c.sudo("hostname", password=password)
                # print(res.stdout)
                print(f"✅ Hostname: {host}")
        except Exception as e:
            print(f"❌ Error getting hostname: {host}")

from invoke import Responder

from fabric import Connection

c = Connection('host')

sudopass = Responder(
    pattern=r'\[sudo\] password:',
    response='mypassword\n',

)

c.run('sudo whoami', pty=True, watchers=[sudopass])


if __name__ == "__main__":
    # set_group("root", "root")
    check_hostname_with_sudo()
