from predictit import PiEngine

pie = PiEngine(authenticate=False)
pie.cancel_orders('*')

