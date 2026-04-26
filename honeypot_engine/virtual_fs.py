"""
Virtual File System for SSH Honeypot
Provides fake Linux directory structure and file contents
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class VirtualFile:
    """Represents a virtual file"""
    
    def __init__(self, name: str, content: str, permissions: str = "644", owner: str = "root", group: str = "root"):
        """Initialize virtual file"""
        self.name = name
        self.content = content
        self.permissions = permissions
        self.owner = owner
        self.group = group
        self.size = len(content)
        self.created_at = datetime.utcnow()
    
    def get_ls_output(self, full_path: str) -> str:
        """Get ls -la format output"""
        timestamp = self.created_at.strftime("%b %d %H:%M")
        return f"-rw-r--r-- 1 {self.owner:8s} {self.group:8s} {self.size:8d} {timestamp} {full_path}"


class VirtualDirectory:
    """Represents a virtual directory"""
    
    def __init__(self, name: str, permissions: str = "755", owner: str = "root", group: str = "root"):
        """Initialize virtual directory"""
        self.name = name
        self.permissions = permissions
        self.owner = owner
        self.group = group
        self.files: Dict[str, VirtualFile] = {}
        self.subdirs: Dict[str, 'VirtualDirectory'] = {}
        self.created_at = datetime.utcnow()
    
    def get_ls_output(self, full_path: str) -> str:
        """Get ls -la format output for directory"""
        timestamp = self.created_at.strftime("%b %d %H:%M")
        return f"drwxr-xr-x 1 {self.owner:8s} {self.group:8s} {4096:8d} {timestamp} {full_path}"
    
    def add_file(self, name: str, file: VirtualFile):
        """Add file to directory"""
        self.files[name] = file
    
    def add_directory(self, name: str, directory: 'VirtualDirectory'):
        """Add subdirectory"""
        self.subdirs[name] = directory


class VirtualFileSystem:
    """Virtual file system for SSH honeypot"""
    
    def __init__(self):
        """Initialize virtual filesystem"""
        self.root = VirtualDirectory("/", owner="root")
        self.current_dir = "/"
        self.initialize_fake_fs()
    
    def initialize_fake_fs(self):
        """Initialize default fake directory structure"""
        
        # Create directory structure
        etc_dir = VirtualDirectory("etc")
        home_dir = VirtualDirectory("home")
        var_dir = VirtualDirectory("var")
        tmp_dir = VirtualDirectory("tmp", permissions="777")
        root_home_dir = VirtualDirectory("root")
        log_dir = VirtualDirectory("log")
        user_home_dir = VirtualDirectory("user")
        
        # Add files
        etc_dir.add_file("passwd", VirtualFile("passwd", """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing list manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
admin:x:1000:1000:admin:/home/admin:/bin/bash
user:x:1001:1001:user:/home/user:/bin/bash"""))
        
        etc_dir.add_file("hostname", VirtualFile("hostname", "honeypot-server\n"))
        etc_dir.add_file("hosts", VirtualFile("hosts", """127.0.0.1	localhost
::1		localhost
127.0.1.1	honeypot-server"""))
        
        etc_dir.add_file("shadow", VirtualFile("shadow", """root:!:18000:0:99999:7:::
daemon:*:18000:0:99999:7:::
bin:*:18000:0:99999:7:::
sys:*:18000:0:99999:7:::
sync:*:18000:0:99999:7:::
games:*:18000:0:99999:7:::
man:*:18000:0:99999:7:::
lp:*:18000:0:99999:7:::
mail:*:18000:0:99999:7:::
news:*:18000:0:99999:7:::
uucp:*:18000:0:99999:7:::""", permissions="600"))
        
        log_dir.add_file("auth.log", VirtualFile("auth.log", "Nov 15 12:34:56 honeypot sshd[1234]: Received disconnect from attacker\n"))
        log_dir.add_file("syslog", VirtualFile("syslog", "Nov 15 12:34:56 honeypot kernel: [1234.567890] CPU: Physical Processor ID: 0\n"))
        
        root_home_dir.add_file(".bash_history", VirtualFile(".bash_history", """ls -la
cd /home
cat /etc/passwd
whoami
id
uname -a
""", permissions="600"))
        
        root_home_dir.add_file(".bashrc", VirtualFile(".bashrc", """# ~/.bashrc
export LS_Colors='di=34:fi=0:ln=35:ex=32'
alias ll='ls -l'
alias la='ls -la'
""", permissions="644", owner="root"))
        
        user_home_dir.add_file(".bash_history", VirtualFile(".bash_history", """pwd
ls
whoami
""", permissions="600"))
        
        user_home_dir.add_file("README.txt", VirtualFile("README.txt", "This is a fake user home directory.\n"))
        
        # Build directory structure
        self.root.add_directory("etc", etc_dir)
        self.root.add_directory("home", home_dir)
        self.root.add_directory("var", var_dir)
        self.root.add_directory("tmp", tmp_dir)
        self.root.add_directory("root", root_home_dir)
        
        var_dir.add_directory("log", log_dir)
        home_dir.add_directory("user", user_home_dir)
    
    def get_current_directory(self) -> VirtualDirectory:
        """Get current directory object"""
        path_parts = [p for p in self.current_dir.split("/") if p]
        
        current = self.root
        for part in path_parts:
            if part in current.subdirs:
                current = current.subdirs[part]
            else:
                return None
        return current
    
    def list_directory(self, path: str = None) -> List[str]:
        """List directory contents (ls command)"""
        if path is None:
            path = self.current_dir
        
        # Resolve absolute vs relative path
        if path.startswith("/"):
            dir_obj = self._resolve_absolute_path(path)
        else:
            dir_obj = self._resolve_relative_path(path)
        
        if not dir_obj:
            return ["ls: cannot access '{}': No such file or directory".format(path)]
        
        output = []
        # Add . and ..
        output.append(dir_obj.get_ls_output("."))
        output.append(self.get_parent_directory().get_ls_output(".."))
        
        # Add files
        for filename, file_obj in dir_obj.files.items():
            full_path = self.current_dir.rstrip("/") + "/" + filename
            output.append(file_obj.get_ls_output(full_path))
        
        # Add directories
        for dirname, subdir in dir_obj.subdirs.items():
            full_path = self.current_dir.rstrip("/") + "/" + dirname
            output.append(subdir.get_ls_output(full_path))
        
        return output
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file contents (cat command)"""
        if path.startswith("/"):
            file_obj = self._resolve_absolute_file_path(path)
        else:
            file_obj = self._resolve_relative_file_path(path)
        
        if not file_obj:
            return f"cat: {path}: No such file or directory"
        
        return file_obj.content
    
    def change_directory(self, path: str) -> bool:
        """Change current directory (cd command)"""
        if path == "/":
            self.current_dir = "/"
            return True
        elif path == "..":
            parent = self.get_parent_directory()
            if parent:
                self.current_dir = self._get_parent_path(self.current_dir)
                return True
        else:
            if path.startswith("/"):
                target_dir = self._resolve_absolute_path(path)
            else:
                target_dir = self._resolve_relative_path(path)
            
            if target_dir:
                self.current_dir = path if path.startswith("/") else self.current_dir.rstrip("/") + "/" + path
                return True
        
        return False
    
    def _resolve_absolute_path(self, path: str) -> Optional[VirtualDirectory]:
        """Resolve absolute path to directory"""
        path_parts = [p for p in path.split("/") if p]
        
        current = self.root
        for part in path_parts:
            if part in current.subdirs:
                current = current.subdirs[part]
            else:
                return None
        return current
    
    def _resolve_absolute_file_path(self, path: str) -> Optional[VirtualFile]:
        """Resolve absolute path to file"""
        path_parts = [p for p in path.split("/") if p]
        filename = path_parts[-1] if path_parts else None
        
        if not filename:
            return None
        
        dir_path = path_parts[:-1]
        current = self.root
        
        for part in dir_path:
            if part in current.subdirs:
                current = current.subdirs[part]
            else:
                return None
        
        return current.files.get(filename)
    
    def _resolve_relative_path(self, path: str) -> Optional[VirtualDirectory]:
        """Resolve relative path to directory"""
        parent_path = self.current_dir.rstrip("/")
        if parent_path == "":
            parent_path = "/"
        
        full_path = parent_path + "/" + path if parent_path != "/" else "/" + path
        return self._resolve_absolute_path(full_path)
    
    def _resolve_relative_file_path(self, path: str) -> Optional[VirtualFile]:
        """Resolve relative path to file"""
        parent_path = self.current_dir.rstrip("/")
        if parent_path == "":
            parent_path = "/"
        
        full_path = parent_path + "/" + path if parent_path != "/" else "/" + path
        return self._resolve_absolute_file_path(full_path)
    
    def get_parent_directory(self) -> VirtualDirectory:
        """Get parent directory"""
        parent_path = self._get_parent_path(self.current_dir)
        return self._resolve_absolute_path(parent_path) or self.root
    
    def _get_parent_path(self, path: str) -> str:
        """Get parent path"""
        path = path.rstrip("/")
        if path == "":
            return "/"
        parent = "/".join(path.split("/")[:-1])
        return parent if parent else "/"
    
    def get_pwd(self) -> str:
        """Print working directory"""
        return self.current_dir if self.current_dir and self.current_dir != "" else "/"
