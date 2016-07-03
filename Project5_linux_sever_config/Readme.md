Your README.md file should include all of the following:

i. The IP address and SSH port so your server can be accessed by the reviewer.
IP address: 52.41.151.121
SSH port: 2200


ii. The complete URL to your hosted web application.
URL: http://52.41.151.121


iii. A summary of software you installed and configuration changes made.
I installed:
apache, postgresql, git, cgi, flask, pip, google_api_python_client
Configuration changes:
created user grader, added to sudoer list
changed ssh prot from 22 to 2200
configured the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)

iv. A list of any third-party resources you made use of to complete this project.
stackoverflow