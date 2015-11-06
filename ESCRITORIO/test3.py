__author__ = 'USUARIO'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

maphtml = '''
<!DOCTYPE html>
<html>
  <head>
    <style>
      html, body, #map-canvas {
        height: 100%;
        margin: 0px;
        padding: 0px
      }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false&libraries=drawing"></script>
    <script>
      function initialize() {
        var mapOptions = {
          center: new google.maps.LatLng(37.5, -122.2),
          zoom: 20,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

        var drawingManager = new google.maps.drawing.DrawingManager({
          drawingMode: google.maps.drawing.OverlayType.POLYGON,
          drawingControl: true,
          drawingControlOptions: {
            position: google.maps.ControlPosition.TOP_CENTER,
            drawingModes: [google.maps.drawing.OverlayType.POLYGON]
          },
          polygonOptions: {editable: true, draggable: true},
        });
        drawingManager.setMap(map);

        var thePolygon = null;

        google.maps.event.addListener(drawingManager, 'polygoncomplete', function (polygon) {
          if (thePolygon)
            thePolygon.setMap(null);
          thePolygon = polygon;
          polygon.getPath().forEach(function (xy, i) {
            self.polygoncomplete(xy.lat(), xy.lng(), i);
          });
        });
      }

      google.maps.event.addDomListener(window, 'load', initialize);

    </script>
  </head>
  <body>
    <div id="map-canvas"></div>
  </body>
</html>
'''

class Browser(QApplication):
    def __init__(self):
        QApplication.__init__(self, [])
        self.window = QWidget()
        self.window.setWindowTitle("Google Google Maps Maps");

        self.web = QWebView(self.window)
        self.web.setMinimumSize(800,800)
        self.web.page().mainFrame().addToJavaScriptWindowObject('self', self)
        self.web.setHtml(maphtml)

        self.text = QTextEdit(self.window)

        self.layout = QVBoxLayout(self.window)
        self.layout.addWidget(self.web)
        self.layout.addWidget(self.text)

        self.window.show()
        self.exec_()

    @pyqtSlot(float, float, int)
    def polygoncomplete(self, lat, lng, i):
        if i == 0:
            self.text.clear()
        self.text.append("Point #{} ({}, {})".format(i, lat, lng))

Browser()