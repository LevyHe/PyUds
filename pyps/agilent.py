import re
import serial
import pyps


class AgilentBase(pyps.base.Base):

    '''
    Base class for Agilent power supplies
    '''

    def __init__(self, port, baud=9600):
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

    def tx(self, command, wait_for_completion=False):
        cmd = "%s\r\n" % command
        self.ser.write(cmd.encode('utf-8'))
        if wait_for_completion and "?" not in command:
            print(self.noop())

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


class E364xA(AgilentBase):

    def __init__(self, port, baud=9600, channel=1, **kwargs):
        AgilentBase.__init__(self, port, baud)
        self.channel = channel
        self.response = ""
        command = AgilentBase.format_tx(self, "INST:SEL OUT<nr1>") % (channel)
        AgilentBase.tx(self, command)

    def setactivechannel(self, channel):
        self.channel = channel
        command = AgilentBase.format_tx(self, "INST:SEL OUT<nr1>") % (channel)
        AgilentBase.tx(self, command)

    def getactivechannel(self):
        return self.channel

    def setv(self, volts):
        """Set output to <nrf> Volts."""
        command = AgilentBase.format_tx(self, "VOLT <nr2>") % (volts)
        AgilentBase.tx(self, command)

    def seti(self, amps):
        """Set output current limit to <nrf> Amps."""
        command = AgilentBase.format_tx(self, "CURR <nr2>") % (amps)
        AgilentBase.tx(self, command)

    def setonoff(self, on):
        """Set output on/off."""
        command = AgilentBase.format_tx(self, "Output on" if on else "Output Off")
        AgilentBase.tx(self, command)

    def getv(self):
        """Returns the set voltage of output.
        The response is in Volts
        """
        AgilentBase.tx(self, "VOLTage?")
        return AgilentBase.rx(self, self.response)

    def geti(self):
        """Returns the set current limit of output.
        The response is in Amps
        """
        AgilentBase.tx(self, "CURRent?")
        return AgilentBase.rx(self, self.response)

    def getcurrentv(self):
        """Returns the output readback voltage for output.
        The response is in Volts
        """
        AgilentBase.tx(self, "MEASure:VOLTage?")
        return AgilentBase.rx(self, self.response)

    def getcurrenti(self):
        """Returns the output readback current for output.
        The response is in Amps
        """
        AgilentBase.tx(self, "MEASure:CURRent?")
        return AgilentBase.rx(self, self.response)

    def reset(self):
        """Resets the instrument to the factory default settings with the exception of all
        remote interface settings
        """
        AgilentBase.tx(self, "*RST")

    def clearstatus(self):
        """Clear Status. Clears the Standard Event Status Register, Query Error Register and
        Execution Error Register. This indirectly clears the Status Byte Register.
        """
        AgilentBase.tx(self, "*CLS")

    def save(self, store_id):
        """Save the current set-up of output to the set-up store specified by <nrf> where <nrf> can be 1-5.
        """
        command = AgilentBase.format_tx(self, "*SAV <nrf>") % (store_id)
        AgilentBase.tx(self, command)

    def recall(self, store_id):
        """Recall a set up for output from the set-up store specified by <nrf> where <nrf> can be 1-5.
        """
        command = AgilentBase.format_tx(self, "*RCL <nrf>") % (store_id)
        AgilentBase.tx(self, command)

    def getid(self):
        """Returns the instrument identification."""
        AgilentBase.tx(self, "*IDN?")
        return AgilentBase.rx(self)

    def setopc(self):
        """Sets the Operation Complete bit (bit 0) in the Standard Event Status Register.
        This will happen immediately the command is executed because of the
        sequential nature of all operations.
        """
        AgilentBase.tx(self, "*OPC")

    def getopc(self):
        """Query Operation Complete status. The syntax of the response is 1<rmt>.
        The response will be available immediately the command is executed because of
        the sequential nature of all operations.
        """
        AgilentBase.tx(self, "*OPC?")
        return AgilentBase.rx(self)

    def noop(self):
        return self.getopc()


if __name__ == "__main__":
    from time import sleep
    aiglent = E364xA("COM6")
    aiglent.reset()
    print("getch %s" % aiglent.getactivechannel())
    aiglent.setactivechannel(2)
    print("getid %s" % aiglent.getid())
    aiglent.setonoff(True)
    sleep(1)
    aiglent.setactivechannel(1)
    aiglent.setv(12)
    sleep(1)
    print("getv %s" % aiglent.getcurrentv())
    sleep(1)
    aiglent.setonoff(False)
