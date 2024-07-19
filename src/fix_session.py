import time
import quickfix as fix


class Application(fix.Application):
    debug = False
    session_id = None
    logged_out = False

    def onCreate(self, session_id):
        return

    def onLogon(self, session_id):
        print("Session %s successfully logged in" % session_id)
        self.session_id = session_id
        self.logged_out = False
        return

    def onLogout(self, session_id):
        print("Session %s logged out" % session_id)
        self.session_id = None
        self.logged_out = True
        return

    def toAdmin(self, message, session_id):
        if self.debug:
            print("To Admin message: %s" % message)
        msg_type = fix.MsgType()
        message.getHeader().getField(msg_type)
        if msg_type.getValue() == fix.MsgType_Logon:
            message.getHeader().setField(fix.Password("password-goes-here"))  # TODO
            message.getHeader().setField(fix.Username("user-goes-here"))      # TODO
        return

    def fromAdmin(self, message, session_id):
        if self.debug:
            print("From Admin message: %s" % message)
        return

    def toApp(self, message, session_id):
        if self.debug:
            print("To App message: ", end='')
            print_message(message)
        return

    def fromApp(self, message, session_id):
        print("\nReceived message: ", end='')
        print_message(message)
        return

# End of Application


class FixSession(object):
    initiator = None
    exec_id = 0

    def __init__(self, config_file):
        self.settings = fix.SessionSettings(config_file)
        self.application = Application()

        store_factory = fix.FileStoreFactory(self.settings)
        log_factory = fix.FileLogFactory(self.settings)
        self.initiator = fix.SocketInitiator(self.application, store_factory, self.settings, log_factory)

    def start(self):
        if not self.initiator.isStopped():
            raise Exception("Session is already started")

        self.application.session_id = None
        self.application.logged_out = False
        self.initiator.start()

        # wait for the client to login
        while not self.application.session_id and not self.application.logged_out:
            time.sleep(0.1)

        if not self.application.session_id:
            raise Exception("Login failed")

    def stop(self):
        self.initiator.stop()

    def gen_exec_id(self):
        new_id = time.time_ns()
        self.exec_id = new_id if self.exec_id < new_id else self.exec_id + 1
        return repr(self.exec_id)

    def submit(self, request):
        print("Sending %s" % request.toString().replace('\x01', '|'))
        fix.Session.sendToTarget(request, self.application.session_id)

# End of FixSession


def print_message(msg):
    msg_type = get_field_value(fix.MsgType(), msg.getHeader())
    if msg_type == fix.MsgType_MarketDataRequestReject:
        reason = get_field_value(fix.Text(), msg)
        print(f"Market data request rejected: {reason}")

    elif msg_type == fix.MsgType_MarketDataSnapshotFullRefresh:
        symbol = get_field_value(fix.Symbol(), msg)
        print(f"Market data snapshot for {symbol}")
        group = fix.Group(268, 269)  # 268 = NoMDEntries, 269 = MDEntryType
        print_md_entries(msg, group)

    elif msg_type == fix.MsgType_MarketDataIncrementalRefresh:
        symbol = get_field_value(fix.Symbol(), msg)
        print(f"Market data incremental update for {symbol}")
        group = fix.Group(268, 279)  # 268 = NoMDEntries, 279 = MDUpdateAction
        print_md_entries(msg, group)

    else:
        print(f"Unexpected message type: {msg_type}")

    fix_str = msg.toString().replace('\x01', '|')
    print(f"FIX message: {fix_str}")


def print_md_entries(msg, group):
    try:
        num_of_entries = get_field_value(fix.NoMDEntries(), msg)
        if num_of_entries is not None:
            for i in range(1, num_of_entries + 1):
                msg.getGroup(i, group)

                md_entry_type = md_entry_type_dict.get(get_field_value(fix.MDEntryType(), group), 'Unknown')
                md_entry_size = get_field_value(fix.MDEntrySize(), group)
                md_entry_price = get_field_value(fix.MDEntryPx(), group)
                print(f"Entry {i}: Type: {md_entry_type}, Size: {md_entry_size}, Price: {md_entry_price}")

    except Exception as e:
        print(f"An error occurred: {e}")


def get_field_value(field, msg):
    if msg.isSetField(field.getField()):
        msg.getField(field)
        return field.getValue()
    else:
        return None


md_entry_type_dict = {
    '0': 'Bid',
    '1': 'Offer',
    '2': 'Trade',
    '3': 'Index Value',
    '4': 'Opening Price',
    '5': 'Closing Price',
    '6': 'Settlement Price',
    '7': 'Trading Session High Price',
    '8': 'Trading Session Low Price',
    '9': 'Trading Session VWAP Price',
    'A': 'Imbalance',
    'B': 'Trade Volume',
    'C': 'Open Interest',
    'D': 'Composite Underlying Price',
    'E': 'Simulated Sell Price',
    'F': 'Simulated Buy Price',
}
