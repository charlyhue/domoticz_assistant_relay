"""
<plugin key="assistant_relay" name="Assistant relay plugin" author="charly hue" version="1.0.0">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="50px" required="true" default="3000"/>
        <param field="Username" label="Username" width="100px" required="true" default=""/>
        <param field="Mode1" label="Lang" width="75px">
            <options>
                <option label="Français" value="fr"/>
            </options>
        </param>
        <param field="Mode2" label="Strings (separator: |)" width="200px" required="false" default=""/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json
import http.client



class BasePlugin:

    __HEARTBEATS2MIN = 6
    __MINUTES = 1         # or use a parameter

    # Device units
    __UNIT_BROADCAST = 1

    def __init__(self):
        self.__runAgain = 0
        self.conn = None
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)

        self.strings = {"fr": ["", "Debout", "À table", "En route", "C'est l'heure du film", "L'émission va commencer", "Au lit"]}
        for p in Parameters["Mode2"].split('|'):
            self.strings[Parameters["Mode1"]].append(p)

        Options = {"LevelNames": "|".join(self.strings[Parameters["Mode1"]]),
                   "LevelOffHidden": "false",
                   "SelectorStyle": "1"}
        if self.__UNIT_BROADCAST not in Devices:
            Domoticz.Device(Name="Diffusion", Unit=self.__UNIT_BROADCAST,
                            TypeName="Selector Switch", Options=Options, Switchtype=18, Image=8).Create()
        else:
            Devices[self.__UNIT_BROADCAST].Update(nValue=0, sValue='off', Options=Options)


        # Log config
        DumpConfigToLog()
        # Connection

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")



    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug(
            "onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if Unit == self.__UNIT_BROADCAST:
            if Command == 'Set Level':
                Domoticz.Debug(self.strings[Parameters["Mode1"]][int(Level / 10)])

                conn = http.client.HTTPConnection(Parameters["Address"], Parameters["Port"])
                headers = {'Content-type': 'application/json'}
                json_data = json.dumps({"command": self.strings[Parameters["Mode1"]][int(Level / 10)], "user": Parameters["Username"], "broadcast": True})
                conn.request('POST', '/assistant', json_data, headers)

                Devices[self.__UNIT_BROADCAST].Update(0, "off")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS2MIN * self.__MINUTES
            # Execute your command


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

################################################################################
# Generic helper functions
################################################################################
def DumpConfigToLog():
    # Show parameters
    Domoticz.Debug("Parameters count.....: " + str(len(Parameters)))
    for x in Parameters:
        if Parameters[x] != "":
           Domoticz.Debug("Parameter '" + x + "'...: '" + str(Parameters[x]) + "'")
    # Show settings
        Domoticz.Debug("Settings count...: " + str(len(Settings)))
    for x in Settings:
       Domoticz.Debug("Setting '" + x + "'...: '" + str(Settings[x]) + "'")
    # Show images
    Domoticz.Debug("Image count..........: " + str(len(Images)))
    for x in Images:
        Domoticz.Debug("Image '" + x + "...': '" + str(Images[x]) + "'")
    # Show devices
    Domoticz.Debug("Device count.........: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device...............: " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device Idx...........: " + str(Devices[x].ID))
        Domoticz.Debug("Device Type..........: " + str(Devices[x].Type) + " / " + str(Devices[x].SubType))
        Domoticz.Debug("Device Name..........: '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue........: " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue........: '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device Options.......: '" + str(Devices[x].Options) + "'")
        Domoticz.Debug("Device Used..........: " + str(Devices[x].Used))
        Domoticz.Debug("Device ID............: '" + str(Devices[x].DeviceID) + "'")
        Domoticz.Debug("Device LastLevel.....: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device Image.........: " + str(Devices[x].Image))

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")

def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, Options=Options)
            Domoticz.Debug("Device Options update: " + Devices[Unit].Name + " = " + str(Options))

def UpdateDeviceImage(Unit, Image):
    if Unit in Devices and Image in Images:
        if Devices[Unit].Image != Images[Image].ID:
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, Image=Images[Image].ID)
            Domoticz.Debug("Device Image update: " + Devices[Unit].Name + " = " + str(Images[Image].ID))

def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details (" + str(len(httpDict)) + "):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("....'" + x + " (" + str(len(httpDict[x])) + "):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")