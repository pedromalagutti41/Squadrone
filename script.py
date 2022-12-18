from http.server import HTTPServer, BaseHTTPRequestHandler
import traceback

LAST_RPM = '0000'
DBG = True

def read_forms(body, word) :
    """Reads a attribute from a forms structured data"""
    bd = body.decode('utf-8')
    index = bd.find(word) + len(word) + 1
    speedStr = bd[index:]
    print('(' + speedStr + ')')

    if not speedStr.isnumeric() :
        raise Exception("ERROR: BAD FORMAT")
    else :
        speedStr = int(speedStr)

    return str(speedStr)

def write_duty_cycle(dutyCycle) :    
    """Writes a value to Duty Cycle PWM control file"""
    if DBG : dir = './duty_cycle'
    else : dir = "/sys/class/pwm/pwmchip8/pwm0/duty_cycle"

    with open(dir, 'w') as file:
        duty_cycle = file.writelines([dutyCycle])

    return

def update_index(file, target, info) :
    # Atualiza pagina
    info = ' ' + info
    aux = file.split(target)
    aux.insert(1, target)
    aux.insert(2, info)
    return ''.join(aux)

def post_response(data, index) :
    global LAST_RPM
    speed_input = read_forms(data, 'speed') 
    write_duty_cycle(speed_input)

    # Updates the index base file         
    new_index = update_index(index, 'Actual Speed:', speed_input)
    
    LAST_RPM = speed_input
    return new_index

class Server(BaseHTTPRequestHandler):
    """Extends BaseHTTPRequestHandler class to create our own web server"""

    def do_GET(self):
        """GET HTML Method to load index.html file as default"""
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        try:
            index = open(self.path[1:]).read()
            self.send_response(200)
        except:
            index = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(index, 'utf-8'))

    def do_POST(self):
        """POST HTML Method read and overwrite Duty Cycle PWM control file"""

        # Reads index.html file
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        # Successful load
        try:
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            index = open(self.path[1:]).read()
            self.send_response(200)
        # Error 404, file not found
        except:
            index = "File not found"
            self.send_response(404)
        self.end_headers()
        
        # Executes post routine
        try :
            index = post_response(data, index)
        # If error in method, keep last valid speed
        except Exception as e :
            print(e)
            index = update_index(index, 'Actual Speed:', LAST_RPM)

        self.wfile.write(bytes(index, 'utf-8'))

def main() :

    global DBG

    export = "0"
    period = "2000"
    duty_cycle = "0000"
    enable = "1"

    if not DBG :
        with open("/sys/class/pwm/pwmchip8/export", "w") as file1:
            file1.writelines([export])
            
        with open("/sys/class/pwm/pwmchip8/pwm0/period", "w") as file2:
            file2.writelines([period])
            
        with open("/sys/class/pwm/pwmchip8/pwm0/duty_cycle", "w") as file3:
            file3.writelines([duty_cycle])
            
        with open("/sys/class/pwm/pwmchip8/pwm0/enable", "w") as file4:
            file4.writelines([enable])

    # Creates the server
    httpd = HTTPServer(('localhost', 8080), Server)
    httpd.serve_forever()

if __name__ == '__main__' :
    main()