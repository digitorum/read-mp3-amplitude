#!/usr/bin/python
# -*- coding: utf-8 -*-
import os;
import sys;
import pygst;
import gst;
import gobject;
import re;

# пока true - пытаемся получить сообщения от gst
doStuff = True;

# результат с максимальными значениями амплидуд в интервале
amplitude = []

# колбэк для обработки сообщения от gst
def onMessage(bus, message):
	global doStuff
	
	if message.type == gst.MESSAGE_EOS or message.type == gst.MESSAGE_ERROR:
		doStuff = False
		return
	if message.src is not level:
		return
	if not message.structure.has_key("peak"):
		return
	amplitude.append(message.structure["peak"][0])

# нормализация результата
def normalize(amplitude):
	if len(amplitude) == 0:
		return [];
	minval = min(amplitude)
	# хорошая идея с http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good-plugins/html/gst-plugins-good-plugins-level.html
	return  [(10 ** ((x - minval) / 20)) for x in amplitude]



# инициализируем pipeline
gobject.threads_init()
if re.match("^https?", sys.argv[1]):
	method="souphttpsrc"
	filename=sys.argv[1]
else:
	method="filesrc"
	filename=os.path.realpath(sys.argv[1])
pipeline = gst.parse_launch(
	(
		'{0} location={1} '
		'! decodebin '
		'! audioconvert '
		'! audio/x-raw-int,channels=1,rate=44100 '
		'! level name="level" interval=100000000 ' # 1000000000 = 1 second
		'! fakesink'
		.format(method, filename)
	)
)
level = pipeline.get_by_name("level")
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect('message', onMessage)
pipeline.set_state(gst.STATE_PLAYING)
ctx=gobject.gobject.main_context_default()
while ctx and doStuff:
	ctx.iteration()
pipeline.set_state(gst.STATE_NULL)
print normalize(amplitude)























