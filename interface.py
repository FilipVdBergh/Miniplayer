import libLCDUI.libLCDUI as libLCDUI
import pylms.server
from player_variables import *
import time
import threading

class Interface(object):
    def __init__(self, display, server, player):
        self.ui = libLCDUI.ui(display, width=20, height=4)
        self.server_address = server
        self.player_name = player
        self.server = None
        self.player = None
        self.all_players = []
        self.all_favorites = []
        self.power = True
        self.mode = 0
        self.modes = {0: ["Now playing", "~[NOTE]"],
                      1: ["Playlist", "~[FOLDER]"],
                      2: ["Favorites", "~[HEART]"],
                      3: ["Info", "~[INFO]"],
                      4: ["Sync", "~[SYNC]"],
                      -1: ["Off", " "]}
        self.alert_pause = 2
        self.counter_modes = {0: "Time",
                              1: "Tracks"}
        self.counter_mode = 0

        self.txtOff = libLCDUI.text(20, 2)
        self.txtOff.format(libLCDUI.center)
        self.icoMode = libLCDUI.text(1,1)
        self.barVolume = libLCDUI.vertical_progress_bar(1,3,0,100)

        self.txtVolumeOverlay = libLCDUI.text(20,4)
        self.txtVolumeOverlay.format(libLCDUI.center)
        self.txtVolumeOverlay.write(["","Volume","",""])
        self.barVolumeLarge = libLCDUI.horizontal_progress_bar(16,1,0,100)
        self.txtVolumeValue = libLCDUI.text(2,1)

        self.txtNowPlaying = libLCDUI.text(18,3)
        self.txtCounter = libLCDUI.text(18, 1)
        self.txtCounter.format(libLCDUI.right)

        self.lstPlaylist = libLCDUI.list(19,4)
        self.barPlaylist = libLCDUI.horizontal_position_bar(18,1,0,10)

        self.lstFavorites = libLCDUI.list(19,4)

        self.lstTechnicalInfo = libLCDUI.list(19, 4)

        self.lstPlayers = libLCDUI.list(19,4)

        self.txtAlert = libLCDUI.text(18, 4)

        self.txtOff.hide()
        self.txtAlert.hide()
        self.barVolumeLarge.hide()
        self.txtVolumeOverlay.hide()
        self.txtVolumeValue.hide()

        self.ui.add_widget(self.txtOff, 1, 0)
        self.ui.add_widget(self.icoMode,0,0)
        self.ui.add_widget(self.barVolume,1,0)
        self.ui.add_widget(self.txtNowPlaying,0,2)
        self.ui.add_widget(self.lstPlaylist,0,1)
        self.ui.add_widget(self.barPlaylist,3,2)
        self.ui.add_widget(self.lstFavorites,0,1)
        self.ui.add_widget(self.lstTechnicalInfo, 0, 1)
        self.ui.add_widget(self.lstPlayers,0,1)
        self.ui.add_widget(self.txtCounter, 3, 2)
        self.ui.add_widget(self.txtVolumeOverlay,0,0)
        self.ui.add_widget(self.txtVolumeValue, 2, 0)
        self.ui.add_widget(self.barVolumeLarge, 2, 3)
        self.ui.add_widget(self.txtAlert,0,2)

        self.layouts = {0: [self.icoMode, self.barVolume, self.txtNowPlaying, self.txtCounter],
                        1: [self.icoMode, self.barVolume, self.lstPlaylist],
                        2: [self.icoMode, self.barVolume, self.lstFavorites],
                        3: [self.icoMode, self.barVolume, self.lstTechnicalInfo],
                        4: [self.icoMode, self.barVolume, self.lstPlayers],
                        -1: [self.txtOff]}
        self.colors  = {0: [LCD_red, LCD_green, LCD_blue],
                        1: [LCD_red, LCD_green, LCD_blue],
                        2: [LCD_red, LCD_green, LCD_blue],
                        3: [LCD_red, LCD_green, LCD_blue],
                        4: [LCD_red, LCD_green, LCD_blue],
                        -1: [LCD_off_red, LCD_off_green, LCD_off_blue]}
        self.change_mode_to(0)
        self.connect()

    def connect(self):
        self.txtAlert.write(["Connecting to", self.server_address])
        self.txtAlert.show()
        success = False
        while not(success):
            self.ui.redraw()
            try:
                self.server = pylms.server.Server(self.server_address)
                self.server.connect()
                success = True
            except:
                time.sleep(pauseBetweenRetries)
        self.txtAlert.write(["Registering", self.player_name])
        success = False
        while not(success):
            self.ui.redraw()
            try:
                self.player = self.server.get_player(self.player_name)
                if self.player is not None:
                    success = True
            except:
                time.sleep(pauseBetweenRetries)



        # Populate several lists. This is only done when reconnecting, so if a new player appears in the network,
        # this is not updated. Same is true for favorites.
        self.txtAlert.write("Getting list")
        self.all_players = self.server.get_players()
        self.lstPlayers.clear()
        for p in self.all_players:
            self.lstPlayers.add_item(p.get_name())

        self.all_favorites = self.server.get_favorites()
        self.lstFavorites.clear()
        for f in self.all_favorites:
            self.lstFavorites.add_item(f['name'])

        self.txtAlert.write("Connected")
        self.txtAlert.start_countdown(self.alert_pause)

        self.redraw()

    def is_connected(self):
        try:
            self.player.get_ip_address()
            return True
        except:
            return False

    def change_mode_to(self, mode):
        if mode in self.modes:
            self.mode = mode
            self.change_layout()

    def change_mode_by(self, step):
        self.mode += step
        if self.mode > max(self.modes):
            self.mode = 0
        if self.mode < 0:
            self.mode = max(self.modes)
        self.change_layout()

    def change_counter_mode(self):
        self.counter_mode += 1
        if self.counter_mode > max(self.counter_modes):
            self.counter_mode = 0

    def get_mode(self, by_name=False):
        if by_name:
            return self.modes[self.mode][0]
        else:
            return self.mode

    def switch_power(self, state=None):
        if state is None:
            self.player.set_power_state(not self.player.get_power_state())
        else:
            self.player.set_power_state = state
        self.power = self.player.get_power_state()
        self.change_layout()

    def change_volume(self, amount):
        if amount > 0:
            self.player.volume_up(amount)
        else:
            self.player.volume_down(-amount)
        #self.barVolumeLarge.start_countdown(1)
        #self.txtVolumeOverlay.start_countdown(1)
        #self.txtVolumeValue.start_countdown(1)

    def show_info(self, i):
        if i == 0:
            self.txtAlert.write(self.player.get_track_artist())
        elif i == 1:
            self.txtAlert.write(self.player.get_track_title())
        elif i == 2:
            self.txtAlert.write(self.player.get_track_album())
        elif i == 3:
            self.txtAlert.write(self.player.get_name())
        elif i == 4:
            self.txtAlert.write(self.player.get_ip_address())
        elif i == 5:
            self.txtAlert.write(self.player.get_mode())
        elif i == 6:
            self.txtAlert.write(self.server_address)

        self.txtAlert.start_countdown(3)

    def change_layout(self):
        self.ui.display.set_color(self.colors[self.mode][0], self.colors[self.mode][1], self.colors[self.mode][2])

        # Change the icon to the icon for the current mode:
        self.icoMode.write([self.modes[self.mode][1]])

        # Enable only widgets in the current layout and disable the rest:
        for widget in self.ui.list_widgets():
            if widget in self.layouts[self.mode]:
                widget.show()
            else:
                widget.hide()

        #Populate some lists
        if self.get_mode(by_name=True) == "Playlist":
            playlist = self.player.playlist_get_info()
            self.lstPlaylist.clear()
            for i in playlist:
                self.lstPlaylist.add_item(i['title'])
            self.barPlaylist.set_maximum_value(self.player.playlist_track_count())
            self.lstPlaylist.set_listindex(self.player.playlist_current_track_index()-1)

        if self.get_mode(by_name=True) == "Info":
            self.lstTechnicalInfo.clear()
            self.lstTechnicalInfo.add_item("Artist: "+self.player.get_track_artist())
            self.lstTechnicalInfo.add_item("Title : "+self.player.get_track_title())
            self.lstTechnicalInfo.add_item("Album : "+self.player.get_track_album())
            self.lstTechnicalInfo.add_item("Player: "+self.player.get_name())
            self.lstTechnicalInfo.add_item("IP    : "+self.player.get_ip_address())
            self.lstTechnicalInfo.add_item("Mode  : "+self.player.get_mode())
            self.lstTechnicalInfo.add_item("Server: "+self.server_address)

    def user_input(self, button, value):
        # This function  handles all user input (button presses and turns).
        if button == 9:
            if self.is_connected():
                self.player.set_power_state(not self.player.get_power_state())

        elif button == 1:
            if self.is_connected():
                self.change_mode_by(1)

        elif button == 2:
            if self.is_connected():
                if self.get_mode(by_name=True) == "Playlist":
                    self.player.playlist_play_index(self.lstPlaylist.get_selected())
                    self.change_mode_to(0)
                if self.get_mode(by_name=True) == "Favorites":
                    self.player.playlist_play(self.all_favorites[self.lstFavorites.get_selected()]['url'])
                    self.txtAlert.write("Selected %s" % self.all_favorites[self.lstFavorites.get_selected()]['name'])
                    self.change_mode_to(0)
                    self.txtAlert.start_countdown(self.alert_pause)
                if self.get_mode(by_name=True) == "Info":
                    self.show_info(self.lstTechnicalInfo.get_selected())
                if self.get_mode(by_name=True) == "Sync":
                    if self.player.is_synced():
                        self.player.unsync()
                        self.txtAlert.write("Unsynced player")
                    else:
                        self.all_players[self.lstPlayers.get_selected()].sync_to(self.player.get_ref())
                        self.txtAlert.write("Synced to %s" % self.all_players[self.lstPlayers.get_selected()].get_name())
                    self.change_mode_to(0)
                    self.txtAlert.start_countdown(self.alert_pause)

        elif button == 3:
            if self.is_connected():
                if self.get_mode(by_name=True) == "Now playing":
                    if self.is_connected():
                        self.change_volume(value)
                elif self.get_mode(by_name=True) == "Playlist":
                    if value > 0:
                        self.lstPlaylist.move_down()
                    else:
                        self.lstPlaylist.move_up()
                elif self.get_mode(by_name=True) == "Favorites":
                    if value > 0:
                        self.lstFavorites.move_down()
                    else:
                        self.lstFavorites.move_up()
                elif self.get_mode(by_name=True) == "Info":
                    if value > 0:
                        self.lstTechnicalInfo.move_down()
                    else:
                        self.lstTechnicalInfo.move_up()
                elif self.get_mode(by_name=True) == "Sync":
                    if value > 0:
                        self.lstPlayers.move_down()
                    else:
                        self.lstPlayers.move_up()

    def redraw(self):
        if not self.player.get_power_state():
            self.change_mode_to(-1)
        else:
            if self.get_mode(by_name=True) == "Off":
                self.change_mode_to(0)
                self.player.play()
        if self.is_connected():
            self.txtOff.write([self.player_name,self.player.get_ip_address()])
            self.txtNowPlaying.write("%s by %s" % (self.player.get_track_title(), self.player.get_track_artist()))
            self.barVolumeLarge.write(self.player.get_volume())
            self.barVolume.write(self.player.get_volume())
            self.txtVolumeValue.write(self.player.get_volume())
            self.barPlaylist.write(self.player.playlist_current_track_index())
            if self.counter_mode == 0:
                if self.player.get_track_duration() > 0:
                    self.txtCounter.write("~[LEFT]%s/%s~[RIGHT]" % (self.time_format(self.player.get_time_elapsed()), self.time_format(self.player.get_track_duration())))
                else:
                    self.txtCounter.write("~[LEFT]%s~[RIGHT]" % (self.time_format(self.player.get_time_elapsed())))
            elif self.counter_mode == 1:
                self.txtCounter.write("[%s of %s]" % (self.player.playlist_current_track_index(), self.player.playlist_track_count()))
                if self.player.get_track_duration() == 0:
                    self.txtCounter.write("stream")

        self.ui.redraw()

    def time_format(self, duration):
        if duration > 3600:
            return time.strftime("%-H:%M", time.gmtime(duration))
        else:
            return time.strftime("%M:%S", time.gmtime(duration))

    class Worker(threading.Thread):
        def __init__(self, display, server, player):
            threading.Thread.__init__(self)
            self.lock = threading.Lock()
            self.stopping = False
            self.interface = Interface(display, server, player)
            self.daemon = True
            self.delay = 0.001
            self.press = False

        def run(self):
            while not self.stopping:
                self.interface.redraw()
                time.sleep(self.delay)

        def stop(self):
            self.stopping = True