from predictit import PiEngine

pie = PiEngine(authenticate=True)
pie.cancel_orders('*')

