# APRebootinator

Every 60 days or so, the access points need to be rebooted. 

This script uses `sshpass` for non-interactive SSH. Make sure that's installed. I have the script installed in `/opt/restartAP/`. Create `/opt/restartAP/pass` containing the password of the user you're SSHing with. Make sure it has `0600` permissions with the user running the script as the owner.

Create `/opt/restartAP/user` containing the username of the SSH user. I don't care what permissions you put on it. You're an adult. Probably `0660` but that's just me.

After the script runs, it sends a Slack notification.

This runs as a `5 4 1 */2 *` cron.
