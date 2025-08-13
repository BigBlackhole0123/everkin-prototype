import math
_running = {}

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    import math as m
    phi1, phi2 = m.radians(lat1), m.radians(lat2)
    dphi = m.radians(lat2-lat1)
    dl = m.radians(lon2-lon1)
    a = m.sin(dphi/2)**2 + m.cos(phi1)*m.cos(phi2)*m.sin(dl/2)**2
    return 2*R*m.atan2(m.sqrt(a), m.sqrt(1-a))

def start_simulation_for_booking(socketio, booking_id:int, lat1, lon1, lat2, lon2) -> bool:
    room = f"booking_{booking_id}"
    if booking_id in _running:
        return False
    _running[booking_id] = True
    total = _haversine(lat1, lon1, lat2, lon2)
    steps = max(30, int(total/120))
    steps = min(steps, 240)
    def worker():
        try:
            for i in range(steps+1):
                if not _running.get(booking_id): break
                t = i/steps
                lat = lat1 + (lat2-lat1)*t
                lon = lon1 + (lon2-lon1)*t
                socketio.emit('position', {'lat':lat, 'lng':lon, 'progress': int(t*100)}, to=room, namespace='/tracking')
                socketio.sleep(1.0)
        finally:
            _running.pop(booking_id, None)
    socketio.start_background_task(worker)
    return True

def stop_simulation_for_booking(booking_id:int) -> bool:
    if booking_id in _running:
        _running[booking_id] = False
        return True
    return False
