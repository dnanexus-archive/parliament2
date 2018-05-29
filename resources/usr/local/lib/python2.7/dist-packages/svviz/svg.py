def _arrowhead_marker():
    return """<marker id="arrowhead"
      viewBox="0 0 10 10" refX="10" refY="5" 
      markerUnits="strokeWidth"
      markerWidth="4" markerHeight="3"
      orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" />
    </marker>"""


def _addOptions(**kwdargs):
    options = []
    for key, arg in kwdargs.items():
        if arg is not None and arg != "":
            options.append("""{key}="{arg}" """.format(key=key, arg=arg))
    return " ".join(options)


class Shape(object):
    pass

class Text(Shape):
    def __init__(self, x, y, text, size=10, anchor="middle", fill="", family="Helvetica", **kwdargs):
        super(Text, self).__init__()
        self.x = x
        self.y = y
        self.text = text
        self.size = size
        self.anchor = anchor
        self.fill = fill
        self.family = family
        self.more = kwdargs

    def render(self, parent):
        self.more["font-family"] = self.family
        more = _addOptions(fill=self.fill, **self.more)
        return """<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" {more}>{text}</text>""".format(x=self.x, y=parent.yy(self.y), 
            size=self.size, anchor=self.anchor, more=more, text=self.text)

class Rect(Shape):
    def __init__(self, x, y, width, height, stroke="", fill="", **kwdargs):
        super(Rect, self).__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.stroke = stroke
        self.fill = fill
        self.more = kwdargs

    def render(self, parent):
        more = _addOptions(stroke=self.stroke, fill=self.fill, **self.more)
        return """<rect x="{x}" y="{y}" width="{w}" height="{h}" {more}/>""".format(x=self.x, y=parent.yy(self.y), 
                                                                                    w=self.width, h=self.height, more=more)

class Line(Shape):
    def __init__(self, x1, y1, x2, y2, stroke="", fill="", arrowhead=None, **kwdargs):
        super(Line, self).__init__()
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.stroke = stroke
        self.fill = fill
        self.more = kwdargs

        assert arrowhead is None

    def render(self, parent):
        more = _addOptions(stroke=self.stroke, fill=self.fill, **self.more)

        return """<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" {more} />""".format(x1=self.x1, x2=self.x2, 
                                                                                    y1=parent.yy(self.y1), y2=parent.yy(self.y2), 
                                                                                    more=more)

class LineWithArrows(Line):
    def __init__(self, x1, y1, x2, y2, stroke="", fill="", n=5, direction="right", arrowKwdArgs=None, **kwdargs):
        super(LineWithArrows, self).__init__(x1, y1, x2, y2, stroke, fill, **kwdargs)
        self.n = n
        self.direction = direction
        self.arrowKwdArgs = arrowKwdArgs

    def render(self, parent):
        rendering = []
        rendering.append(Line(self.x1, self.y1, self.x2, self.y2, self.stroke, self.fill, **self.more).render(parent))
        if self.arrowKwdArgs is None: self.arrowKwdArgs = {}

        for i in range(1, self.n+1):
            x_arrow = self.x1+float(self.x2-self.x1)*i/self.n
            y_arrow = parent.yy(self.y1+float(self.y2-self.y1)*i/self.n)
            rendering.append(Arrow(x_arrow, y_arrow, self.direction, 
                color=self.stroke, scale=self.more.get("stroke-width", 1), **self.arrowKwdArgs).render(parent))
        return "\n".join(rendering)

class Arrow(Shape):
    def __init__(self, x, y, direction, color="black", scale=1.0, **kwdargs):
        super(Arrow, self).__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.scale = scale
        self.more = kwdargs

    def render(self, parent):
        more = _addOptions(**self.more)

        if self.direction == "right":
            a = """<path d="M {x0} {y0} L {x1} {y1} L {x2} {y2} z" fill="{color}" xcenter="{xcenter}" {more}/>""".format(
                x0=(self.x-10*self.scale), y0=(self.y-5*self.scale), 
                x1=(self.x), y1=self.y, 
                x2=(self.x-10*self.scale), y2=(self.y+5*self.scale),
                color=self.color,
                xcenter=self.x,
                more=more)
        elif self.direction == "left":
            a = """<path d="M {x0} {y0} L {x1} {y1} L {x2} {y2} z" fill="{color}" xcenter="{xcenter}" {more}/>""".format(
                x0=(self.x+10*self.scale), y0=(self.y-5*self.scale), 
                x1=(self.x), y1=self.y, 
                x2=(self.x+10*self.scale), y2=(self.y+5*self.scale),
                color=self.color,
                xcenter=self.x,
                more=more)
        return a



class SVG(object):
    def __init__(self, width, height, headerExtras="", markers=None, yrelto="bottom"):
        self.width = width
        self.height = height

        self.svg = []
        self.footer = ["""</g></svg>"""]
        self.headerExtras = headerExtras
        if markers is None:
            markers = {}
        self.markers = markers
        self.yrelto = yrelto

    def yy(self, iny):
        """ convert y coordinates to relative coordinates -- either relative to the top or bottom """
        if self.yrelto == "bottom":
            return self.height - iny
        else:
            return iny

    def getDefaultZIndex(self, zindex):
        """ allows insertion at the beginning of the svg list (ie before all the other items, therfore below them) """
        if zindex is None:
            zindex = len(self.svg)
        return zindex

    def header(self):
        header = []
        # """<?xml version="1.0" encoding="utf-8" ?>"""
        header.append("""<svg baseProfile="full" version="1.1" """
            """xmlns="http://www.w3.org/2000/svg" {extras} """
            """xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink"><defs>{markers}</defs>""".format(extras=self.headerExtras,
                markers="\n".join(list(self.markers.values()))))

        header.append("<g class=\"svg_viewport\">")
        return header

    def __str__(self):
        return self.asString()

    def asString(self, headerSet=None):
        oldHeaderExtras = self.headerExtras

        if headerSet is None:
            self.headerExtras += """viewBox="0 0 {w} {h}" """.format(w=self.width, h=self.height)
            header = self.header()
        elif headerSet == "export":
            self.headerExtras = ""
            header = self.header()
        elif headerSet == "web":
            xmlHeader = """<?xml version="1.0" encoding="utf-8" ?>"""
            self.headerExtras += """preserveAspectRatio="none" height="100%" width="100%" """
            header = [xmlHeader] + self.header()

        self.headerExtras = oldHeaderExtras

        return "\n".join(header + self.svg + self.footer)

    def write(self, path, headerSet=None):
        output = open(path, "w")
        output.write(self.asString(headerSet))



    def line(self, x1, y1, x2, y2, stroke="", fill="", arrowhead=None, **kwdargs):
        self.svg.append(Line(x1, y1, x2, y2, stroke=stroke, fill=fill, arrowhead=arrowhead, **kwdargs).render(self))

    def arrow(self, x, y, direction, color="black", scale=1.0, **kwdargs):
        self.svg.append(Arrow(x, y, direction, color, scale, **kwdargs).render(self))

    def lineWithInternalArrows(self, x1, y1, x2, y2, stroke="", fill="", n=5, direction="right", arrowKwdArgs=None, **kwdargs):
        self.svg.append(LineWithArrows(x1, y1, x2, y2, stroke, fill, n, direction, arrowKwdArgs, **kwdargs).render(self))

    def rect(self, x, y, width, height, stroke="", fill="", zindex=None, **kwdargs):
        zindex = self.getDefaultZIndex(zindex)
        self.svg.insert(zindex, Rect(x, y, width, height, stroke, fill, **kwdargs).render(self))

    def text(self, x, y, text, size=10, anchor="middle", fill="", family="Helvetica", **kwdargs):
        self.svg.append(Text(x, y, text, size, anchor, fill, family, **kwdargs).render(self))




