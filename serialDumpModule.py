import serial, sys, glob, time

### HELPER FUNCTIONS ###
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usb*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def stripped(string):
	return ''.join([i for i in string if 31 < ord(i) < 127])
### HELPER FUNCTIONS ###

### MAIN ###
ports = serial_ports()
# List ports
print 'Listing ports fyi: ' + str(ports)
while True:
    time.sleep(1)
    print 'Waiting for available port.'
    try:
        # Try opening port dynamically
        port = serial.Serial(ports[0], 115200, timeout=1)
    except:
        # Keep querying the port until it is available
        time.sleep(1)
        continue
    # Wait until we receive handshake
    print 'Port opened, waiting for handshake.'
    while stripped(port.readline()) != 'Propeller':
        time.sleep(1)
    print 'Received handshake from Propeller.'

    # Send handshake to ensure connection
    print 'Sending handshake to Propeller, preparing for data transfer.'
    port.write('H0st\n')
    time.sleep(3)

    # Initiate data transfer
    print 'Pulling data.'
    # Flush 5 bytes since H0st is being echoed (workaround)
    port.read(5)
    
    num_records = ord(port.readline()[0])
    if num_records == 1:
        print 'No records found, closing port.'
        port.close()
        continue

    names = []
    emails = []
    # This is our own data
    for i in xrange(0, num_records):
        names.append(stripped(port.readline()))
        emails.append(stripped(port.readline()))

    print 'Dumping to file.'
    f = open('data.txt', 'w')
    f.write('Interaction record for ' + names[0] + ' - ' + emails[0] + ':\n\n')
    for i in xrange(1, num_records):
        f.write(names[i] + ' -> ' + emails[i] + '\n')
    f.close()

    print 'Dump complete, closing port.'
    port.close()

### MAIN ###