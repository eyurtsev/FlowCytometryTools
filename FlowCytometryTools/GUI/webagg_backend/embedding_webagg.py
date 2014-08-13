"""
This example demonstrates how to embed matplotlib WebAgg interactive
plotting in your own web application and framework.  It is not
necessary to do all this if you merely want to display a plot in a
browser or use matplotlib's built-in Tornado-based server "on the
side".

The framework being used must support web sockets.
"""

import io

try:
    import tornado
except ImportError:
    raise RuntimeError("This example requires tornado.")
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.websocket


from matplotlib.backends.backend_webagg_core import (
    FigureManagerWebAgg, new_figure_manager_given_figure)
from matplotlib.figure import Figure

import numpy as np
import json


from FlowCytometryTools.GUI import fc_widget
import os
import tkFileDialog

def create_figure():
    """
    Creates a simple example figure.
    """
    #fig = Figure()
    import pylab as pl
    fig = Figure()
    ax = fig.add_subplot(111)
    fc_manager = fc_widget.FCToolBar(ax)
    return fig, fc_manager

class MyApplication(tornado.web.Application):
    class MainPage(tornado.web.RequestHandler):
        """
        Serves the main HTML page.
        """
        def get(self):
            # Load HTML template
            with open('./app_template.html', 'r') as f:
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
                manager = self.application.fc_manager

                if message['name'] == 'open_file':
                    filename = tkFileDialog.askopenfilename(initialdir=os.path.curdir, defaultextension='.fcs')
                    if len(filename) != 0:
                        manager.load_fcs(filename)
                elif message['name'] == 'draw_poly_gate':
                    manager.create_gate_widget('poly')
                elif message['name'] == 'draw_horizontal_gate':
                    manager.create_gate_widget('horizontal threshold')
                elif message['name'] == 'draw_vertical_gate':
                    manager.create_gate_widget('vertical threshold')
                elif message['name'] == 'delete_gate':
                    manager.remove_active_gate()
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

    def __init__(self, figure, fc_manager):
        self.figure = figure
        self.fc_manager = fc_manager
        self.manager = new_figure_manager_given_figure(
            id(figure), figure)

        # Route callbacks from the widget directly to javascript
        #self.fc_manager.add_callback(lambda event : self.WebSocket.send_json(['hello']))
        def x(*args, **kwargs):
            print(args, kwargs)
        fc_manager.add_callback(x)

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


if __name__ == "__main__":
    figure, fc_manager = create_figure()
    application = MyApplication(figure, fc_manager)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)

    print("http://127.0.0.1:8080/")
    print("Press Ctrl+C to quit")

    tornado.ioloop.IOLoop.instance().start()
