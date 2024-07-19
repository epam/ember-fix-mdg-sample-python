###############################################################################
# This is minimalistic sample that illustrates how to subscribe for market data
###############################################################################
import sys
import quickfix as fix
import quickfix50sp2 as fixnn

from fix_session import FixSession

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please specify config file parameter")
        exit(1)

    # start session
    config_file = sys.argv[1]
    session = FixSession(config_file)
    session.start()

    # initialize market data request
    request = fix.Message()
    request.getHeader().setField(fix.MsgType(fix.MsgType_MarketDataRequest))

    request.setField(fix.MDReqID(session.gen_exec_id()))
    request.setField(fix.SubscriptionRequestType(fix.SubscriptionRequestType_SNAPSHOT_PLUS_UPDATES))
    request.setField(fix.MarketDepth(0))  # full book
    request.setField(fix.MDUpdateType(fix.MDUpdateType_INCREMENTAL_REFRESH))

    group = fixnn.MarketDataRequest().NoMDEntryTypes()
    group.setField(fix.MDEntryType(fix.MDEntryType_BID))
    request.addGroup(group)
    group.setField(fix.MDEntryType(fix.MDEntryType_OFFER))
    request.addGroup(group)
    group.setField(fix.MDEntryType(fix.MDEntryType_TRADE))
    request.addGroup(group)

    group = fixnn.MarketDataRequest().NoRelatedSym()
    group.setField(fix.SecurityType(fix.SecurityType_OPTION))
    request.addGroup(group)

    # send request
    session.submit(request)

    # wait for user to type something then stop session
    command = input()
    session.stop()
