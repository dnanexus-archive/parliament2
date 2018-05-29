
(function () {
'use strict';

var $ = jQuery;

var name = 'SVGScroller';


function Scrollbar(scrollpanel, $host, options) {
    var self = this;

    self.settings = $.extend({}, {"vertical": true, "endSpace":10}, options || {});    
    self.orientation = self.settings.vertical ? "vert" : "horiz";
    self.$host = $host;

    self.$scrollbar = $('<div class="scrollbar ' + self.orientation + '"/>');
    self.$thumb = $('<div class="thumb '  + self.orientation + '"/>').appendTo(self.$scrollbar);

    self.$host.append(self.$scrollbar);
    self.mouseOffset = 0;
    self.scrollProportion = 0.5;
    self.scrollmax = 0;
    self.pageSize = 0;

    self.active = true;

    self.resize = function(size, viewable, viewsize) {
        self.scrollmax = viewsize - viewable;
        self.pageSize = viewable / viewsize;

        self.thumbsize = self.pageSize * self.scrollbarSize;
        self.thumbsize = Math.max(self.thumbsize, 10);

        if (self.settings.vertical) {
            self.scrollbarSize = size - self.settings.endSpace;
            self.$scrollbar.height(self.scrollbarSize);
            self.$thumb.height(Math.min(self.scrollbarSize, self.thumbsize));
        } else {
            self.scrollbarSize = size - self.settings.endSpace;
            self.$scrollbar.width(self.scrollbarSize);
            self.$thumb.width(Math.min(self.scrollbarSize, self.thumbsize));
        }

        if (self.pageSize >= 1.0 ) {
            // self.$scrollbar.fadeTo(50, 0.8);
            self.$thumb.fadeTo(50, 0.0);
            self.active = false;
        } else {
            self.active = true;
            // self.$scrollbar.fadeTo(50, 1);
            self.$thumb.fadeTo(50, 1);
            self.scrollTo(self.scrollProportion);
        }
    }

    self.scrollTo = function(newproportion) {
        if (!self.active) {
            return;
        }

        if (newproportion < 0) {
            newproportion = 0;
        } else if (newproportion > 1.0) {
            newproportion = 1.0;
        }

        self.scrollProportion = newproportion;
        var scrollBarPosition = (self.scrollbarSize - self.thumbsize) * self.scrollProportion;

        if (self.settings.vertical) {
            self.$thumb.css({"top": scrollBarPosition});
        } else {
            self.$thumb.css({"left": scrollBarPosition});
        }

        scrollpanel.scroll();
    }

    self.scrollBy = function(distance) {
        // convert screen coordinates to proportion
        var proportionalDistance = self.coordToProportion(distance);
        self.scrollTo(self.scrollProportion+proportionalDistance);
    }

    self.page = function(pages) {
        if ((!self.active) || (pages > 0 & self.scrollProportion == 1.0) || (pages < 0 & self.scrollProportion == 0.0)){
            return false;
        } else {
            self.scrollTo(self.scrollProportion + pages*self.pageSize);
            return true;
        }
    }

    self.coordToProportion = function(coord) {
        var proportion = coord / (self.scrollbarSize-self.thumbsize);
        return proportion;
    }

    self.onMouseDrag = function(event) {
        if (!self.active){
            return;
        }

        var clickFrac;
        if (self.settings.vertical) {
            clickFrac = self.coordToProportion(event.pageY - self.$scrollbar.offset().top - self.mouseOffset);
        } else {
            clickFrac = self.coordToProportion(event.pageX - self.$scrollbar.offset().left - self.mouseOffset);
        }

        self.scrollTo(clickFrac);

        event.preventDefault();
        event.stopPropagation();
    }


    self.$thumb.on("mousedown", function(event) {
        if (!self.active){
            return;
        }

        if (self.settings.vertical) {
            self.mouseOffset = event.pageY - self.$thumb.offset().top;
        } else {
            self.mouseOffset = event.pageX - self.$thumb.offset().left;
        }

        self.$thumb.addClass('active');

        $(window)
            .on('mousemove', self.onMouseDrag)
            .one('mouseup', function (event) {
                self.$thumb.removeClass('active');
                $(window).off('mousemove', self.onMouseDrag);
            });

        event.preventDefault();
        event.stopPropagation();
    })

    self.$scrollbar.on("mousedown", function(event) {
        if (!self.active){
            return;
        }

        if (event.altKey){
            // jump to clicked position
            var clickFrac;
            if (self.settings.vertical) {
                clickFrac = (event.pageY - self.$scrollbar.offset().top - self.thumbsize/2.0) / self.scrollbarSize;
            } else {
                clickFrac = (event.pageX - self.$scrollbar.offset().left - self.thumbsize/2.0) / self.scrollbarSize;
            }
            self.scrollTo(clickFrac * self.scrollbarSize);
        } else {
            // scroll a page in the direction of the click
            var direction = 1;
            if (self.settings.vertical) {
                if (event.pageY < self.$thumb.offset().top){
                    direction = -1;
                }
            } else {
                if (event.pageX < self.$thumb.offset().left){
                    direction = -1;
                }
            }
            self.page(direction);
        }
    })
}

function ScrollPanel(element, options, svg_tags) {
    var self = this;

    svg_tags = typeof svg_tags !== 'undefined' ? svg_tags : "";
    self.$element = $(element);
    self.$views = self.$element.find(svg_tags+" .one_svg")
    self.nviews = self.$views.length;

    self.xmin = 1e100;
    self.xmax = 0;

    self.ymin = 1e100;
    self.ymax = 0;

    self.axisHeight = 75;
    self.annoHeight = 0;

    self.yviewsizes = [];

    self.containerwidth = self.$element.width();
    self.containerheight = self.$element.height();

    self.xscrollbar = new Scrollbar(self, self.$element, {"vertical":false});
    self.yscrollbars = [];

    self.yviewables = [];
    self.types = []
    self.bboxes = []

    self.$element.find(".zoomin").on("mouseup", function(){
        self.doZoom(1.25);
    });
    self.$element.find(".zoomout").on("mouseup", function(){
        self.doZoom(0.80);
    });

    self.$views.each(function(i){
        var newyscrollbar = new Scrollbar(self, $(this), {"vertical":true, "endSpace":0});
        self.yscrollbars.push(newyscrollbar);

        var bbox = $(this).find(".svg_viewport")[0].getBBox();
        self.bboxes.push(bbox);

        self.xmin = Math.min(self.xmin, bbox.x);
        self.xmax = Math.max(self.xmax, bbox.x+bbox.width);

        self.yviewsizes.push(bbox.height + 550);

        $(this).width("100%");
        // $(this).height(100.0/self.nviews+"%");
        $(this).height("calc("+100.0/(self.nviews-1)+"% - "+((10 + self.axisHeight + self.annoHeight +(self.nviews-2)*2.0)/(self.nviews-1))+"px)");

        if ($(this).hasClass("axis")) {
            self.types.push("axis");
            $(this).height(self.axisHeight+"px");
            self.yviewsizes[i] = bbox.height;
            newyscrollbar.scrollProportion = 0.0; // because the scrollbar is hidden we need to make sure we're scrolled to the correct position
        } else if ($(this).hasClass("anno")) {
            newyscrollbar.scrollProportion = 0.0; // because the scrollbar is hidden we need to make sure we're scrolled to the correct position
            self.types.push("anno");
            self.annoHeight += 100;
        } else {
            self.ymin = Math.min(self.ymin, bbox.y);
            self.ymax = Math.max(self.ymax, bbox.y+bbox.height);
            
            self.types.push("sample");
        }

        self.yviewables.push(0);
    })

    self.xzoom = self.containerwidth / (self.xmax-self.xmin);
    self.yzooms = self.$views.map(function(){return self.xzoom;});


    self.unscale = function() {
        self.$element.find(".axis svg text, .anno svg text").each(function(i, curElement) {
            var $curElement = $(curElement);
            var a = 1 / self.xzoom;
            var e = ($curElement.attr("x")-$curElement.attr("x")*a)
            var matrix = "matrix("+a+" 0 0 1 "+e+" 0)";
            $curElement.attr("transform", matrix);
        });

        self.$element.find(".axis svg .scaleArrow").each(function(i, curElement) {
            var $curElement = $(curElement);
            var a = 1 / self.xzoom;
            var e = ($curElement.attr("xcenter")-$curElement.attr("xcenter")*a)
            var matrix = "matrix("+a+" 0 0 1 "+e+" 0)";
            $curElement.attr("transform", matrix);
        });
    }

    self.zoom = function() {
        self.xviewable = self.containerwidth / self.xzoom;
        for (var i=0; i < self.yviewables.length; i++) {
            self.yviewables[i] = self.containerheight / self.yzooms[i] / self.nviews;
            if (self.types[i] == "axis") {
                self.yviewables[i] = self.axisHeight;
            } else if (self.types[i] == "anno") {
                self.yviewables[i] = 100;
            }
        }
    }

    self.doZoom = function(zoomFactor) {
        self.xzoom *= zoomFactor;
        for (var i=0; i < self.yzooms.length; i++){
            self.yzooms[i] *= zoomFactor;
        }

        self.update();
    }

    $( window ).resize(function() {
        self.update();
    });

    self.scroll = function() {
        var xscroll = ((self.xmax-self.xmin) - self.xviewable) * (self.xscrollbar.scrollProportion) + self.xmin;
        if (self.xviewable > (self.xmax-self.xmin)) {
            xscroll = ((self.xmax-self.xmin) - self.xviewable) / 2.0;
        }

        self.$views.each(function(i, view){
            var ymin = self.ymin;
            var ymax = self.ymax;

            if (self.types[i] == "anno" || self.types[i] == "axis") {
                ymin = 0;
                ymax = self.bboxes[i].height;
            }

            var yscroll = ((ymax - ymin) - self.yviewables[i]) * (self.yscrollbars[i].scrollProportion);

            if (self.yviewables[i] > (ymax-ymin)) {
                yscroll = ((ymax-ymin) - self.yviewables[i]) / 2.0;
            }
            var viewBox = [xscroll, yscroll, self.xviewable, self.yviewables[i]];

            $(this).find("svg")[0].setAttribute("viewBox", viewBox.join(" "));
        })
    }

    self.scrollToTop = function() {
        self.yscrollbars.forEach(function(scrollbar){
            scrollbar.scrollTo(0.0);
        });
    }
    self.scrollToBottom = function() {
        self.yscrollbars.forEach(function(scrollbar){
            scrollbar.scrollTo(1.0);
        });
    }

    self.moveView = function(deltax, deltay){
        self.xscrollbar.scrollBy(deltax);
        self.yscrollbars.forEach(function(scrollbar, i){
            scrollbar.scrollBy(deltay);
        });
        self.update();
    }

    self.update = function() {
        self.zoom();
        self.xscrollbar.resize($(self.$views[0]).width(), self.xviewable, self.xmax-self.xmin);

        self.yscrollbars.forEach(function(scrollbar, i){
            if (self.types[i] == "sample") {
                scrollbar.resize($(self.$views[i]).height(), self.yviewables[i], self.ymax-self.ymin); //self.yviewsizes[i]);
            } else if (self.types[i] == "anno") {
                scrollbar.resize($(self.$views[i]).height(), self.yviewables[i], self.bboxes[i].height); //self.yviewsizes[i]);
            } else if (self.types[i] == "axis") {
                scrollbar.resize($(self.$views[i]).height(), self.axisHeight, self.axisHeight);
            }
        });
        self.scroll();
        self.unscale();
    }


    self.$element.on("mousedown", function(mouseDownEvent){
        var scrollStartX = mouseDownEvent.pageX;
        var scrollStartY = mouseDownEvent.pageY;

        var onMouseDrag = function(dragevent) {
            self.moveView(scrollStartX - dragevent.pageX, scrollStartY - dragevent.pageY);

            scrollStartX = dragevent.pageX;
            scrollStartY = dragevent.pageY;

            dragevent.preventDefault();
            dragevent.stopPropagation();
        }

        $(window)
            .on('mousemove', onMouseDrag)
            .one('mouseup', function (event) {
                $(window).off('mousemove', onMouseDrag);
            });

        mouseDownEvent.preventDefault();
        mouseDownEvent.stopPropagation();
    });

    self.$element.on("mousewheel", function(event){
        var didScroll = false;

        if (event.altKey){
            var zoomFactor;
            zoomFactor = event.deltaY > 0 ? Math.pow(1.25, Math.min(3,event.deltaY)) : Math.pow(0.8, -(Math.max(-3, event.deltaY)));
            self.doZoom(zoomFactor);
            didScroll = true;
        } else {
            if (event.deltaX != 0) {
                didScroll |= self.xscrollbar.page(event.deltaX*0.03);
            }
            if (event.deltaY != 0) {
                for (var i=0; i < self.yscrollbars.length; i++) {
                    didScroll |= self.yscrollbars[i].page(-event.deltaY*0.03);
                }
            }
        }

        if (didScroll){
            event.preventDefault();
            event.stopPropagation();
        }
    });
    // Initial update.
    self.update();
}

// Register the plug in
// --------------------
$.fn[name] = function (options, options2) {
    return this.each(function () {
        var $this = $(this);
        var scrollpanel = $this.data(name);

        if (!scrollpanel) {
            scrollpanel = new ScrollPanel(this, options);
            scrollpanel.update();
            scrollpanel.scrollToTop();
            $this.data(name, scrollpanel);
        }

        if (options === 'update') {
            scrollpanel.update(options2);
        }
    });
};

}());