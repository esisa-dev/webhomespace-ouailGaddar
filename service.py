import subprocess
from model import User,Directory,File
import crypt
import re
import os
import datetime
import pwd
import zipfile

class UserService:
    def __init__(self)->None:
        pass
    def authentification(self,name:str,password:str) -> bool:
        print('B')
        self.name=name
        self.password=password
        try:
            with open('/etc/shadow') as f:
                for line in f:
                    fields = line.strip().split(':')
                    if fields[0] == self.name:
                        hashed_pwd = fields[1]
                        break
            
            hash_algo, salt, hashed = hashed_pwd.split('$')[1:4]
            hashed_pwd_input = crypt.crypt(self.password, f"${hash_algo}${salt}${hashed}$")
            if hashed_pwd_input == hashed_pwd:
                print('********avant')
                current_user = os.getlogin()
                print(f"User info:\n{current_user}")
                cmd = ['su', self.name, '-c', 'whoami']
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = p.communicate(input=self.password.encode())
                if p.returncode == 0 and output.decode().strip() == self.name:
                    print('********apres')
                    print(f"User switched to: {output.decode().strip()}")
                    cmd_id = ['id', self.name]
                    p_id = subprocess.Popen(cmd_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output_id, error_id = p_id.communicate()
                    print(f"User info:\n{output_id.decode().strip()}")
                else:
                    print('False')

                return True
            else:
                return False
        except KeyError:
            
            return False
    
    def list_user_files_and_directories(self,path:str):
        
        cmd_id = ['id', self.name]
        p_id = subprocess.Popen(cmd_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output_id, error_id = p_id.communicate()
        print(f"User info:\n{output_id.decode().strip()}")
        home_dir = path
        cmd = f"find {home_dir} -mindepth 1 -maxdepth 1"
        output = subprocess.check_output(cmd, shell=True)
        files_and_directories = output.decode("utf-8").strip().split("\n")
        file_info = []
        for item in files_and_directories:
            item_name = os.path.basename(item)
            item_date = datetime.datetime.fromtimestamp(os.path.getmtime(item))
            #----------------------------
            now = datetime.datetime.now()
            yesterday = now - datetime.timedelta(days=1)
            two_days_ago = now - datetime.timedelta(days=2)
            if item_date.date() == now.date():
                formatted_date = item_date.strftime('%H:%M')
            elif item_date.date() == yesterday.date():
                formatted_date = "hier à " + item_date.strftime('%H:%M')
            elif item_date.date() == two_days_ago.date():
                formatted_date = "avant-hier à " + item_date.strftime('%H:%M')
            else:
                formatted_date = item_date.strftime('%-d %b. %Y à %H:%M')
            #----------------------------
            item_date_str = formatted_date
            item_size = os.path.getsize(item)
            #------------------------------------------
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            i = 0
            while item_size>= 1024 and i < len(units)-1:
                item_size /= 1024
                i += 1
    
            size = f"{item_size:.2f} {units[i]}"
            #------------------------------------------
            item_path = "-".join(home_dir.split("/")).lstrip("-")

            if os.path.isfile(item):
                item_info = File(item_name, item_date_str ,size, item_path)
            else:
                item_info = Directory(item_name, item_date_str , size, item_path)
            file_info.append(item_info)
        return file_info
    def getPath(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return current_dir

    def isDirectroyOrfile(self,chemin:str)->str:
            if os.path.isfile(chemin):
                return "file"
            elif os.path.isdir(chemin):
                return "directory"
            else:
                return "unknown"
    def toChemine(self,info_str):
   
        match = re.search(r'\((.*?)\)', info_str)
        if match:
            directory_str = match.group(1)
            
            directory_str = directory_str.replace('-', '/').strip()
            
            directory_str = '/' + directory_str

            return directory_str
        else:
            return None
    def read_file(self,chemin: str) -> str:
        with open(chemin, 'r') as file:
            contenu = file.read()
        return contenu
    def count_files(self,username):
        cmd = f"find /home/{username} -type f -user {username} | wc -l"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            print(f"Error: {result.stderr.strip()}")
            return -1
    def count_directories_for_user(self,username):
        user_dir = f"/home/{username}"  
        result = subprocess.run(['find', user_dir, '-mindepth', '1', '-type', 'd', '-print'], capture_output=True, text=True)
        num_directories = len(result.stdout.splitlines())          
        return num_directories
    def calculate_space_for_user(self,username):
        
        user_dir = f"/home/{username}"  
        total_size = 0
        
        for root, dirs, files in os.walk(user_dir):
            for directory in dirs:
                directory_path = os.path.join(root, directory)
                if os.path.islink(directory_path):  
                    continue
                try:
                    size = os.path.getsize(directory_path)
                    total_size += size
                except OSError:
                    continue
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.islink(file_path):  
                    continue
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                except OSError:
                    continue
            
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while total_size >= 1024 and i < len(units)-1:
            total_size /= 1024
            i += 1
    
        return f"{total_size:.2f} {units[i]}"
    
    def find_files(self,username, filename=None, extension=None):
        user_dir = f"/home/{username}"
        args = ['find', user_dir, '-type', 'f']
        if filename:
            #print("A")
            args += ['-name', f'*{filename}*']
        if extension:
            #print("B")
            args += ['-name', f'*.{extension}']
        result = subprocess.run(args, capture_output=True, text=True)
        #print(result)
        file_paths = result.stdout.strip().split('\n')
        files = []
        for file_path in file_paths:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size  
            file_date = datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            file_name = os.path.basename(file_path)
            files.append(File(file_name, file_date, file_size, file_path))
        return files
    def download_directory(self, username):
           
        zip_name = username + '_home.zip'
        zip_file = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

        home_dir = '/home/' + username

        cmd = ['find', home_dir, '-path', '*/\.*', '-prune', '-o', '-print']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        for item in stdout.decode().splitlines():
            
            zip_file.write(item, item.replace(home_dir, ''))
        zip_file.close()
        return zip_name
    

if __name__=='__main__':
    service=UserService()
    if service.authentification('ahmed','111') :
        print(service.count_files('ahmed'))
    
    
  
   

    