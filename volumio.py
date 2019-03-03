#coding=utf-8
from __future__ import print_function
class Volumio:
    def __init__(self, host="localhost", port=3000):

        from socketIO_client import SocketIO

        self._state = {}
        self._queue = list()
        self._radios = list()
        self._waiting = .1

        print("Opening {}:{} ".format(host, port), end='')
        self._sock = SocketIO(host, port)

        # Callbacks
        self._sock.on('connect', self._on_connect)
        self._sock.on('pushState', self._on_push_state)
        self._sock.on('pushBrowseLibrary', self._on_push_browse_library)
        self._sock.on('pushQueue', self._on_push_queue)

        while len(self._state)==0:
            print('.', end='')
            self._sock.wait(seconds=0.3)

        
    def _on_connect(self, *args):
        print(' Connected!')
        self.get_state()

    def _on_push_state(self, *args):
        print("State updated")
        self._state = args[0]

    def _on_push_browse_library(self, *args):
        radios_list = args[0]['navigation']['lists'][0]['items']
        self._radios = list()
        for radio in radios_list:
            self._radios.append({
                'title': radio['title'],
                'uri': radio['uri']
            })

    def _on_push_queue(self, *args):
        print("Fetching queue")
        self._queue = list()
        for music in args[0]:
            self._queue.append({
                "uri": music['uri'],
                "title": music.get('title', None),
                "name": music.get('name', None),
            })

    def _send(self, command, args=None, callback=None):
        self._sock.emit(command, args, callback)
        self._sock.wait_for_callbacks(seconds=self._waiting)


    def get_state(self):
        self._send('getState', callback=self._on_push_state)

    def get_radios(self):
        self._send('browseLibrary', {"uri": "radio/myWebRadio"}, self._on_push_browse_library)

    def get_queue(self):
        self._send('getQueue', callback=self._on_push_queue)

    def radios(self):
        self.get_radios()
        return self._radios

    def state(self):
        return self._state

    def status(self):
        return self._state["status"]

    def playing(self):
        return Volumio.get_name(self._state)

    def playing_uri(self):
        self.get_state()
        return self._state["uri"]

    def stop(self):
        self._send('stop')
        self._send('clearQueue')

    def queue(self):
        self.get_queue()
        return self._queue

    def volume(self):
        return self._state["volume"]

    def set_volume(self, volume):
        """
        Définit le volume de lecture
        :param volume: Volume souhaité [0-100]
        """
        assert isinstance(volume, int), ":volume: doit être un entier (type : {})".format(type(volume))
        assert 0 <= volume <= 100, ":volume: doit être compris entre 0 et 100 (valeur : {})".format(volume)
        self._send('volume', volume, callback=self._on_push_state)

    def play_radio(self, uri):
        """
        Joue immédiatement la radio dont l'URI est passée en paramètre
        :param uri: URI de la radio à jouer
        """

        # Méthode de force brute, on est obligé de vider la queue, et d'ajouter une musique,
        # Sinon elle s'ajoute à la fin de la queue.
        self._send('clearQueue')
        self._send('addPlay', {'status':'play', 'service':'webradio', 'uri':uri})

    @staticmethod
    def get_name(music_as_dict):
        """
        Permet d'extraire le nom (qui est soit le champ 'title' soit le champ 'name' d'une musique
        :param music_as_dict: le dictionnaire représentant la musique
        :return: le titre, ou le nom, ou bien None
        """
        title = music_as_dict.get("title", None)
        name = music_as_dict.get("name", None)
        return title if title is not None else name
