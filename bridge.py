"""Local-only, bounded LEGO Education hardware adapter. Python 3.14+."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, threading, re

motor = None
busy = threading.Lock()
stop_requested = threading.Event()
COLORS = {name: 'LEGO_COLOR_' + name for name in ('BLUE','RED','GREEN','PURPLE','YELLOW','ORANGE','AZURE','MAGENTA')}
ORIGIN = 'http://localhost:8765'

def halt():
    if motor is not None and getattr(motor, 'connected', False):
        motor.movement_stop()

def run_program(commands):
    import legoeducation as le
    if not motor or not motor.connected:
        raise RuntimeError('Connect the Double Motor first')
    if not isinstance(commands, list) or len(commands) > 20:
        raise ValueError('Program must contain at most 20 actions')
    for cmd in commands:
        if stop_requested.is_set():
            break
        if not isinstance(cmd, dict):
            raise ValueError('Invalid command')
        kind = cmd.get('type')
        if kind == 'drive':
            deg = int(cmd['deg']); speed = int(cmd['speed'])
            if not 1 <= deg <= 360 or not 10 <= speed <= 60 or cmd.get('dir') not in ('forward','backward'):
                raise ValueError('Drive exceeds safety limits')
            direction = le.MOVEMENT_MOVE_DIRECTION_FORWARD if cmd['dir'] == 'forward' else le.MOVEMENT_MOVE_DIRECTION_BACKWARD
            motor.movement_move_for_degrees(deg, direction=direction, speed=speed)
        elif kind == 'turn':
            angle = float(cmd['angle'])
            if not -180 <= angle <= 180:
                raise ValueError('Turn exceeds safety limits')
            if angle:
                direction = le.MOVEMENT_TURN_DIRECTION_RIGHT if angle > 0 else le.MOVEMENT_TURN_DIRECTION_LEFT
                motor.movement_turn_for_degrees(degrees=abs(angle), direction=direction)
        else:
            raise ValueError('Unsupported hardware action: ' + str(kind))
    halt()

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data):
        payload = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', ORIGIN)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
    def do_OPTIONS(self):
        if self.headers.get('Origin') != ORIGIN: return self.reply(403, {'error':'Origin denied'})
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    def do_GET(self):
        if self.path == '/status': self.reply(200, {'connected':bool(motor and motor.connected),'busy':busy.locked()})
        else: self.reply(404, {'error':'Not found'})
    def do_POST(self):
        global motor
        if self.headers.get('Origin') != ORIGIN: return self.reply(403, {'error':'Origin denied'})
        try:
            size = int(self.headers.get('Content-Length','0'))
            if not 0 < size <= 8192: return self.reply(413, {'error':'Invalid request size'})
            data = json.loads(self.rfile.read(size))
            if self.path == '/stop':
                stop_requested.set()
                # Do not block on an in-flight BLE call; it may be synchronous.
                try: halt()
                except Exception: pass
                return self.reply(200, {'ok':True,'message':'Stop requested; BLE stop is not guaranteed'})
            if not busy.acquire(blocking=False): return self.reply(409, {'error':'Hardware busy'})
            try:
                if self.path == '/connect':
                    import legoeducation as le
                    color = str(data.get('color','')).upper()
                    serial = str(data.get('serial',''))
                    if color not in COLORS or not re.fullmatch(r'\d{4}', serial):
                        raise ValueError('Select a colour and four-digit serial')
                    if motor and motor.connected: halt(); motor.disconnect()
                    motor = le.DoubleMotor()
                    motor.connect(card_color=getattr(le, COLORS[color]), card_serial=serial)
                    if not motor.connected: raise RuntimeError('Motor connection failed')
                elif self.path == '/execute':
                    stop_requested.clear()
                    run_program(data.get('commands'))
                elif self.path == '/disconnect':
                    stop_requested.set()
                    if motor and motor.connected: halt(); motor.disconnect()
                else: return self.reply(404, {'error':'Unknown action'})
                return self.reply(200, {'ok':True,'connected':bool(motor and motor.connected)})
            finally:
                busy.release()
        except Exception as exc:
            try: halt()
            except Exception: pass
            return self.reply(400, {'error':str(exc)})

if __name__ == '__main__':
    print('Hardware bridge listening ONLY on http://127.0.0.1:8766')
    ThreadingHTTPServer(('127.0.0.1', 8766), Handler).serve_forever()
