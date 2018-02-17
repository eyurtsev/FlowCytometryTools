import io
import json
import os
import webbrowser

import tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from matplotlib.backends.backend_webagg_core import (
    FigureManagerWebAgg, new_figure_manager_given_figure)
from matplotlib.figure import Figure

try:  # Old library
    import tkFileDialog as filedialog
except:
    # New style file dialog import
    from tkinter import filedialog

from FlowCytometryTools.gui import fc_widget


class MyApplication(tornado.web.Application):
    class MainPage(tornado.web.RequestHandler):
        """
        Serves the main HTML page.
        """

        def get(self):
            # Load HTML template
            path = os.path.realpath(__file__)
            path = os.path.split(path)[0]
            app_path = os.path.join(path, 'app_template.html')
            with open(app_path, 'r') as f:
                html_content = f.read()

            manager = self.application.manager
            ws_uri = "ws://{req.host}/".format(req=self.request)
            content = html_content % {
                "ws_uri": ws_uri, "fig_id": manager.num}
            self.write(content)

    class MplJs(tornado.web.RequestHandler):
        """
        Serves the generated matplotlib javascript file.  The content
        is dynamically generated based on which toolbar functions the
        user has defined.  Call `FigureManagerWebAgg` to get its
        content.
        """

        def get(self):
            self.set_header('Content-Type', 'application/javascript')
            js_content = FigureManagerWebAgg.get_javascript()

            self.write(js_content)

    class Download(tornado.web.RequestHandler):
        """
        Handles downloading of the figure in various file formats.
        """

        def get(self, fmt):
            manager = self.application.manager

            mimetypes = {
                'ps': 'application/postscript',
                'eps': 'application/postscript',
                'pdf': 'application/pdf',
                'svg': 'image/svg+xml',
                'png': 'image/png',
                'jpeg': 'image/jpeg',
                'tif': 'image/tiff',
                'emf': 'application/emf'
            }

            self.set_header('Content-Type', mimetypes.get(fmt, 'binary'))

            buff = io.BytesIO()
            manager.canvas.print_figure(buff, format=fmt)
            self.write(buff.getvalue())

    class WebSocket(tornado.websocket.WebSocketHandler):
        """
        A websocket for interactive communication between the plot in
        the browser and the server.

        In addition to the methods required by tornado, it is required to
        have two callback methods:

            - ``send_json(json_content)`` is called by matplotlib when
              it needs to send json to the browser.  `json_content` is
              a JSON tree (Python dictionary), and it is the responsibility
              of this implementation to encode it as a string to send over
              the socket.

            - ``send_binary(blob)`` is called to send binary image data
              to the browser.
        """
        supports_binary = True

        def open(self):
            # Register the websocket with the FigureManager.
            manager = self.application.manager
            manager.add_web_socket(self)
            if hasattr(self, 'set_nodelay'):
                self.set_nodelay(True)

        def on_close(self):
            # When the socket is closed, deregister the websocket with
            # the FigureManager.
            manager = self.application.manager
            manager.remove_web_socket(self)

        def on_message(self, message):
            # The 'supports_binary' message is relevant to the
            # websocket itself.  The other messages get passed along
            # to matplotlib as-is.

            # Every message has a "type" and a "figure_id".
            message = json.loads(message)
            if message['type'] == 'supports_binary':
                self.supports_binary = message['value']
            elif message['type'] == 'app_control':
                fc_manager = self.application.fc_manager

                if message['name'] == 'open_file':
                    filename = filedialog.askopenfilename(initialdir=os.path.curdir,
                                                          defaultextension='.fcs')
                    if len(filename) != 0:
                        fc_manager.load_fcs(filename)
                elif message['name'] == 'draw_poly_gate':
                    fc_manager.create_gate_widget('poly')
                elif message['name'] == 'draw_horizontal_gate':
                    fc_manager.create_gate_widget('horizontal threshold')
                elif message['name'] == 'draw_vertical_gate':
                    fc_manager.create_gate_widget('vertical threshold')
                elif message['name'] == 'delete_gate':
                    fc_manager.remove_active_gate()
                elif message['name'] == 'change_axis':
                    fc_manager.change_axis(message['axis_num'], message['value'])
                elif message['name'] == 'generate_code':
                    fc_manager.get_generation_code()
                elif message['name'] == 'quit':
                    if hasattr(self.application.stop_callback, '__call__'):
                        self.application.stop_callback()
            else:
                manager = self.application.manager
                manager.handle_json(message)

        def send_json(self, content):
            self.write_message(json.dumps(content))

        def send_binary(self, blob):
            if self.supports_binary:
                self.write_message(blob, binary=True)
            else:
                data_uri = "data:image/png;base64,{0}".format(
                    blob.encode('base64').replace('\n', ''))
                self.write_message(data_uri)

    def load_fcs(self, path):
        return self.fc_manager.load_fcs(path)

    def load_measurement(self, measurement):
        return self.fc_manager.load_measurement(measurement)

    def __init__(self, stop_callback=None):
        super(MyApplication, self).__init__([
            # Static files for the CSS and JS
            (r'/_static/(.*)',
             tornado.web.StaticFileHandler,
             {'path': FigureManagerWebAgg.get_static_file_path()}),

            # The page that contains all of the pieces
            ('/', self.MainPage),

            ('/mpl.js', self.MplJs),

            # Sends images and events to the browser, and receives
            # events from the browser
            ('/ws', self.WebSocket),

            # Handles the downloading (i.e., saving) of static images
            (r'/download.([a-z0-9.]+)', self.Download),
        ])

        figure = Figure()

        self.manager = new_figure_manager_given_figure(
            id(figure), figure)

        ax = figure.add_subplot(1, 1, 1)

        def callback(event):
            '''Sends event to front end'''
            event.info.pop('caller', None)  # HACK: popping caller b/c it's not JSONizable.
            self.manager._send_event(event.type, **event.info)

        self.fc_manager = fc_widget.FCGateManager(ax, callback_list=callback)
        self.stop_callback = stop_callback


class GUILauncher(object):
    """ Use this to launch the wx-based fdlow cytometry app """

    def __init__(self, filepath=None, measurement=None):
        if filepath is not None and measurement is not None:
            raise ValueError('You can only specify either filepath or measurement, but not both.')

        # Not sure if this is the appropriate way to deal with IOLoop
        # The question is what to do if launched from within ipython notebook, which is
        # already running a tornado server.
        self.ioloop_initiator = not tornado.ioloop.IOLoop.initialized()

        self.app = MyApplication(stop_callback=self.stop)

        if filepath is not None:
            self.app.load_fcs(filepath)
        if measurement is not None:
            self.app.load_measurement(measurement)

        self.http_server = tornado.httpserver.HTTPServer(self.app)

        port = 8080
        try:
            self.http_server.listen(port)
        except:
            msg = ('Could not open port {}. Please make sure sure you have no open tabs '
                   'using that port.'.format(port))
            print(msg)
            raise
        self.run()

    def run(self):
        url = r'http://127.0.0.1:8080/'
        print('The application should have opened a new tab '
              'in the webbrowser at address: {}'.format(url))
        webbrowser.open_new_tab(url)

        if self.ioloop_initiator:
            tornado.ioloop.IOLoop.current().start()

    def stop(self):
        self.http_server.stop()

        if self.ioloop_initiator:
            tornado.ioloop.IOLoop.current().stop()
