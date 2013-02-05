#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This program is distributed under the terms of the GNU General Public License
#   For more info see http://www.gnu.org/licenses/gpl.txt

# Based on the pysshfs utility: https://github.com/dprevite/pysshfs/blob/master/pysshfs



import subprocess
import os
import ssh
import sys
import pexpect
import gtk
import pygtk
pygtk.require('2.0')

import gnomeapplet
import glib

from os.path import expanduser

SSHFS_OPTIONS = 'idmap=user,ServerAliveInterval=10,ServerAliveCountMax=5,IdentityFile=~/.MassiveCvlKeyPair'

def run_ssh_command(ssh_client, command):
    """
    Run a shell command using the supplied ssh client. Returns stdout
    and stderr.
    """

    stdin, stdout, stderr = ssh_client.exec_command(command)
    stdout, stderr = stdout.read(), stderr.read()

    if stdout is None: stdout = ''
    if stderr is None: stderr = ''

    print command, stdout, stderr

    return stdout, stderr

def run_shell_command(command):
    """
    Run a shell command. Returns stdout and stderr.
    """

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
    stdin=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
    universal_newlines=True) stdout, stderr = proc.communicate()

    if stdout is None: stdout = ''
    if stderr is None: stderr = ''

    print command, stdout, stderr
    return stdout, stderr

def current_mountpoints():
    """
    Parse the output of 'mount' to determine the user's sshfs
    mountpoints. Alternative: parse /etc/mtab.
    """

    home = expanduser('~')
    stdout = run_shell_command('mount')[0].split('\n')
    return [x.split()[2] for x in stdout if home in x and 'fuse.sshfs' in x]

def create_keypair():
    """
    Creates the keypair ~/.MassiveCvlKeyPair{,.pub}. If the keypair exists,
    it will be destroyed.
    """

    stdout, stderr = run_shell_command('/bin/rm -f ~/.MassiveCvlKeyPair*')
    if stderr != '': return stdout, stderr, 'removing MassiveCvlKeyPair'

    stdout, stderr = run_shell_command('/usr/bin/ssh-keygen -C "MASSIVE CVL" -N "" -t rsa -f ~/.MassiveCvlKeyPair')
    if stderr != '': return stdout, stderr, 'ssh-keygen'

    stdout, stderr = run_shell_command('/bin/chmod 600 ~/.MassiveCvlKeyPair*')
    if stderr != '': return stdout, stderr, 'chmod 600'


def install_keypair_on_massive(host, username, password):
    """
    Copy the public key ~/.MassiveCvlKeyPair.pub to ~/.ssh/authorized_keys on the remote host.
    """

    try:
        ssh_client = ssh.SSHClient()
        ssh_client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password, look_for_keys=False)
        sftp_client = ssh_client.open_sftp()
    except IOError, e:
        show_msg('IO Error while connecting to ' + host + ': ' + str(e))
        return
    except ssh.AuthenticationException, e:
        show_msg('Authentication error while connecting to ' + host + ': ' + str(e))
        return

    stdout, stderr = run_ssh_command(ssh_client, '/bin/mkdir ~/.ssh')
    if stderr != '' and 'File exists' not in stderr: return stdout, stderr

    stdout, stderr = run_ssh_command(ssh_client, '/bin/chmod 700 ~/.ssh')
    if stderr != '': return stdout, stderr

    stdout, stderr = run_ssh_command(ssh_client, '/bin/touch ~/.ssh/authorized_keys')
    if stderr != '': return stdout, stderr

    stdout, stderr = run_ssh_command(ssh_client, '/bin/sed -i -e "/MASSIVE CVL/d" ~/.ssh/authorized_keys')
    if stderr != '': return stdout, stderr

    try:
        source_file = expanduser('~') + '/.MassiveCvlKeyPair.pub'
        target_file = '/home/' + username + '/.MassiveCvlKeyPair.pub'
        sftp_client.put(source_file, target_file, confirm=True)
    except IOError, e:
        return '', str(e), 'scp %s to %s' % (source_file, target_file,)

    stdout, stderr = run_ssh_command(ssh_client, '/bin/cat ~/.MassiveCvlKeyPair.pub >> ~/.ssh/authorized_keys')
    if stderr != '': return stdout, stderr

    stdout, stderr = run_ssh_command(ssh_client, "/bin/rm -f ~/.MassiveCvlKeyPair.pub")
    if stderr != '': return stdout, stderr


    stdout, stderr = run_ssh_command(ssh_client, "/bin/chmod 600 ~/.ssh/authorized_keys")
    if stderr != '': return stdout, stderr

def test_ssh_keypair(host, username):
    """
    Test if the user can connect to Massive using just their keypair (no password).
    """

    ssh_client = ssh.SSHClient()
    ssh_client.set_missing_host_key_policy(ssh.AutoAddPolicy())

    try:
        ssh_client.connect(host, username=username, look_for_keys=False, key_filename=expanduser('~') + '/.MassiveCvlKeyPair')
        return True, None
    except IOError, e:
        print False, e
    except ssh.AuthenticationException, e:
        print False, e

    return False, 'unknown error in test_ssh_keypair()'


def write_massive_config(hostname, username, project):
    f = open(expanduser('~') + '/.Massive_Preferences', 'w')

    f.write(hostname + '\n')
    f.write(username + '\n')
    f.write(project  + '\n')

    f.close()

def read_massive_config():
    f = open(expanduser('~') + '/.Massive_Preferences', 'r')

    lines = f.read().rstrip().split('\n')

    if len(lines) == 3:
        return lines[0], lines[1], lines[2] # hostname, username, project
    else:
        return None

def callback():
    """
    Example of a callback; see the commented line in factory()
    that runs this every second.
    """

    print 'called'
    return True

def applet_clicked(widget, event, applet):
    if event.button == 1:
        ui = UI()
        ui.run()
        widget.emit_stop_by_name("button_press_event")

def xpm_box(parent, xpm_filename):
    """
    Load an XPM into a box. Use this to create a button
    with a pixmap.
    """

    box = gtk.HBox(False, 0)
    box.set_border_width(2)

    image = gtk.Image()
    image.set_from_file(xpm_filename)

    box.pack_start(image, False, False, 3)

    image.show()
    return box

def factory(applet, iid):
    icon_filename = '/home/carlo/MASSIVElogoTransparent32x32.xpm'

    button = gtk.Button()
    button.set_relief(gtk.RELIEF_NONE)
    # button.set_label("Massive :)")

    # This calls our box creating function
    box = xpm_box(applet, icon_filename)

    # Pack and show all our widgets
    button.add(box)

    button.connect("button_press_event", applet_clicked, applet)
    applet.add(button)
    applet.show_all()

    # To call callback() every second:
    # glib.timeout_add_seconds(1, callback)

    # If the user already has a functioning ssh keypair, mount their project
    # directory immediately.
    try:
        host, username, project = read_massive_config()
        if test_ssh_keypair(host, username):
            dir, mountpoint = '/home/projects/' + project, os.getenv('HOME') + '/' + project

            if not os.path.exists(mountpoint): os.mkdir(mountpoint)
            ret = sshFs().mount(user=username, host=host, dir=dir, mountpoint=mountpoint)
    except:
        pass

    return True

class UI:
    def __init__(self):
        # Create window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Massive Preferences")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect("destroy", self.quit)

        try:
            a_host, a_user, a_project = read_massive_config()
        except:
            a_host, a_user, a_project = '', '', ''

        # Containers
        BoxBase = gtk.VBox()
        #~ BoxBase.set_spacing(5)
        BoxBase.set_border_width(5)

        BoxMain = gtk.HBox()
        BoxMain.set_spacing(5)
        BoxMain.set_border_width(5)

        BoxControls = gtk.HButtonBox()
        #~ BoxControls.set_spacing(2)
        BoxControls.set_layout(gtk.BUTTONBOX_END)

        button_mount = gtk.Button('Mount all')
        button_mount.connect("clicked", self.mount_all)
        BoxControls.pack_end(button_mount, False, False)

        button_unmount = gtk.Button('Unmount all')
        button_unmount.connect("clicked", self.unmount_all)
        BoxControls.pack_end(button_unmount, False, False)


        # Exit
        button_exit = gtk.Button(stock=gtk.STOCK_CLOSE)
        button_exit.connect("clicked", self.quit)
        BoxControls.pack_end(button_exit, False, False)

        table = gtk.Table()
        table.set_row_spacings(5)
        table.set_col_spacings(5)

        ## User
        self.User_entry = gtk.Entry()
        self.User_entry.set_text(a_user)
        label = gtk.Label('User :')
        label.set_alignment(0, 1)
        table.attach(label, 0, 1, 1, 2)
        table.attach(self.User_entry, 1, 2, 1, 2)

        ## Password
        self.Password_entry = gtk.Entry()
        self.Password_entry.set_visibility(False)
        label = gtk.Label('Password :')
        label.set_alignment(0, 1)
        table.attach(label, 0, 1, 2, 3)
        table.attach(self.Password_entry, 1, 2, 2, 3)

        ## Host
        self.Host_entry = gtk.Entry()
        label = gtk.Label('Host :')
        self.Host_entry.set_text(a_host)
        label.set_alignment(0, 1)
        table.attach(label, 0, 1, 3, 4)
        table.attach(self.Host_entry, 1, 2, 3, 4)

        ## Project
        self.Project_entry = gtk.Entry()
        label = gtk.Label('Project :')
        self.Project_entry.set_text(a_project)
        label.set_alignment(0, 1)
        table.attach(label, 0, 1, 4, 5)
        table.attach(self.Project_entry, 1, 2, 4, 5)

        ## Connect
        self.Connect_Bt = gtk.Button('Apply')
        self.Connect_Bt.connect("clicked", self.mount_sshfs)
        table.attach(self.Connect_Bt, 1, 2, 7, 8)

        ## Separator
        table.attach(gtk.HSeparator(), 0, 2, 8, 9)

        BoxMain.add(table)
        BoxBase.pack_start(BoxMain, True)
        BoxBase.pack_end(BoxControls, False)

        self.window.add(BoxBase)

        self.User_entry.connect("changed", self.auto_mountpoint)
        self.Host_entry.connect("changed", self.auto_mountpoint)

        self.update_mountedfs()

        #Show main window frame and all content
        self.window.show_all()

    def auto_mountpoint(self, widget):
        return
        User = self.User_entry.get_text()
        Host = self.Host_entry.get_text()
        self.Mountpoint_entry.set_text('%s@%s' % (User, Host))

    def open_mountpoint(self, widget):
        mount_point = self.Mounted_fs_combo.get_active()
        if mount_point == 0 or mount_point == -1:
            return
        else:
            os.system('xdg-open %s' % self.Mounted_fs_combo.get_active_text())

    def umount_sshfs(self, widget):
        mount_point = self.Mounted_fs_combo.get_active()
        if mount_point == 0 or mount_point == -1:
            return
        else:
            os.system('fusermount -u %s' % self.Mounted_fs_combo.get_active_text())
            os.system('rmdir %s' % self.Mounted_fs_combo.get_active_text())
            self.update_mountedfs()

    def update_mountedfs(self):
        return

        self.mounted_fs_tab = get_mounted_fs()
        self.Mounted_fs_combo.get_model().clear()
        self.Mounted_fs_combo.insert_text(0, 'Choose')

        ind = 1
        for mounted_fs in self.mounted_fs_tab:
            self.Mounted_fs_combo.insert_text(ind, mounted_fs[1])
            ind += 1
        self.Mounted_fs_combo.set_active(0)

    def mount_sshfs(self, widget=None):
        username        = self.User_entry.get_text()
        password        = self.Password_entry.get_text()
        host            = self.Host_entry.get_text()
        project         = self.Project_entry.get_text()

        result = create_keypair()
        if result is not None:
            show_msg('Error creating keypair: ' + str(result))
            return

        result = install_keypair_on_massive(host, username, password)
        if result is not None:
            show_msg('Error installing keypair: ' + str(result))
            return

        result, info = test_ssh_keypair(host, username)
        if not result:
            show_msg('Keypair error: ' + str(info))
            return

        self.nmount_all()

        dir, mountpoint = '/home/projects/' + project, os.getenv('HOME') + '/' + project

        if not os.path.exists(mountpoint): os.mkdir(mountpoint)
        ret = sshFs().mount(user=username, host=host, dir=dir, mountpoint=mountpoint)
        print dir, mountpoint, ret # FIXME check ret?

        write_massive_config(host, username, project)

    def run(self):
        gtk.main()

    def quit(self, widget=None, data=None):
        self.window.destroy()

    def unmount_all(self, widget=None, data=None):
        for x in current_mountpoints():
            run_shell_command('fusermount -u %s' % x)
            run_shell_command('rmdir         %s' % x)

    def mount_all(self, widget=None, data=None):
        username        = self.User_entry.get_text()
        host            = self.Host_entry.get_text()
        project         = self.Project_entry.get_text()

        if test_ssh_keypair(host, username):
            dir, mountpoint = '/home/projects/' + project, os.getenv('HOME') + '/' + project

            if not os.path.exists(mountpoint): os.mkdir(mountpoint)
            ret = sshFs().mount(user=username, host=host, dir=dir, mountpoint=mountpoint)

## Initialize the module.
class sshFs:
    def __init__(self):
        ## Three responses we might expect.
        self.initial_responses = ['Are you sure you want to continue connecting (yes/no)?',
                                  'password:', pexpect.EOF]

    def mount(self, user="", password="", host="", dir="", mountpoint="", port=22, timeout=120):

        command = "sshfs -p %s %s@%s:%s %s -o %s" % (port, user, host, dir, mountpoint, SSHFS_OPTIONS)
        debug_info("Command : %s" % command)

        print command

        child = pexpect.spawn(command)

        ## Get the first response.
        ret = child.expect (self.initial_responses, timeout)
        ## The first reponse is to accept the key.
        if ret==0:
            debug_info("The first reponse is to accept the key.")
            #~ T = child.read(100)
            child.sendline("yes")
            child.expect('password:', timeout)
            child.sendline(password)
        ## The second response sends the password.
        elif ret == 1:
            debug_info("The second response sends the password.")
            child.sendline(password)
        # check for ssh bound mount - child exited and exitstatus=0
        elif child.isalive() == False:
            if child.exitstatus == 0:
                return (0, "ssh-bound host mounted")
            else:
                #this is wierd.. quit
                return (-3, 'ERROR: Unknown')
        ## Otherwise, there is an error.
        else:
            debug_info("Otherwise, there is an error.")
            return (-3, 'ERROR: Unknown: ' + str(child.before))

        ## Get the next response.
        possible_responses = ['password:', pexpect.EOF]
        ret = child.expect (possible_responses, timeout)

        ## If it asks for a password, error.
        if ret == 0:
            debug_info("If it asks for a password, error.")
            return (-4, 'ERROR: Incorrect password.')
        elif ret == 1:
            debug_info("Otherwise we are okay.")
            return (0, str(child.after))
            ## Otherwise we are okay.
        else:
            debug_info("Otherwise, there is an error.")
            return (-3, 'ERROR: Unknown: ' + str(child.before))

def show_msg(msg=' .. '):
    """  """
    message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
    resp = message.run()
    message.destroy()

def debug_info(msg):
    if DEBUG:
        print "# %s" % msg

if __name__ == '__main__':
    if sys.argv[1:] == ['--testing']:
        mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        mainWindow.set_title("Ubuntu System Panel")
        mainWindow.connect("destroy", gtk.main_quit)
        applet = gnomeapplet.Applet()
        factory(applet, None)
        applet.reparent(mainWindow)
        mainWindow.show_all()
        gtk.main()
        sys.exit()
    else:
        print "Starting factory"
        gnomeapplet.bonobo_factory("OAFIID:Gnome_Panel_Example_Factory", gnomeapplet.Applet.__gtype__, "Simple gnome applet example", "1.0", factory)


