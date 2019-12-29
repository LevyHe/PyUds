# -*- coding: utf-8 -*-
"""
Created on Sat Mar  20 10:51:35 2019

@author: levy.he
"""
import ctypes
from . import vxlapy
from . import vxlbase
import time
import threading
from ...fr import FrFrame

class VectorError(IOError):

    def __init__(self, error_code, error_string, function):
        self.error_code = error_code
        text = "%s failed (%s)" % (function, error_string)
        super(VectorError, self).__init__(text)

class FrBus(vxlbase.VxlBase):
    fr_param = dict(busGuardianEnable=0,
                    baudrate=10000000,
                    busGuardianTick=0,
                    externalClockCorrectionMode=0,
                    gColdStartAttempts=10,
                    gListenNoise=2,
                    gMacroPerCycle=5000,
                    gMaxWithoutClockCorrectionFatal=14,
                    gMaxWithoutClockCorrectionPassive=10,
                    gNetworkManagementVectorLength=8,
                    gNumberOfMinislots=92,
                    gNumberOfStaticSlots=33,
                    gOffsetCorrectionStart=4981,
                    gPayloadLengthStatic=32,
                    gSyncNodeMax=8,
                    gdActionPointOffset=9,
                    gdDynamicSlotIdlePhase=0,
                    gdMacrotick=0,
                    gdMinislot=10,
                    gdMiniSlotActionPointOffset=3,
                    gdNIT=48,
                    gdStaticSlot=122,
                    gdSymbolWindow=0,
                    gdTSSTransmitter=9,
                    gdWakeupSymbolRxIdle=59,
                    gdWakeupSymbolRxLow=55,
                    gdWakeupSymbolRxWindow=301,
                    gdWakeupSymbolTxIdle=180,
                    gdWakeupSymbolTxLow=0,
                    pAllowHaltDueToClock=1,
                    pAllowPassiveToActive=2,
                    pChannels=1,
                    pClusterDriftDamping=2,
                    pDecodingCorrection=48,
                    pDelayCompensationA=1,
                    pDelayCompensationB=1,
                    pExternOffsetCorrection=0,
                    pExternRateCorrection=0,
                    pKeySlotUsedForStartup=1,
                    pKeySlotUsedForSync=1,
                    pLatestTx=65,
                    pMacroInitialOffsetA=11,
                    pMacroInitialOffsetB=11,
                    pMaxPayloadLengthDynamic=127,
                    pMicroInitialOffsetA=31,
                    pMicroInitialOffsetB=31,
                    pMicroPerCycle=200000,
                    pMicroPerMacroNom=0,
                    pOffsetCorrectionOut=378,
                    pRateCorrectionOut=601,
                    pSamplesPerMicrotick=2,
                    pSingleSlotEnabled=0,
                    pWakeupChannel=1,
                    pWakeupPattern=50,
                    pdAcceptedStartupRange=212,
                    pdListenTimeout=401202,
                    pdMaxDrift=601,
                    pdMicrotick=0,
                    gdCASRxLowMax=87,
                    gChannels=0,
                    vExternOffsetControl=0,
                    vExternRateControl=0,
                    pChannelsMTS=0)
    def __init__(self, app_name="CANalyzer", channel=0,  spy=False, eray=1, cold=2, poll_interval=0.001, sync_data=[], nm_data=[],
                 rx_queue_size=2 ** 14, **config):
        super(FrBus, self).__init__()
        self.fr_cycle = 0
        self.xlInterfaceVersion = vxlapy.XL_INTERFACE_VERSION_V4
        self.bus_type = vxlapy.XL_BUS_TYPE_FLEXRAY
        self.channel = channel
        self.spy = spy
        self.eray = eray
        self.cold = cold
        self.config = config
        self.SyncAck = False
        self.recv_queue = []
        self.send_quene = []
        self.sync_data = sync_data
        self.nm_data = nm_data
        self._lock = threading.Lock()
        self.poll_interval = poll_interval
        self.rx_queue_size = rx_queue_size
        self._app_name = app_name
        self.channel_info = '%s:Fr %d' % (app_name, self.channel + 1)
        self.clusterConfig = None
        self.channelIdx = self.getchannelIdx()
        self.getChannelMask()
        self.openPort()
        offset = vxlapy.XLuint64()
        self.api.xlGetSyncTime(self.portHandle, offset)
        self.bus_start_time = time.time()
        self._time_offset = self.bus_start_time - offset.value * 1e-9
        self.event_handle = vxlapy.XLhandle()
        self.api.xlSetNotification(
            self.portHandle, ctypes.byref(self.event_handle), 1)
        self._start = True

    def getchannelIdx(self):
        return super(FrBus, self).getchannelIdx(self.channel, self._app_name, self.bus_type)
        
    def getChannelMask(self):
        return super(FrBus, self).getChannelMask(self.bus_type, self.channelIdx,
            self.xlInterfaceVersion)

    def activateChannel(self):
        return super(FrBus, self).activateChannel(self.bus_type)

    def deactivateChannel(self):
        return super(FrBus, self).deactivateChannel()

    def startUpSync(self, erayId=1, coldId=2):
        fr_event = vxlapy.XLfrEvent()
        xlFrMode = vxlapy.XLfrMode()
        payllen = self.clusterConfig.gPayloadLengthStatic
        ctypes.memset(ctypes.byref(fr_event), 0, ctypes.sizeof(fr_event))
        #  setup the startup and sync frames for the E-Ray
        fr_event.tag = vxlapy.XL_FR_TX_FRAME
        fr_event.flagsChip = vxlapy.XL_FR_CHANNEL_A
        fr_event.size = 254
        fr_event.userHandle = 101
        fr_event.tagData.frTxFrame.flags = vxlapy.XL_FR_FRAMEFLAG_STARTUP | vxlapy.XL_FR_FRAMEFLAG_SYNC | vxlapy.XL_FR_FRAMEFLAG_REQ_TXACK
        fr_event.tagData.frTxFrame.offset = 0
        fr_event.tagData.frTxFrame.repetition = 2
        fr_event.tagData.frTxFrame.payloadLength = payllen
        fr_event.tagData.frTxFrame.slotID = erayId
        fr_event.tagData.frTxFrame.txMode = vxlapy.XL_FR_TX_MODE_CYCLIC
        fr_event.tagData.frTxFrame.data[0:254] = [0x88] * 254
        fr_event.tagData.frTxFrame.incrementOffset = 0
        fr_event.tagData.frTxFrame.incrementSize = 0
        fr_event.tagData.frTxFrame.data[0] = erayId
        fr_event.tagData.frTxFrame.data[2 * payllen - 1] = 0xFF - erayId + 1
        fr_event.tagData.frTxFrame.data[:len(self.sync_data)] = bytearray(self.sync_data)
        self.api.xlFrInitStartupAndSync(self.portHandle, self.accessMask, ctypes.byref(fr_event))


        # setup the startup and sync frames for the COLD CC
        # NEEDS advanced LICENSE!
        fr_event.tag = vxlapy.XL_FR_TX_FRAME
        fr_event.flagsChip = vxlapy.XL_FR_CC_COLD_A
        fr_event.size = 254
        fr_event.userHandle = 101
        fr_event.tagData.frTxFrame.flags = vxlapy.XL_FR_FRAMEFLAG_STARTUP | vxlapy.XL_FR_FRAMEFLAG_SYNC | vxlapy.XL_FR_FRAMEFLAG_REQ_TXACK
        fr_event.tagData.frTxFrame.offset = 0
        fr_event.tagData.frTxFrame.repetition = 1
        fr_event.tagData.frTxFrame.payloadLength = payllen
        fr_event.tagData.frTxFrame.slotID = coldId
        fr_event.tagData.frTxFrame.txMode = vxlapy.XL_FR_TX_MODE_CYCLIC
        fr_event.tagData.frTxFrame.data[0:254] = [0xFF] * 254
        fr_event.tagData.frTxFrame.data[:len(self.nm_data)] = bytearray(self.nm_data)
        fr_event.tagData.frTxFrame.incrementOffset = 0
        fr_event.tagData.frTxFrame.incrementSize = 0
        self.api.xlFrInitStartupAndSync(self.portHandle, self.accessMask, ctypes.byref(fr_event))

        fr_event.tag = vxlapy.XL_FR_TX_FRAME
        fr_event.flagsChip = vxlapy.XL_FR_CC_COLD_B
        fr_event.size = 254
        fr_event.userHandle = 101
        fr_event.tagData.frTxFrame.flags = vxlapy.XL_FR_FRAMEFLAG_STARTUP | vxlapy.XL_FR_FRAMEFLAG_SYNC | vxlapy.XL_FR_FRAMEFLAG_REQ_TXACK
        fr_event.tagData.frTxFrame.offset = 0
        fr_event.tagData.frTxFrame.repetition = 1
        fr_event.tagData.frTxFrame.payloadLength = payllen
        fr_event.tagData.frTxFrame.slotID = coldId
        fr_event.tagData.frTxFrame.txMode = vxlapy.XL_FR_TX_MODE_CYCLIC
        fr_event.tagData.frTxFrame.data[0:254] = [0xFF] * 254
        fr_event.tagData.frTxFrame.incrementOffset = 0
        fr_event.tagData.frTxFrame.incrementSize = 0
        self.api.xlFrInitStartupAndSync(self.portHandle, self.accessMask, ctypes.byref(fr_event))

        #setup the mode for the E-Ray CC
        xlFrMode.frMode = vxlapy.XL_FR_MODE_NORMAL
        xlFrMode.frStartupAttributes = vxlapy.XL_FR_MODE_COLDSTART_LEADING
        self.api.xlFrSetMode(self.portHandle, self.accessMask, ctypes.byref(xlFrMode))

        # setup the mode for the COLD CC
        xlFrMode.frMode = vxlapy.XL_FR_MODE_COLD_NORMAL
        xlFrMode.frStartupAttributes = vxlapy.XL_FR_MODE_COLDSTART_LEADING
        self.api.xlFrSetMode(self.portHandle, self.accessMask, ctypes.byref(xlFrMode))

    def getKeymaninfo(self):
        nbrOfBoxes = ctypes.c_uint()
        boxMask = ctypes.c_uint()
        boxSerial = ctypes.c_uint()
        licInfo = (ctypes.c_uint64*4)()
        self.api.xlGetKeymanBoxes(ctypes.byref(nbrOfBoxes))
        for i in range(nbrOfBoxes):
            self.api.xlGetKeymanInfo(i, ctypes.byref(boxMask), ctypes.byref(boxSerial), licInfo)
            print("xlGetKeymanInfo: Keyman Dongle (%d) with SerialNumber: %d-%d"%(i, boxMask, boxSerial))
        
    def openPort(self):
        super(FrBus, self).openPort(busType=self.bus_type, userName=self._app_name,
                                    rxQueueSize=self.rx_queue_size, xlInterfaceVersion=self.xlInterfaceVersion)
        self.clusterConfig = vxlapy.XLfrClusterConfig()
        for k in self.fr_param:
            if k in self.config:
                setattr(self.clusterConfig, k, self.config[k])
            else:
                setattr(self.clusterConfig, k, self.fr_param[k])
        if self.initAccess:
            self.api.xlFrSetConfiguration(self.portHandle, self.accessMask, ctypes.byref(self.clusterConfig))
            if not self.spy:
                self.startUpSync(self.eray,self.cold)
        self.activateChannel()

    def shutdown(self):
        self.flush_tx_buffer()
        self.flush_rx_buffer()
        self.closePort()
        self._start = False

    def start(self):
        if not self._start:
            super(FrBus, self).__init__()
            self.fr_cycle = 0
            self.xlInterfaceVersion = vxlapy.XL_INTERFACE_VERSION_V4
            self.bus_type = vxlapy.XL_BUS_TYPE_FLEXRAY
            self.recv_queue = []
            self.send_quene = []
            self._lock = threading.Lock()
            self.clusterConfig = None
            self.channelIdx = self.getchannelIdx()
            self.getChannelMask()
            self.openPort()
            offset = vxlapy.XLuint64()
            self.api.xlGetSyncTime(self.portHandle, offset)
            self.bus_start_time = time.time()
            self._time_offset = self.bus_start_time - offset.value * 1e-9
            self.event_handle = vxlapy.XLhandle()
            self.api.xlSetNotification(
                self.portHandle, ctypes.byref(self.event_handle), 1)
            self._start = True

    def reset(self):
        self.deactivateChannel()
        self.activateChannel()

    def get_fr_cycle(self):
        return self.fr_cycle

    def recv_event(self):
        event = vxlapy.XLfrEvent()
        with self._lock:
            try:
                self.api.xlFrReceive(self.portHandle, ctypes.byref(event))
            except vxlapy.XLstatusError as e:
                if e.status not in [vxlapy.XL_ERR_QUEUE_IS_EMPTY, vxlapy.XL_ERROR]:
                    raise
            else:
                if event.tag == vxlapy.XL_FR_TXACK_FRAME:
                    self.send_msg_ack(event)
                    self.recv_queue.append(event)
                elif event.tag == vxlapy.XL_FR_RX_FRAME:
                    self.fr_cycle = event.tagData.frRxFrame.cycleCount
                    self.recv_queue.append(event)
                elif event.tag == vxlapy.XL_FR_WAKEUP:
                    self.fr_cycle = event.tagData.frWakeup.cycleCount
                elif event.tag == vxlapy.XL_FR_SYMBOL_WINDOW:
                    self.fr_cycle = event.tagData.frSymbolWindow.cycleCount
                elif event.tag == vxlapy.XL_FR_START_CYCLE:
                    self.SyncAck = True
                    self.fr_cycle = event.tagData.frStartCycle.cycleCount
                elif event.tag == vxlapy.XL_FR_ERROR:
                    self.fr_cycle = event.tagData.frError.cycleCount
                elif event.tag == vxlapy.XL_FR_NM_VECTOR:
                    self.fr_cycle = event.tagData.frNmVector.cycleCount
                elif event.tag == vxlapy.XL_FR_SPY_FRAME:
                    self.fr_cycle = event.tagData.frSpyFrame.cycleCount
    def send(self, msg, timeout=None):

        xlFrEvent = vxlapy.XLfrEvent()
        ctypes.memset(ctypes.byref(xlFrEvent), 0, ctypes.sizeof(xlFrEvent))

        xlFrEvent.tag = vxlapy.XL_FR_TX_FRAME
        xlFrEvent.flagsChip = msg.channel_mask
        xlFrEvent.tagData.frTxFrame.flags = vxlapy.XL_FR_FRAMEFLAG_REQ_TXACK
        xlFrEvent.tagData.frTxFrame.offset = msg.base_cycle
        xlFrEvent.tagData.frTxFrame.repetition = msg.repetition_cycle
        xlFrEvent.tagData.frTxFrame.payloadLength = msg.pay_load_length
        xlFrEvent.tagData.frTxFrame.slotID = msg.slot_id
        xlFrEvent.tagData.frTxFrame.txMode = vxlapy.XL_FR_TX_MODE_SINGLE_SHOT if msg.single_shot else vxlapy.XL_FR_TX_MODE_CYCLIC
        xlFrEvent.tagData.frTxFrame.incrementOffset = 0
        xlFrEvent.tagData.frTxFrame.incrementSize = 0
        xlFrEvent.tagData.frTxFrame.data[0:len(msg.data)] = msg.data
        self.send_quene.append(msg.slot_id)
        self.api.xlFrTransmit(self.portHandle, self.accessMask, ctypes.byref(xlFrEvent))
        # if timeout is None:
        #     return
        # end_time = time.time() + timeout
        # while True:
        #     self.recv_event()
        #     if self.SendAck:
        #         return
        #     if end_time is not None and time.time() > end_time:
        #         raise Exception("Flexray transmit timeout")
        #     time_left = end_time - time.time()
        #     time_left_ms = max(0, int(time_left * 1000))
        #     self.api.waitForSingleObject(self.event_handle.value, time_left_ms)
    
    def send_msg_ack(self, event):
        rv = event.tagData.frRxFrame.slotID
        if rv in self.send_quene:
            self.send_quene.remove(rv)

    def wait_sync(self, timeout=None):
        end_time = time.time() + timeout if timeout is not None else None
        while True:
            self.recv_event()
            if self.SyncAck:
                self.SyncAck = False
                if len(self.send_quene)==0:
                    return 0
                else:
                    return -1
            if end_time is not None and time.time() > end_time:
                if len(self.send_quene) == 0:
                    return 0
                else:
                    return -1
            if len(self.recv_queue) > 0:
                return len(self.recv_queue)
            if timeout is None:
                time_left_ms = 1000
            else:
                time_left = end_time - time.time()
                time_left_ms = max(0, int(time_left * 1000))
            self.api.waitForSingleObject(self.event_handle.value, time_left_ms)

    def recv(self, timeout=None):
        if len(self.recv_queue) > 0:
            event = self.recv_queue.pop()
            slot_id = event.tagData.frRxFrame.slotID
            cycle = event.tagData.frRxFrame.cycleCount
            base_cycle = 0
            repetition_cycle = 1
            pay_load_length = event.tagData.frRxFrame.payloadLength
            flags = event.tagData.frRxFrame.flags
            timestamp = event.timeStamp * 1e-9
            channel = self.channel
            channel_mask = event.flagsChip
            if pay_load_length > 0:
                msg = FrFrame(
                    timestamp=timestamp + self._time_offset,
                    slot_id=slot_id,
                    base_cycle=base_cycle,
                    cycle=cycle,
                    direction='Tx' if bool(flags & vxlapy.XL_FR_FRAMEFLAG_FRAME_TRANSMITTED) else 'Rx',
                    repetition_cycle=repetition_cycle,
                    pay_load_length=pay_load_length,
                    channel_mask=channel_mask,
                    data=list(event.tagData.frRxFrame.data)[0:pay_load_length* 2],
                    flags=flags,
                    channel=channel)
                return msg
            else:
                return None
        else:
            return None

if __name__ == "__main__":
    fr = FrBus()
    msg = fr.recv()
    print(msg)
    fr.shutdown()
