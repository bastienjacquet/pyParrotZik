from parrot_zik import resource_manager
from parrot_zik.indicator import Menu
from parrot_zik.indicator import MenuItem
from parrot_zik.model.base import BatteryStates

RECONNECT_FREQUENCY = 5000


class ParrotZikBaseInterface(object):
    def __init__(self, indicator):
        self.indicator = indicator
        self.parrot = None
        self.battery_level = MenuItem("Battery Level:", None, sensitive=False,
                                      visible=False)
        self.battery_state = MenuItem("Battery State:", None, sensitive=False,
                                      visible=False)
        self.firmware_version = MenuItem("Firmware Version:", None,
                                         sensitive=False, visible=False)
        self.settings = MenuItem("Settings", None, visible=False)
        self.settings_submenu = Menu()
        self.settings.set_submenu(self.settings_submenu)

        self.auto_connection = MenuItem("Auto Connection", self.toggle_auto_connection,
                                        checkitem=True)
        self.settings_submenu.append(self.auto_connection)

        self.indicator.menu.append(self.battery_level)
        self.indicator.menu.append(self.battery_state)
        self.indicator.menu.append(self.firmware_version)
        self.indicator.menu.append(self.settings)

    def activate(self, manager):
        self.parrot = self.parrot_class(manager)
        self.read_battery()
        self.indicator.info("Connected to: " + self.parrot.friendly_name)
        self.firmware_version.set_label(
            "Firmware version: " + self.parrot.version)
        self.auto_connection.set_active(self.parrot.auto_connect)
        self.battery_level.show()
        self.battery_state.show()
        self.firmware_version.show()
        self.settings.show()
        self.indicator.active_interface = self

    @property
    def parrot_class(self):
        raise NotImplementedError

    def deactivate(self):
        self.parrot = None
        self.battery_level.hide()
        self.battery_state.hide()
        self.firmware_version.hide()
        self.settings.hide()
        self.indicator.menu.reposition()
        self.indicator.active_interface = None
        self.indicator.setIcon("zik-audio-headset")
        self.indicator.info('Lost Connection')
        self.indicator.reconnect.start(self.indicator, RECONNECT_FREQUENCY)

    def toggle_auto_connection(self, widget):
        try:
            self.parrot.auto_connect = self.auto_connection.get_active()
            self.auto_connection.set_active(self.parrot.auto_connect)
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def refresh(self):
        self.read_battery()

    def read_battery(self):
        try:
            self.parrot.refresh_battery()
            battery_level = self.parrot.battery_level
            battery_state = self.parrot.battery_state
        except resource_manager.DeviceDisconnected:
            self.deactivate()
        else:
            icon_battery_level = int(battery_level/20)*20
            icon_name = "zik-battery-" + format(icon_battery_level, '03')
            if True:
                icon_name += "-headset"
            if battery_state == 'charging':
                icon_name += "-charging"
            elif battery_state == 'charged':
                icon_name += "-charging"
            if self.parrot.version.startswith("2"):
                from parrot_zik.model.version2 import NoiseControlTypes
                if self.parrot.noise_control in [NoiseControlTypes.NOISE_CONTROL_ON,NoiseControlTypes.NOISE_CONTROL_MAX]:
                    icon_name += "-nac"
            if self.parrot.version.startswith("1"):
                if self.parrot.cancel_noise:
                    icon_name += "-nac"
            self.indicator.setIcon(icon_name)
            self.battery_state.set_label(
                "State: " + BatteryStates.representation[battery_state])
            self.battery_level.set_label(
                "Battery Level: " + str(battery_level))
