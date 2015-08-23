import serial, sys, glob, time, os

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

    return ports

    # Checking the ports already sends a reset signal.
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
while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    raw_input('Press Enter to begin connection.')
    for p in ports:
        try:
            # Try opening ports, if we find one, send reset signal
            port = serial.Serial(p, 115200, timeout=1)
            port.close()
            break
        except:
            # Keep querying until we find a port
            pass
    try:
        port.isOpen()
    except:
        raw_input('Unable to find a badge, press Enter to continue.')
        continue
    # Wait until we receive handshake
    print 'Port opened, hold OSH on your badge.'
    port.open()
    while stripped(port.readline()) != 'Propeller':
        time.sleep(1)
    print 'Detected badge.'

    # Send handshake to ensure connection
    print 'Preparing data transfer.'
    port.write('H0st\n')
    time.sleep(3)

    # Initiate data transfer
    print 'Pulling data.'
    # Flush 5 bytes since H0st is being echoed (workaround)
    port.read(5)    
    
    # Get records, if no records are found, it won't dump
    num_records = ord(port.readline()[0])
    # For num_records, since Propeller cannot send an int yet, we send a byte
    # So we can have a maximum of 255 interactions, else it'll overflow
    if num_records == 1:
        raw_input('No records found, press Enter to exit.')
        port.close()
        # time.sleep(5)
        continue

    names = []
    emails = []
    # This is our own data
    for i in xrange(0, num_records):
        names.append(stripped(port.readline()))
        emails.append(stripped(port.readline()))

    # Dump to file
    print 'Dumping interactions.'
    f = open(names[0] + '-' + emails[0] + '.txt', 'w')
    f.write('Interaction record for ' + names[0] + ' - ' + emails[0] + ':\n\n')
    for i in xrange(1, num_records):
        f.write(names[i] + ' -> ' + emails[i] + '\n')
    f.close()

    raw_input('Dump complete, press Enter to exit.')
    port.close()
    # time.sleep(5)

### MAIN ###

### NOTES ###

### TODO ###
# -Better way to ensure disconnection, wait until user disconnects then find
# a way to send a reset signal.