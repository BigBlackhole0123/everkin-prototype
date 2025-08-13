
import math, time, threading
from flask_socketio import SocketIO

_SIM_THREADS = {}
_STOP_FLAGS = {}

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dlambda = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R*c

def _heading(lat1, lon1, lat2, lon2):
    y = math.sin(math.radians(lon2-lon1)) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1))*math.sin(math.radians(lat2)) - math.sin(math.radians(lat1))*math.cos(math.radians(lat2))*math.cos(math.radians(lon2-lon1))
    brng = math.degrees(math.atan2(y,x))
    return (brng + 360) % 360

def _interpolate(lat1, lon1, lat2, lon2, steps):
    for i in range(steps+1):
        t = i/steps
        yield lat1 + (lat2-lat1)*t, lon1 + (lon2-lon1)*t

def _sim_thread(socketio: SocketIO, booking_id, start, end, room):
    speed_mps = 8.0  # ~28.8 km/h realistic city speed
    total_dist = _haversine(start[0], start[1], end[0], end[1])
    duration = max(10, int(total_dist / speed_mps))
    steps = min(600, max(60, duration))  # 1 update/sec approx
    prev = start
    for lat, lng in _interpolate(start[0], start[1], end[0], end[1], steps):
        if _STOP_FLAGS.get(booking_id):
            break
        dist_remain = _haversine(lat, lng, end[0], end[1])
        eta_sec = int(dist_remain / speed_mps)
        head = _heading(prev[0], prev[1], lat, lng)
        socketio.emit('position', {
            'booking_id': booking_id,
            'lat': lat, 'lng': lng,
            'speed_mps': speed_mps,
            'heading_deg': head,
            'eta_sec': eta_sec
        }, room=room, namespace='/tracking')
        prev = (lat, lng)
        time.sleep(1.0)
    socketio.emit('complete', {'booking_id': booking_id}, room=room, namespace='/tracking')
    _SIM_THREADS.pop(booking_id, None)
    _STOP_FLAGS.pop(booking_id, None)

def start_simulation_for_booking(socketio: SocketIO, booking_id, start_lat, start_lng, end_lat, end_lng):
    if booking_id in _SIM_THREADS:
        return False
    room = f"booking_{booking_id}"
    _STOP_FLAGS[booking_id] = False
    th = threading.Thread(target=_sim_thread, args=(socketio, booking_id, (start_lat, start_lng), (end_lat, end_lng), room), daemon=True)
    _SIM_THREADS[booking_id] = th
    th.start()
    return True

def stop_simulation_for_booking(booking_id):
    if booking_id in _SIM_THREADS:
        _STOP_FLAGS[booking_id] = True
        return True
    return False

def is_sim_running(booking_id):
    return booking_id in _SIM_THREADS
