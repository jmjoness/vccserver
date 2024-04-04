#!/usr/bin/env python3.9

"""handle views"""
import json
import datetime
import time
import os
import serial
from serial.tools import list_ports
from netifaces import interfaces, ifaddresses, AF_INET
from flask import render_template, session, redirect, url_for, request, \
	make_response, jsonify

from . import main, logger

camPort = serial.Serial()
portList = list_ports.comports()
portNames = [p.name for p in portList]

print("\nPorts:")
for port in portNames:
	print(port)

print("\nIP Address:")
for ifaceName in interfaces():
	addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
	if 'No IP addr' not in addresses and '127.0.0.1' not in addresses:
		print(addresses[0])

def msgToString(msg):
	str = "".join('{:02X}'.format(x) for x in msg)
	return str

def send(msg):
	if not camPort.is_open:
		print("No COM port selected")
		return
	
	try:
		camPort.write(msg)
		print("write:", msgToString(msg))
		camPort.flush()

	except serial.SerialException as e:
		print("Verify that COM port has been set")
	except Exception as e: 
		print("failed to write", e)

def recv():
	if not camPort.is_open:
		print("No COM port selected")
		return

	resp = []
	try:
		done = False
		while not done:
			b = camPort.read(1)
			r = int.from_bytes(b, byteorder='little')
			resp.append(r)
			done = (r == 0xFF)

		print("receive:", msgToString(resp))

	except serial.SerialException as e:
		print("Verify that COM port has been set")
	except Exception as e: 
		print("failed to read", e)

	return resp

@main.route("/")
def index():
	print("print: index", flush=True)
	logger.info("logger: index")
	logger.debug("debug: index")
	return render_template('index.html')

@main.route("/getports")
def getports():
	print("getports()", portNames)
	return jsonify(success=True, ports=portNames), 200

@main.route("/checkport")
def checkport():
	if camPort.is_open:
		return jsonify(success=True), 200
	else:
		return jsonify(success=False), 400

@main.route('/start/<name>', methods=['GET'])
def start(name):
	try:
		print("start:", name)
		camPort.port = name
		camPort.open()
		addBcastList = [0x88, 0x30, 0x01, 0xFF]
		bAddBcast = bytes(addBcastList)
		send(bAddBcast)
		rcv = recv()
		if rcv != [0x88, 0x30, 0x02, 0xFF]:
			print("incorrect response", msgToString(rcv))

		return jsonify(success=True), 200

	except Exception as e: 
		print("failed to start", e)
		return jsonify(success=False), 400

@main.route('/stop', methods=['GET'])
def stop():
	try:
		camPort.close()
		camPort.name = ""

		return jsonify(success=True), 200

	except Exception as e: 
		print("failed to stop", e)
		return jsonify(success=False), 400
	
@main.route('/ptdrive/<id>/<dir>/<spd>', methods=['GET'])
def ptdrive(id, dir, spd):
	try:
		msg = [0x80, 0x01, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0xFF]
		iId = int(id)
		iSpd = int(spd)
		iSpd = min(iSpd, 17)
		msg[0] += iId
		print(id, dir, spd)
		msg[4] = iSpd
		msg[5] = iSpd
		msg[6] = 0x03
		msg[7] = 0x03

		if "l" in dir:
			msg[6] = 0x01
		elif "r" in dir:
			msg[6] = 0x02

		if "u" in dir:
			msg[7] = 0x01
		elif "d" in dir:
			msg[7] = 0x02
		
		pMsg = bytes(msg)
		send(pMsg)
		time.sleep(.02)
		resp = recv()
		resp = recv()

		msg[6] = 0x03
		msg[7] = 0x03
		pMsg = bytes(msg)
		send(pMsg)
		resp = recv()

		return jsonify(success=True), 200

	except Exception as e: 
		print("failed to pan/tilt camera", e)
		return jsonify(success=False), 400
	
@main.route('/ptcenter/<id>', methods=['GET'])
def ptcenter(id):
	try:
		msg = [0x80, 0x01, 0x06, 0x04, 0xFF]
		iId = int(id)
		msg[0] += iId
		
		pMsg = bytes(msg)
		send(pMsg)
		resp = recv()

		return jsonify(success=True), 200

	except Exception as e: 
		print("failed to center camera", e)
		return jsonify(success=False), 400
	
@main.route('/preset/<id>/<set>/<num>', methods=['GET'])
def preset(id, set, num):
	try:
		msg = [0x80, 0x01, 0x04, 0x3F, 0x01, 0x00, 0xFF]
		iId = int(id)
		msg[0] += iId
		if set != "set":
			msg[4] = 0x02
		iNum = int(num)
		msg[5] = iNum
		
		pMsg = bytes(msg)
		send(pMsg)
		resp = recv()

		return jsonify(success=True), 200

	except Exception as e: 
		print("failed to preset/recall camera", e)
		return jsonify(success=False), 400

@main.route('/zoom/<id>/<inout>/<spd>', methods=['GET'])
def zoom(id, inout, spd):
	try:
		msg = [0x80, 0x01, 0x04, 0x07, 0x00, 0xFF]
		iId = int(id)
		iSpd = int(spd)
		iSpd = min(iSpd, 7)
		msg[0] += iId
		if inout == "in":
			msg[4] = 0x20
			msg[4] += iSpd
		elif inout == "out":
			msg[4] = 0x30
			msg[4] += iSpd
		
		pMsg = bytes(msg)
		send(pMsg)
		time.sleep(.1)
		resp = recv()
		resp = recv()

		msg[4] = 0x00
		pMsg = bytes(msg)
		send(pMsg)
		resp = recv()

		return jsonify(success=True), 200

	except Exception as e: 
		print("failed to zoom camera", e)
		return jsonify(success=False), 400
