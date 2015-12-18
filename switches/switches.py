#import the required modules
import RPi.GPIO as GPIO
import time
import sys
import cherrypy

class Switch:

    exposed = True

    def init(self):
        # set the pins numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Select the GPIO pins used for the encoder K0-K3 data inputs
        GPIO.setup(11, GPIO.OUT)
        GPIO.setup(15, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)

        # Select the signal to select ASK/FSK
        GPIO.setup(18, GPIO.OUT)

        # Select the signal used to enable/disable the modulator
        GPIO.setup(22, GPIO.OUT)

        # Disable the modulator by setting CE pin lo
        GPIO.output (22, False)

        # Set the modulator to ASK for On Off Keying 
        # by setting MODSEL pin lo
        GPIO.output (18, False)

        # Initialise K0-K3 inputs of the encoder to 0000
        GPIO.output (11, False)
        GPIO.output (15, False)
        GPIO.output (16, False)
        GPIO.output (13, False)

    def ctrl_socket(self, socket, on):
        print(socket)
        if socket == 1:
                m = [ True, True, True ]
        elif socket == 2:
                m = [ False, True, True ]
        elif socket == 3:
                m = [ True, False, True ]
        elif socket == 4:
                m = [ False, False, True ]
        elif socket == 0:
                m = [ True, True, False ]
        else:
                raise Exception('Socket must be 0 - 4, where 0 is all sockets, it was ' + socket)

        # Set K0-K3
        GPIO.output (11, m[0])
        GPIO.output (15, m[1])
        GPIO.output (16, m[2])
        GPIO.output (13, on)
        # let it settle, encoder requires this
        time.sleep(0.1)        
        # Enable the modulator
        GPIO.output (22, True)
        # keep enabled for a period
        time.sleep(0.25)
        # Disable the modulator
        GPIO.output (22, False)

    def cleanup(self):
        GPIO.cleanup()

    def GET(self, id):
        self.init()
        self.ctrl_socket(int(id), True)
        self.cleanup()
        return ""

    def DELETE(self, id):
        self.init()
        self.ctrl_socket(int(id), False)
        self.cleanup()
        return ""

if __name__ == '__main__':

    cherrypy.tree.mount(
        Switch(), '/api/switches',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )

    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.engine.start()
    cherrypy.engine.block()

