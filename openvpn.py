# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import subprocess, os

class openvpn(kp.Plugin):
    """
    Keypirinha plugin for connecting to openvpn profiles more conveniently
    Some values currently hardcoded.

    More detailed documentation at: http://keypirinha.com/api/plugin.html
    --command cmd where cmd is:
    connect cnn
    disconnect cnn
    reconnect cnn
    disconnect_all
    status cnn
    TODO:
    magic variables, abstractions, display stderr
    config options?
    read from config
    move config_folder
    """
    DEFAULT_ITEM_LABEL = "OpenVPN-Gui"
    DEFAULT_ITEM_DESC = "Manipulate openvpn connections"
    KEYWORD = "OpenVPN"
    DEFAULT_IDLE_TIME = 0.25
    ACTION_CONNECT = "connect"
    ACTION_DISCONNECT = "disconnect"
    ACTION_STATUS = "status"
    ACTION_RECONNECT = "reconnect"
    CONFIG_FOLDER = "C:/Users/alex/OpenVPN/config"

    ITEMCAT_OPENVPN = kp.ItemCategory.USER_BASE + 1
    ITEMCAT_OPENVPN_DC_ALL = kp.ItemCategory.USER_BASE + 2

    def __init__(self):
        super().__init__()
        self._debug = False

    def on_start(self):
        actions = [
            self.create_action(
                name=self.ACTION_CONNECT,
                label="Connect",
                short_desc="Connect this config"),
            self.create_action(
                name=self.ACTION_DISCONNECT,
                label="Disconnect",
                short_desc="Disconnect this config"),
            self.create_action(
                name=self.ACTION_RECONNECT,
                label="Reconnect",
                short_desc="Reconnect this config"),
            self.create_action(
                name=self.ACTION_STATUS,
                label="Status",
                short_desc="Check status of connection") ]
        self.set_actions(self.ITEMCAT_OPENVPN, actions)


    def on_catalog(self):
        self.dbg("On Catalog")
        items = list(map(lambda c: self._create_connection(c), self._get_configs()))
        self.dbg(f"About to catalog: {self._get_configs()}, targets: {[i.target() for i in items]}")

        items = items + [self._create_dc_item()]

        self.set_catalog(items)

    def _create_connection(self, connection_path):
        connection_name, _ = os.path.splitext(connection_path)
        return self._create_connection_item(self.DEFAULT_ITEM_LABEL, connection_name)

    def on_suggest(self, user_input, items_chain):
        pass

    def on_execute(self, item, action):
        self.dbg('On Execute "{}" (action: {} action.name: {})'.format(item, action, action.name() if action else "action is None and has no name"))

        if item and item.category() == self.ITEMCAT_OPENVPN_DC_ALL:
            self._call_command(['disconnect_all'])
            return

        if not item or item.category() != self.ITEMCAT_OPENVPN:
            return


        cnn = item.data_bag()
        if action and action.name() in (self.ACTION_CONNECT,
                                        self.ACTION_DISCONNECT,
                                        self.ACTION_RECONNECT,
                                        self.ACTION_STATUS):
            if action.name() == self.ACTION_CONNECT:
                self._call_command(['disconnect_all'])
                self._call_command(['connect', cnn])
            elif action.name() == self.ACTION_DISCONNECT:
                self._call_command(['disconnect', cnn])
            elif action.name() == self.ACTION_RECONNECT:
                self._call_command(['reconnect', cnn])
            elif action.name() == self.ACTION_STATUS:
                self._call_command(['status', cnn])

        else:
            self._call_command(['disconnect_all'])
            self._call_command(['connect', cnn])

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        pass

    def _call_command(self, args):
        # hide window
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # TODO abstract into arbitrary executable path
        exec_list = ["C:/Program Files/OpenVPN/bin/openvpn-gui.exe", "--command"] + args

        p = subprocess.Popen(exec_list, stderr=subprocess.PIPE, startupinfo=si)

        _, stderr = p.communicate()
        # set single item on cat to stderr

    def _get_configs(self):
        config_ext = ".ovpn"

        return [f for f in os.listdir(self.CONFIG_FOLDER)
            if os.path.isfile(os.path.join(self.CONFIG_FOLDER, f))
            and os.path.splitext(f)[1] == config_ext]


    def _create_connection_item(self, label, connection_name):
        return self.create_item(
            category=self.ITEMCAT_OPENVPN,
            label=str(f"{label} : {connection_name}"),
            short_desc=str(f"{label} : Connection action on {connection_name}"),
            target=str(connection_name),
            args_hint=kp.ItemArgsHint.FORBIDDEN,
            hit_hint=kp.ItemHitHint.IGNORE,
            data_bag=str(connection_name)
            )

    def _create_dc_item(self):
        return self.create_item(
            category=self.ITEMCAT_OPENVPN_DC_ALL,
            label=str(f"{self.DEFAULT_ITEM_LABEL}: Disconnect all"),
            short_desc=f"{self.DEFAULT_ITEM_LABEL} : Disconnect from all connections",
            target=str(f"{self.DEFAULT_ITEM_LABEL}: Disconnect all"),
            args_hint=kp.ItemArgsHint.FORBIDDEN,
            hit_hint=kp.ItemHitHint.IGNORE
            )

