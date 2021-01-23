import re

import serial

import pyps


class TTiBase(pyps.base.Base):

    '''
    Base class for TTi power supplies
    '''

    def __init__(self, port, baud=19200):
        self.ser = None
        self.ser = serial.Serial(port, baud, timeout=1, xonxoff=True)

    def __del__(self):
        if self.ser is not None and self.ser.isOpen():
            self.ser.close()

    def noop(self):
        raise NotImplementedError

    def format_tx(self, cmdfmt):
        subst = [("<rmt>", ""),
                 ("<nrf>", "%.3f"),
                 ("<nr1>", "%d"),
                 ("<nr2>", "%.3f"),
                 ("<n>", "%d")]
        for r in subst:
            cmdfmt = cmdfmt.replace(r[0], r[1])
        return cmdfmt

    def tx(self, command, wait_for_completion=True):
        self.ser.write("%s\r\n" % command)
        if wait_for_completion and "?" not in command:
            self.noop()

    def rx(self, rspfmt=None):
        rx = self.ser.readline().strip()
        return self.format_rx(rx, rspfmt) if rspfmt else rx

    def format_rx(self, rxstr, rspfmt):
        rspsubst = [("<rmt>", r"\s*"),
                    ("<nrf>", r"([\d.]+)"),
                    ("<nr1>", r"(\d+)"),
                    ("<nr2>", r"([\d.]+)"),
                    ("<n>", r"(\d+)")]
        for r in rspsubst:
            rspfmt = rspfmt.replace(r[0], r[1])
        matches = re.match(rspfmt, rxstr)
        if matches:
            return matches.groups()[0] if len(matches.groups()) == 1 else matches.groups()
        else:
            return rxstr


class EX355P(TTiBase):

    def __init__(self, port, baud=9600, **kwargs):
        TTiBase.__init__(self, port, baud)
        self.lastv = None

    def setv(self, volts):
        """Set output to <nrf> Volts."""
        command = TTiBase.format_tx(self, "V <nr2>") % (volts)
        if command != self.lastv:
            TTiBase.tx(self, command)
            self.lastv = command

    def seti(self, amps):
        """Set output current limit to <nrf> Amps"""
        command = TTiBase.format_tx(self, "I <nr2>") % (amps)
        TTiBase.tx(self, command)

    def setonoff(self, on):
        """Set output on/off"""
        command = TTiBase.format_tx(self, "ON" if on else "OFF")
        TTiBase.tx(self, command)

    def getv(self):
        """Returns the set voltage of output.
        The response is V <nr2><rmt> where <nr2> is in Volts
        """
        command = TTiBase.format_tx(self, "V?")
        TTiBase.tx(self, command)
        response = "V <nr2><rmt>"
        return TTiBase.rx(self, response)

    def geti(self):
        """Returns the set current limit of output
        The response is I <nr2><rmt> where <nr2> is in Amps
        """
        command = TTiBase.format_tx(self, "I?")
        TTiBase.tx(self, command)
        response = "I <nr2><rmt>"
        return TTiBase.rx(self, response)

    def getcurrentv(self):
        """Returns the output readback voltage for output.
        The response is V<nr2><rmt> where <nr2> is in Volts
        """
        command = TTiBase.format_tx(self, "VO?")
        TTiBase.tx(self, command)
        response = "V <nr2><rmt>"
        return TTiBase.rx(self, response)

    def getcurrenti(self):
        """Returns the output readback current for output.
        The response is A<nr2><rmt> where <nr2> is in Amps
        """
        command = TTiBase.format_tx(self, "IO?")
        TTiBase.tx(self, command)
        response = "I <nr2><rmt>"
        return TTiBase.rx(self, response)

    def getonoff(self):
        """Returns the output readback current for output.
        The response is A<nr2><rmt> where <nr2> is in Amps
        """
        command = TTiBase.format_tx(self, "OUT?")
        TTiBase.tx(self, command)
        response = "OUT (.*)<rmt>"
        return TTiBase.rx(self, response)

    def getid(self):
        """Returns the instrument identification."""
        command = TTiBase.format_tx(self, "*IDN?")
        TTiBase.tx(self, command)
        return TTiBase.rx(self)

    def noop(self):
        return self.getid()


class QL355_564P(TTiBase):

    def __init__(self, port, baud=19200, channel=1, **kwargs):
        TTiBase.__init__(self, port, baud)
        self.channel = channel

    def setactivechannel(self, channel):
        self.channel = channel

    def getactivechannel(self):
        return self.channel

    def setv(self, volts):
        """Set output <n> to <nrf> Volts. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "V<n> <nrf>") % (self.channel, volts)
        TTiBase.tx(self, command)

    def setvv(self, volts):
        """Set output <n> to <nrf> Volts with verify. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "V<n>V <nrf>") % (self.channel, volts)
        TTiBase.tx(self, command)

    def setovp(self, volts):
        """Set output <n> over voltage protection trip point to <nrf> Volts"""
        command = TTiBase.format_tx(self, "OVP<n> <nrf>") % (self.channel, volts)
        TTiBase.tx(self, command)

    def seti(self, amps):
        """Set output <n> current limit to <nrf> Amps"""
        command = TTiBase.format_tx(self, "I<n> <nrf>") % (self.channel, amps)
        TTiBase.tx(self, command)

    def setocp(self, amps):
        """Set output <n> over current protection trip point to <nrf> Amps"""
        command = TTiBase.format_tx(self, "OCP<n> <nrf>") % (self.channel, amps)
        TTiBase.tx(self, command)

    def getv(self):
        """Returns the set voltage of output <n>. For AUX output <n>=3
        The response is V<n> <nr2><rmt> where <nr2> is in Volts
        """
        command = TTiBase.format_tx(self, "V<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "V<n> <nr2><rmt>"
        return TTiBase.rx(self, response)

    def geti(self):
        """Returns the set current limit of output <n>
        The response is I<n> <nr2><rmt> where <nr2> is in Amps
        """
        command = TTiBase.format_tx(self, "I<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "I<n> <nr2><rmt>"
        return TTiBase.rx(self, response)

    def getovp(self):
        """Returns the voltage trip setting for output <n>
        The response is VP<n> <nr2><rmt> where <nr2> is in Volts
        """
        command = TTiBase.format_tx(self, "OVP<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "VP<n> <nr2><rmt>"
        return TTiBase.rx(self, response)

    def getocp(self):
        """Returns the current trip setting for output <n>
        The response is CP<n> <nr2><rmt> where <nr2> is in Amps
        """
        command = TTiBase.format_tx(self, "OCP<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "CP<n> <nr2><rmt>"
        return TTiBase.rx(self, response)

    def getcurrentv(self):
        """Returns the output readback voltage for output <n>. For AUX output <n>=3
        The response is <nr2>V<rmt> where <nr2> is in Volts
        """
        command = TTiBase.format_tx(self, "V<n>O?") % (self.channel)
        TTiBase.tx(self, command)
        response = "<nr2>V<rmt>"
        return TTiBase.rx(self, response)

    def getcurrenti(self):
        """Returns the output readback current for self.channel <n>. For AUX output <n>=3
        The response is <nr2>A<rmt> where <nr2> is in Amps
        """
        command = TTiBase.format_tx(self, "I<n>O?") % (self.channel)
        TTiBase.tx(self, command)
        response = "<nr2>A<rmt>"
        return TTiBase.rx(self, response)

    def setrange(self, range_id):
        """Set the voltage range of output <n> to <nrf> where <nrf> has the following meaning:
        QL355 Models: 0=15V(5A), 1=35V(3A), 2=35V(500mA)
        QL564 Models: 0=25V(4A), 1=56V(2A), 2=56V(500mA)
        """
        command = TTiBase.format_tx(self, "RANGE<n> <nrf>") % (self.channel, range_id)
        TTiBase.tx(self, command)

    def getrange(self):
        """Report the current range for output <n>
        The response is R<n> <nr1><rmt> where <nr1> has the following meaning:
        QL355 Models: 0=15V(5A), 1=35V(3A), 2=35V(500mA)
        QL564 Models: 0=25V(4A), 1=56V(2A), 2=56V(500mA)
        """
        command = TTiBase.format_tx(self, "RANGE<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def setdeltav(self, voltage_step):
        """Set the output <n> voltage step size to <nrf> Volts. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "DELTAV<n> <nrf>") % (self.channel, voltage_step)
        TTiBase.tx(self, command)

    def setdeltai(self, current_step):
        """Set the output <n> current step size to <nrf> Amps. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "DELTAI<n> <nrf>") % (self.channel, current_step)
        TTiBase.tx(self, command)

    def getdeltav(self):
        """Returns the output <n> voltage step size. For AUX output <n>=3
        The response is DELTAV<n> <nr2><rmt> where <nr2> is in Volts.
        """
        command = TTiBase.format_tx(self, "DELTAV<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "DELTAV<n> <nr2><rmt>"
        return TTiBase.rx(self, response)

    def getdeltai(self):
        """Returns the output <n> current step size
        The response is DELTAI<n> <nr2><rmt> where <nr2> is in Amps.
        """
        command = TTiBase.format_tx(self, "DELTAI<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "DELTAI<n> <nr2><rmt>"
        return TTiBase.rx(self, response)

    def setincv(self):
        """Increment the output <n> voltage by the step size set for output <n>. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "INCV<n>") % (self.channel)
        TTiBase.tx(self, command)

    def setincvv(self):
        """Increment the output <n> voltage by the step size set for output <n> and verify. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "INCV<n>V") % (self.channel)
        TTiBase.tx(self, command)

    def setdecv(self):
        """Decrement the output <n> voltage by the step size set for output <n>. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "DECV<n>") % (self.channel)
        TTiBase.tx(self, command)

    def setdecvv(self):
        """Decrement the output <n> voltage by the step size set for output <n> and verify. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "DECV<n>V") % (self.channel)
        TTiBase.tx(self, command)

    def setinci(self):
        """Increment the output <n> current limit by the step size set for output <n>"""
        command = TTiBase.format_tx(self, "INCI<n>") % (self.channel)
        TTiBase.tx(self, command)

    def setdeci(self):
        """decrement the output <n> current limit by the step size set for output <n>"""
        command = TTiBase.format_tx(self, "DECI<n>") % (self.channel)
        TTiBase.tx(self, command)

    def setonoff(self, on):
        """Set output <n> on/off where <nrf> has the following meaning: 0=OFF, 1=ON. For AUX output <n>=3"""
        command = TTiBase.format_tx(self, "OP<n> <nrf>") % (self.channel, on)
        TTiBase.tx(self, command)

    def setonoffall(self, on):
        """Simultaneously sets all outputs on/off where <nrf> has the following meaning:
        0=ALL OFF, 1=ALL ON.
        If OPALL sets all outputs ON then any that were already on will remain ON
        If OPALL sets all outputs OFF then any that were already off will remain OFF
        """
        command = TTiBase.format_tx(self, "OPALL <nrf>") % (on)
        TTiBase.tx(self, command)

    def getonoff(self):
        """Returns output <n> on/off status.
        The response is <nr1><rmt> where 1 = ON, 0 = OFF."""
        command = TTiBase.format_tx(self, "OP<n>?") % (self.channel)
        TTiBase.tx(self, command)
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def settriprst(self):
        """Attempt to clear all trip conditions."""
        command = TTiBase.format_tx(self, "TRIPRST")
        TTiBase.tx(self, command)

    def setlocal(self):
        """Go to local. This does not release any active interface lock so that the lock remains
        with the selected interface when the next remote command is received.
        """
        command = TTiBase.format_tx(self, "LOCAL")
        TTiBase.tx(self, command)

    def setiflock(self):
        """Request interface lock. This command requests exclusive access control of the instrument.
        The response is 1 if successful or -1 if the lock is unavailable either because it is already
        in use or the user has disabled this interface from taking control using the web interface
        """
        command = TTiBase.format_tx(self, "IFLOCK")
        TTiBase.tx(self, command)

    def getiflock(self):
        """Query the status of the interface lock.
        The return value is 1 if the lock is owned by the requesting interfaced instance;
        0 if there is no active lock or -1 if the lock is unavailable either because it is already in use,
        or the user has disabled this interface from taking control using the web interface.
        """
        command = TTiBase.format_tx(self, "IFLOCK?")
        TTiBase.tx(self, command)
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def setifunlock(self):
        """Release the lock if possible. This command returns the value 0 if successful.
        If this command is unsuccessful -1 is returned, 200 is placed in the Execution Register and
        bit 4 of the Event Status Register is set indicating that there is no authority to release the lock.
        """
        command = TTiBase.format_tx(self, "IFUNLOCK")
        TTiBase.tx(self, command)

    def getlsr(self, lsr):
        """Query and clear LSR<n>, limit status register <n> response is <nr1><rmt>"""
        command = TTiBase.format_tx(self, "LSR<n>?") % (lsr)
        TTiBase.tx(self, command)
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def setlse(self, lse, value):
        """Set the value of LSE<n>, Limit Event Status Enable Register <n>, to <nrf>"""
        command = TTiBase.format_tx(self, "LSE<n> <nrf>") % (lse, value)
        TTiBase.tx(self, command)

    def getlse(self, lse):
        """Return the value of LSE<n>, Limit Event Status Enable Register <n> - response is <nr1><rmt>"""
        command = TTiBase.format_tx(self, "LSE<n>?") % (lse)
        TTiBase.tx(self, command)
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def save(self, store_id):
        """Save the current set-up of output <n> to the set-up store specified by <nrf> where <nrf> can be 0-9.
        For AUX output <n>=3
        """
        command = TTiBase.format_tx(self, "SAV<n> <nrf>") % (self.channel, store_id)
        TTiBase.tx(self, command)

    def recall(self, store_id):
        """Recall a set up for output <n> from the set-up store specified by <nrf> where <nrf> can be 0-9.
        For AUX output <n>=3
        """
        command = TTiBase.format_tx(self, "RCL<n> <nrf>") % (self.channel, store_id)
        TTiBase.tx(self, command)

    def reset(self):
        """Resets the instrument to the factory default settings with the exception of all
        remote interface settings
        """
        TTiBase.tx(self, "*RST")

    def geteer(self):
        """Query and clear Execution Error Register. The response format is nr1<rmt>.
        """
        TTiBase.tx(self, "EER?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def getqer(self):
        """Query and clear Query Error Register. The response format is nr1<rmt>
        """
        TTiBase.tx(self, "QER?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def clearstatus(self):
        """Clear Status. Clears the Standard Event Status Register, Query Error Register and
        Execution Error Register. This indirectly clears the Status Byte Register.
        """
        TTiBase.tx(self, "*CLS")

    def setese(self, value):
        """Set the Standard Event Status Enable Register to the value of <nrf>.
        """
        command = TTiBase.format_tx(self, "*ESE <nrf>") % (value)
        TTiBase.tx(self, command)

    def getese(self):
        """Returns the value in the Standard Event Status Enable Register in <nr1> numeric format.
        The syntax of the response is <nr1><rmt>
        """
        TTiBase.tx(self, "*ESE?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def getesr(self):
        """Returns the value in the Standard Event Status Register in <nr1> numeric format. The
        register is then cleared. The syntax of the response is <nr1><rmt>
        """
        TTiBase.tx(self, "*ESR?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def getist(self):
        """Returns ist local message as defined by IEEE Std. 488.2. The syntax of the response is
        0<rmt>, if the local message is false, or 1<rmt>, if the local message is true.
        """
        TTiBase.tx(self, "*IST?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def setopc(self):
        """Sets the Operation Complete bit (bit 0) in the Standard Event Status Register.
        This will happen immediately the command is executed because of the
        sequential nature of all operations.
        """
        TTiBase.tx(self, "*OPC")

    def getopc(self):
        """Query Operation Complete status. The syntax of the response is 1<rmt>.
        The response will be available immediately the command is executed because of
        the sequential nature of all operations.
        """
        TTiBase.tx(self, "*OPC?")
        return TTiBase.rx(self)

    def setpre(self, value):
        """Set the Parallel Poll Enable Register to the value <nrf>.
        """
        command = TTiBase.format_tx(self, "*PRE <nrf>") % (value)
        TTiBase.tx(self, command)

    def getpre(self):
        """Returns the value in the Parallel Poll Enable Register in <nr1> numeric format.
        The syntax of the response is <nr1><rmt>
        """
        TTiBase.tx(self, "*PRE?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def setsre(self, value):
        """Set the Service Request Enable Register to <nrf>.
        """
        command = TTiBase.format_tx(self, "*SRE <nrf>") % (value)
        TTiBase.tx(self, command)

    def getsre(self):
        """Returns the value of the Service Request Enable Register in <nr1> numeric format. The
        syntax of the response is <nr1><rmt>
        """
        TTiBase.tx(self, "*SRE?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def getstb(self):
        """Returns the value of the Status Byte Register in <nr1> numeric format. The syntax of the
        response is <nr1><rmt>
        """
        TTiBase.tx(self, "*STB?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def wait(self):
        """Wait for Operation Complete true. As all commands are completely executed before the
        next is started this command takes no additional action.
        """
        TTiBase.tx(self, "*WAI")

    def getid(self):
        """Returns the instrument identification."""
        command = TTiBase.format_tx(self, "*IDN?")
        TTiBase.tx(self, command)
        return TTiBase.rx(self)

    def getaddress(self):
        """Returns the bus address of the instrument. The syntax of the response is <nr1><rmt>.
        """
        TTiBase.tx(self, "ADDRESS?")
        response = "<nr1><rmt>"
        return TTiBase.rx(self, response)

    def noop(self):
        return self.getopc()

if __name__ == "__main__":
    from time import sleep
    tti = QL355_564P("COM16")
    tti.seti(3)
    tti.setonoff(True)
    print("getid %s" % tti.getid())
    print("seti %s" % tti.seti(1))
    print("setv %s" % tti.setv(13.8))
    sleep(1)
    print("turn on %s" % tti.setonoff(True))
    sleep(1)
    print("rampv 12 0 10 %s" % tti.rampv(12, 0, 10))
    sleep(1)
    print("turn off %s" % tti.setonoff(False))
    sleep(1)
    print("setv %s" % tti.setv(12))
    sleep(1)
    print("getv %s" % tti.getv())
    sleep(1)
    print("turn on %s" % tti.setonoff(True))
    sleep(1)
    print("currentv %s" % tti.getcurrentv())
    print("currenti %s" % tti.getcurrenti())
