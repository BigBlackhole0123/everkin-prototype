import math, time, threading

_active = {}
_active_lock = threading.Lock()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    phi1 = math.radians(lat1); phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1); dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a)); return R*c

def _runner(socketio, booking_id, start_lat, start_lng, end_lat, end_lng):
    speed_mps = 8.0
    total = max(1.0, haversine(start_lat, start_lng, end_lat, end_lng))
    steps = int(total / (speed_mps * 1.0)); steps = max(30, min(steps, 300))
    for i in range(steps + 1):
        with _active_lock:
            if booking_id not in _active or _active[booking_id]['stop']: break
        t = i / steps
        lat = start_lat + (end_lat - start_lat) * t
        lng = start_lng + (end_lng - start_lng) * t
        remain = max(0.0, total - (total * t)); eta_sec = int(remain / speed_mps)
        socketio.emit('position', {
            'lat': lat, 'lng': lng, 'progress': round(t*100, 2),
            'speed_mps': speed_mps, 'eta_sec': eta_sec
        }, to=f'booking_{booking_id}', namespace='/tracking')
        time.sleep(1.0)
    with _active_lock: _active.pop(booking_id, None)

def start_simulation_for_booking(socketio, booking_id, slat, slng, elat, elng):
    with _active_lock:
        if booking_id in _active: return False
        _active[booking_id] = {'stop': False}
    threading.Thread(target=_runner, args=(socketio, booking_id, slat, slng, elat, elng), daemon=True).start()
    return True

def stop_simulation_for_booking(booking_id):
    with _active_lock:
        if booking_id in _active:
            _active[booking_id]['stop'] = True; return True
    return False
