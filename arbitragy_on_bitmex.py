import bitmex
import time
import datetime
import ccxt

'''
this program is ready to get profit on the BITMEX
By author liuhuihui
'''

client = bitmex.bitmex(test=False, api_key="your api key",
                       api_secret="your api secret")
bitmex = ccxt.bitmex()


# 套利函数
def profit():
    print('启动套利函数 %s' % datetime.datetime.now())
    while 1:
        '''
        读数 如果出现读数异常,则进入下一次循环
        '''
        try:

            # XBTUSD bid1 ask1
            ret_usd = client.OrderBook.OrderBook_getL2(symbol='XBTUSD', depth=1).result()
            # bitmex rate limit
            remain_api = ret_usd[1].headers.get('X-RateLimit-Remaining')
            if (int(remain_api) <= 12):
                time.sleep(12)
            a = ret_usd[0][0].get('price')  # ask1
            a1 = ret_usd[0][1].get('price')  # bid1
            # XBTU18 bid2 ask2
            ret_U18 = client.OrderBook.OrderBook_getL2(symbol='XBTU18', depth=1).result()
            c1 = ret_U18[0][0].get('price')  # ask2
            c = ret_U18[0][1].get('price')  # bid2
            # 获取XBTUSD 资金费率,每八小时改变一次，资金费率>0,代表多仓付给空仓,反之
            ret = client.Instrument.Instrument_get(symbol='XBTUSD', reverse=True, count=1).result()
            d = ret[0][0].get('fundingRate')
        except:
            continue

        '''
        交易策略
        '''
        if d < 0 or (d > 0 and d < 0.002):
            n = c / a  # U18买一/XBT卖一
            if n > 1:
                print(d)
                print(n)

                ######获取仓位信息#################
                try:
                    pos = client.Position.Position_get().result()
                except:
                    pass
                while pos[1].status_code != 200:
                    try:
                        pos = client.Position.Position_get().result()
                    except:
                        pass
                    time.sleep(2)
                ##保证rate limit
                if int(pos[1].headers.get('X-RateLimit-Remaining')) <= 9:
                    time.sleep(9)

                #####平衡两边，避免暴露风险########################
                cmp_pos_qty = pos[0][0].get('currentQty') + pos[0][1].get('currentQty')  # 比较净多空
                if cmp_pos_qty < 0:
                    # 市价平衡
                    try:
                        result0 = client.Order.Order_new(symbol='XBTU18', side='Buy', orderQty=abs(cmp_pos_qty),
                                                         ordType='Market', text='Market Order').result()
                    except:
                        pass
                    while result0[1].status_code != 200:

                        ###单独针对post类请求的503错误
                        if result0[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result0 = client.Order.Order_new(symbol='XBTU18', side='Buy', orderQty=abs(cmp_pos_qty),
                                                                 ordType='Market', text='Market Order').result()
                            except:
                                pass
                            continue
                        try:
                            result0 = client.Order.Order_new(symbol='XBTU18', side='Buy', orderQty=abs(cmp_pos_qty),
                                                             ordType='Market', text='Market Order').result()
                        except:
                            pass
                    print('arbi<0,平衡')

                if cmp_pos_qty > 0:
                    # 市价平衡
                    try:
                        result1 = client.Order.Order_new(symbol='XBTUSD', side='Sell', orderQty=abs(cmp_pos_qty),
                                                         ordType='Market', text='Market Order').result()
                    except:
                        pass
                    while result1[1].status_code != 200:
                        ###单独针对post类请求的503错误
                        if result1[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result1 = client.Order.Order_new(symbol='XBTUSD', side='Sell',
                                                                 orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                 text='Market Order').result()
                            except:
                                pass
                            continue
                        try:
                            result1 = client.Order.Order_new(symbol='XBTUSD', side='Sell', orderQty=abs(cmp_pos_qty),
                                                             ordType='Market', text='Market Order').result()
                        except:
                            pass
                    print('arbi<0,平衡')

                ##################arbitrary<0,下单条件####################################
                if n > 1.011:

                    print('arbi<0,市价下单')
                    # XBTUSD 下多单 指令执行成功 200,其他情况非200
                    global result2
                    try:
                        result2 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=5000, ordType='Market',
                                                        text='Market Order').result()
                    except:
                        pass
                    ##变量未定义##
                    '''
                    while ('result2' in dir()) == False:
                        print('result2--变量未定义,重新赋值....')
                        result2 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=5000, ordType='Market',
                                                        text='Market Order').result()
                        time.sleep(1)
                    '''
                    # 保证变量定义#
                    while result2[1].status_code != 200:

                        ###单独针对post类请求的503错误
                        if result2[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result2 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=5000,
                                                                ordType='Market', text='Market Order').result()
                            except:
                                pass
                            continue  ##直接进入下一次循环
                        try:
                            result2 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=5000,
                                                            ordType='Market', text='Market Order').result()
                        except:
                            pass
                        time.sleep(2)

                    try:
                        result3 = client.Order.Order_new(symbol='XBTU18', side='Sell', orderQty=5000, ordType='Market',
                                                         text='Market Order').result()
                    except:
                        pass
                    while result3[1].status_code != 200:

                        ###单独针对post类请求的503错误
                        if result3[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result3 = client.Order.Order_new(symbol='XBTU18', side='Sell', orderQty=5000,
                                                                 ordType='Market', text='Market Order').result()
                            except:
                                pass
                            continue
                        try:
                            result3 = client.Order.Order_new(symbol='XBTU18', side='Sell', orderQty=5000,
                                                             ordType='Market', text='Market Order').result()
                        except:
                            pass
                        time.sleep(2)

                    # 更新仓位信息
                    try:
                        pos = client.Position.Position_get().result()
                    except:
                        pass
                    while pos[1].status_code != 200:
                        try:
                            pos = client.Position.Position_get().result()
                        except:
                            pass
                        time.sleep(2)

                ################arbitrary<0,平仓条件#####################################
                if n < 1.0011 and pos[0][0].get('currentQty') < 0 and pos[0][1].get('currentQty') > 0 and (
                        pos[0][0].get('currentQty') + pos[0][1].get('currentQty')) == 0:

                    print('arbi<0，限价平仓')
                    # position1=client.Order.Order_closePosition(symbol='XBTUSD',price=a).result()
                    # position1=client.Order.Order_new(symbol='XBTUSD', orderQty=-min(5000,pos[0][1].get('currentQty')), price=a).result()
                    # ccxt过去一分钟内的k线最大值最小值
                    candles = bitmex.fetch_ohlcv('BTC/USD', '1m', since=None, limit=2, params={'reverse': True})
                    if candles[1][2] - candles[1][3] < 20:
                        global position1
                        try:
                            position1 = client.Order.Order_new(symbol='XBTUSD', side='Sell', execInst='Close',
                                                               orderQty=min(30000, pos[0][1].get('currentQty')),
                                                               price=a).result()
                        except:
                            pass
                        # 变量未定义#
                        '''
                        while ('position1' in dir()) == False:
                            print('position1 --未定义，再次赋值')
                            position1 = client.Order.Order_new(symbol='XBTUSD', side='Sell', execInst='Close',
                                                               orderQty=min(30000, pos[0][1].get('currentQty')),
                                                               price=a).result()
                            time.sleep(1)
                        '''
                        ##保证变量定义##
                        while position1[1].status_code != 200:

                            ###单独针对post类请求的503错误
                            if position1[1].status_code == 503:
                                print('Unable to contact the BitMEX API (503), retrying. ')
                                time.sleep(3)
                                try:
                                    position1 = client.Order.Order_new(symbol='XBTUSD', side='Sell', execInst='Close',
                                                                       orderQty=min(30000, pos[0][1].get('currentQty')),
                                                                       price=a).result()
                                except:
                                    pass
                                continue
                            try:
                                position1 = client.Order.Order_new(symbol='XBTUSD', side='Sell', execInst='Close',
                                                                   orderQty=min(30000, pos[0][1].get('currentQty')),
                                                                   price=a).result()
                            except:
                                pass
                            time.sleep(2)

                        # position2=client.Order.Order_closePosition(symbol='XBTU18',price=c).result()
                        try:
                            position2 = client.Order.Order_new(symbol='XBTU18', side='Buy', execInst='Close',
                                                               orderQty=min(30000, abs(pos[0][0].get('currentQty'))),
                                                               price=c).result()
                        except:
                            pass
                        while position2[1].status_code != 200:

                            ###单独针对post类请求的503错误
                            if position2[1].status_code == 503:
                                print('Unable to contact the BitMEX API (503), retrying. ')
                                time.sleep(3)
                                try:
                                    position2 = client.Order.Order_new(symbol='XBTU18', side='Buy', execInst='Close',
                                                                       orderQty=min(30000,
                                                                                    abs(pos[0][0].get('currentQty'))),
                                                                       price=c).result()
                                except:
                                    pass
                                continue
                            try:
                                position2 = client.Order.Order_new(symbol='XBTU18', side='Buy', execInst='Close',
                                                                   orderQty=min(30000,
                                                                                abs(pos[0][0].get('currentQty'))),
                                                                   price=c).result()
                            except:
                                pass
                            time.sleep(2)
                        # 更新仓位信息
                        try:
                            pos = client.Position.Position_get().result()
                        except:
                            pass
                        while pos[1].status_code != 200:
                            try:
                                pos = client.Position.Position_get().result()
                            except:
                                pass
                            time.sleep(2)
                        cmp_pos_qty = pos[0][0].get('currentQty') + pos[0][1].get('currentQty')  # 比较净多空
                        while cmp_pos_qty == 0:
                            try:
                                pos = client.Position.Position_get().result()
                            except:
                                pass
                            while pos[1].status_code != 200:
                                try:
                                    pos = client.Position.Position_get().result()
                                except:
                                    pass
                                time.sleep(2)
                            cmp_pos_qty = pos[0][0].get('currentQty') + pos[0][1].get('currentQty')  # 比较净多空
                            print('waiting..........')
                            time.sleep(2)
                        ######保证必定而且立刻撤单,追单##########################
                        if cmp_pos_qty < 0:
                            # 取消平仓
                            try:
                                result4 = client.Order.Order_cancel(orderID=position1[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result4[1].status_code != 200:
                                try:
                                    result4 = client.Order.Order_cancel(orderID=position1[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)

                            try:
                                result5 = client.Order.Order_cancel(orderID=position2[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result5[1].status_code != 200:
                                try:
                                    result5 = client.Order.Order_cancel(orderID=position2[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)
                            # 市价追单
                            try:
                                result6 = client.Order.Order_new(symbol='XBTU18', side='Buy', orderQty=abs(cmp_pos_qty),
                                                                 ordType='Market', text='Market Order').result()
                            except:
                                pass
                            while result6[1].status_code != 200:

                                ###单独针对post类请求的503错误
                                if result6[1].status_code == 503:
                                    print('Unable to contact the BitMEX API (503), retrying. ')
                                    time.sleep(3)
                                    try:
                                        result6 = client.Order.Order_new(symbol='XBTU18', side='Buy',
                                                                         orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                         text='Market Order').result()
                                    except:
                                        pass
                                    continue
                                try:
                                    result6 = client.Order.Order_new(symbol='XBTU18', side='Buy',
                                                                     orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                     text='Market Order').result()
                                except:
                                    pass
                            print('arbi<0,撤单追单成功')
                        if cmp_pos_qty > 0:
                            # 取消平仓
                            try:
                                result7 = client.Order.Order_cancel(orderID=position1[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result7[1].status_code != 200:
                                try:
                                    result7 = client.Order.Order_cancel(orderID=position1[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)

                            try:
                                result8 = client.Order.Order_cancel(orderID=position2[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result8[1].status_code != 200:
                                try:
                                    result8 = client.Order.Order_cancel(orderID=position2[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)

                            # 市价追单
                            try:
                                result9 = client.Order.Order_new(symbol='XBTUSD', side='Sell',
                                                                 orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                 text='Market Order').result()
                            except:
                                pass
                            while result9[1].status_code != 200:
                                ###单独针对post类请求的503错误
                                if result9[1].status_code == 503:
                                    print('Unable to contact the BitMEX API (503), retrying. ')
                                    time.sleep(3)
                                    try:
                                        result9 = client.Order.Order_new(symbol='XBTUSD', side='Sell',
                                                                         orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                         text='Market Order').result()
                                    except:
                                        pass
                                    continue
                                try:
                                    result9 = client.Order.Order_new(symbol='XBTUSD', side='Sell',
                                                                     orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                     text='Market Order').result()
                                except:
                                    pass

                            print('arbi<0,撤单追单成功')

        if d > 0 or (d < 0 and d > -0.002):

            n = a1 / c1  # XBT买一/ U18卖一
            if n > 1:
                print(d)
                print(n)

                ######获取仓位信息#################
                try:
                    pos = client.Position.Position_get().result()
                except:
                    pass
                while pos[1].status_code != 200:
                    try:
                        pos = client.Position.Position_get().result()
                    except:
                        pass
                    time.sleep(2)
                ##保证rate limit
                if int(pos[1].headers.get('X-RateLimit-Remaining')) <= 9:
                    time.sleep(9)

                #####平衡两边，避免暴露风险########################
                cmp_pos_qty = pos[0][0].get('currentQty') + pos[0][1].get('currentQty')  # 比较净多空
                if cmp_pos_qty > 0:
                    # 市价平衡
                    try:
                        result10 = client.Order.Order_new(symbol='XBTU18', side='Sell', orderQty=abs(cmp_pos_qty),
                                                         ordType='Market', text='Market Order').result()
                    except:
                        pass
                    while result10[1].status_code != 200:
                        ###针对订单类post请求503单独处理
                        if result10[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result10 = client.Order.Order_new(symbol='XBTU18', side='Sell',
                                                                 orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                 text='Market Order').result()
                            except:
                                pass
                            continue
                        try:
                            result10 = client.Order.Order_new(symbol='XBTU18', side='Sell', orderQty=abs(cmp_pos_qty),
                                                             ordType='Market', text='Market Order').result()
                        except:
                            pass
                    print('arbi>0,平衡')
                if cmp_pos_qty < 0:
                    # 市价追单
                    try:
                        result11 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=abs(cmp_pos_qty),
                                                         ordType='Market', text='Market Order').result()
                    except:
                        pass
                    while result11[1].status_code != 200:
                        ###针对订单类post请求503单独处理
                        if result11[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result11 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=abs(cmp_pos_qty),
                                                                 ordType='Market', text='Market Order').result()
                            except:
                                pass
                            continue
                        try:
                            result11 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=abs(cmp_pos_qty),
                                                             ordType='Market', text='Market Order').result()
                        except:
                            pass

                    print('arbi>0,平衡')

                ################arbitrary>0,下单条件##########################
                if n > 1.012:
                    print('arbi>0，市价下单')
                    # XBTUSD 下空单 指令执行成功 200,其他情况非200
                    global result12
                    try:
                        result12 = client.Order.Order_new(symbol='XBTUSD', side='Sell', orderQty=5000, ordType='Market',
                                                         text='Market Order').result()
                    except:
                        pass
                    '''
                    while ('result12' in dir()) == False:
                        print('result12--变量为定义,重新赋值......')
                        try:
                            result12 = client.Order.Order_new(symbol='XBTUSD', side='Sell', orderQty=5000, ordType='Market',
                                                         text='Market Order').result()
                        except:
                            pass
                        time.sleep(1)
                    '''
                    print('result12赋值ok!')
                    while result12[1].status_code != 200:

                        ###针对订单类post请求503单独处理
                        if result12[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result12 = client.Order.Order_new(symbol='XBTUSD', side='Sell', orderQty=5000,
                                                                 ordType='Market', text='Market Order').result()
                            except:
                                pass
                            continue  ###直接进入下一次循环
                        try:
                            result12 = client.Order.Order_new(symbol='XBTUSD', side='Sell', orderQty=5000,
                                                             ordType='Market', text='Market Order').result()
                        except:
                            pass
                        time.sleep(2)

                    try:
                        result13 = client.Order.Order_new(symbol='XBTU18', side='Buy', orderQty=5000, ordType='Market',
                                                         text='Market Order').result()
                    except:
                        pass
                    while result13[1].status_code != 200:
                        ###针对订单类post请求503单独处理
                        if result13[1].status_code == 503:
                            print('Unable to contact the BitMEX API (503), retrying. ')
                            time.sleep(3)
                            try:
                                result13 = client.Order.Order_new(symbol='XBTU18', side='Buy', orderQty=5000,
                                                                 ordType='Market', text='Market Order').result()
                            except:
                                pass
                            continue
                        try:
                            result13 = client.Order.Order_new(symbol='XBTU18', side='Buy', orderQty=5000,
                                                             ordType='Market', text='Market Order').result()
                        except:
                            pass
                        time.sleep(2)

                    # 更新仓位信息
                    try:
                        pos = client.Position.Position_get().result()
                    except:
                        pass
                    while pos[1].status_code != 200:
                        try:
                            pos = client.Position.Position_get().result()
                        except:
                            pass
                        time.sleep(2)
                ###############arbitrary>0,平仓条件###########################
                if n < 1.0011 and pos[0][0].get('currentQty') > 0 and pos[0][1].get('currentQty') < 0 and (
                        pos[0][0].get('currentQty') + pos[0][1].get('currentQty')) == 0:
                    print('arbi>0，限价平仓')
                    # position1=client.Order.Order_closePosition(symbol='XBTUSD',price=a1).result()
                    # ccxt过去一分钟内的k线最大值最小值
                    candles = bitmex.fetch_ohlcv('BTC/USD', '1m', since=None, limit=2, params={'reverse': True})
                    if candles[1][2] - candles[1][3] < 20:
                        global position3
                        try:
                            position3 = client.Order.Order_new(symbol='XBTUSD', side='Buy', execInst='Close',
                                                               orderQty=min(30000, abs(pos[0][1].get('currentQty'))),
                                                               price=a1).result()
                        except:
                            pass
                        '''
                        while ('position3' in dir()) == False:
                            print('position3未定义,重新赋值......')
                            try:
                                position3 = client.Order.Order_new(symbol='XBTUSD', side='Buy', execInst='Close',
                                                               orderQty=min(30000, abs(pos[0][1].get('currentQty'))),
                                                               price=a1).result()
                            except:
                                pass
                            time.sleep(1)
                        '''
                        while position3[1].status_code != 200:
                            ###针对订单类post请求503单独处理
                            if position3[1].status_code == 503:
                                print('Unable to contact the BitMEX API (503), retrying. ')
                                time.sleep(3)
                                try:
                                    position3 = client.Order.Order_new(symbol='XBTUSD', side='Buy', execInst='Close',
                                                                       orderQty=min(30000,
                                                                                    abs(pos[0][1].get('currentQty'))),
                                                                       price=a1).result()
                                except:
                                    pass
                                continue
                            try:
                                position3 = client.Order.Order_new(symbol='XBTUSD', side='Buy', execInst='Close',
                                                                   orderQty=min(30000,
                                                                                abs(pos[0][1].get('currentQty'))),
                                                                   price=a1).result()
                            except:
                                pass
                            time.sleep(2)
                        # position2=client.Order.Order_closePosition(symbol='XBTU18',price=c1).result()
                        try:
                            position4 = client.Order.Order_new(symbol='XBTU18', side='Sell', execInst='Close',
                                                               orderQty=min(30000, pos[0][0].get('currentQty')),
                                                               price=c1).result()
                        except:
                            pass
                        while position4[1].status_code != 200:
                            ###针对订单类post请求503单独处理
                            if position4[1].status_code == 503:
                                print('Unable to contact the BitMEX API (503), retrying. ')
                                time.sleep(3)
                                try:
                                    position4 = client.Order.Order_new(symbol='XBTU18', side='Sell', execInst='Close',
                                                                       orderQty=min(30000, pos[0][0].get('currentQty')),
                                                                       price=c1).result()
                                except:
                                    pass
                                continue
                            try:
                                position4 = client.Order.Order_new(symbol='XBTU18', side='Sell', execInst='Close',
                                                                   orderQty=min(30000, pos[0][0].get('currentQty')),
                                                                   price=c1).result()
                            except:
                                pass
                            time.sleep(2)
                            # 更新仓位信息
                        try:
                            pos = client.Position.Position_get().result()
                        except:
                            pass
                        while pos[1].status_code != 200:
                            try:
                                pos = client.Position.Position_get().result()
                            except:
                                pass
                            time.sleep(2)
                        cmp_pos_qty = pos[0][0].get('currentQty') + pos[0][1].get('currentQty')  # 比较净多空
                        ######保证必定而且立刻撤单,追单##########################
                        while cmp_pos_qty == 0:
                            try:
                                pos = client.Position.Position_get().result()
                            except:
                                pass
                            while pos[1].status_code != 200:
                                try:
                                    pos = client.Position.Position_get().result()
                                except:
                                    pass
                                time.sleep(2)
                            cmp_pos_qty = pos[0][0].get('currentQty') + pos[0][1].get('currentQty')  # 比较净多空
                            print('waiting..........')
                            time.sleep(2)
                        if cmp_pos_qty > 0:
                            # 取消平仓
                            try:
                                result14 = client.Order.Order_cancel(orderID=position3[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result14[1].status_code != 200:
                                try:
                                    result14 = client.Order.Order_cancel(orderID=position3[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)

                            try:
                                result15 = client.Order.Order_cancel(orderID=position4[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result15[1].status_code != 200:
                                try:
                                    result15 = client.Order.Order_cancel(orderID=position4[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)

                            # 市价追单
                            try:
                                result17 = client.Order.Order_new(symbol='XBTU18', side='Sell',
                                                                 orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                 text='Market Order').result()
                            except:
                                pass
                            while result17[1].status_code != 200:
                                ###针对订单类post请求503单独处理
                                if result17[1].status_code == 503:
                                    print('Unable to contact the BitMEX API (503), retrying. ')
                                    time.sleep(3)
                                    try:
                                        result17 = client.Order.Order_new(symbol='XBTU18', side='Sell',
                                                                         orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                         text='Market Order').result()
                                    except:
                                        pass
                                    continue
                                try:
                                    result17 = client.Order.Order_new(symbol='XBTU18', side='Sell',
                                                                     orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                     text='Market Order').result()
                                except:
                                    pass
                            print('arbi>0,撤单追单成功')
                        if cmp_pos_qty < 0:
                            # 取消平仓
                            try:
                                result18 = client.Order.Order_cancel(orderID=position3[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result18[1].status_code != 200:
                                try:
                                    result18 = client.Order.Order_cancel(orderID=position3[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)

                            try:
                                result19 = client.Order.Order_cancel(orderID=position4[0].get('orderID'),
                                                                    text='Submitted via API.').result()
                            except:
                                pass
                            while result19[1].status_code != 200:
                                try:
                                    result19 = client.Order.Order_cancel(orderID=position4[0].get('orderID'),
                                                                        text='Submitted via API.').result()
                                except:
                                    pass
                                time.sleep(2)

                            # 市价追单
                            try:
                                result20 = client.Order.Order_new(symbol='XBTUSD', side='Buy', orderQty=abs(cmp_pos_qty),
                                                                 ordType='Market', text='Market Order').result()
                            except:
                                pass
                            while result20[1].status_code != 200:
                                ###针对订单类post请求503单独处理
                                if result20[1].status_code == 503:
                                    print('Unable to contact the BitMEX API (503), retrying. ')
                                    time.sleep(3)
                                    try:
                                        result20 = client.Order.Order_new(symbol='XBTUSD', side='Buy',
                                                                         orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                         text='Market Order').result()
                                    except:
                                        pass
                                    continue
                                try:
                                    result20 = client.Order.Order_new(symbol='XBTUSD', side='Buy',
                                                                     orderQty=abs(cmp_pos_qty), ordType='Market',
                                                                     text='Market Order').result()
                                except:
                                    pass

                            print('arbi>0,撤单追单成功')

        # 每次循环停留6s(1次循环最多调用13次api请求)，保证rate limit
        time.sleep(6)


# 程序执行入口
if __name__ == "__main__":
    # 调用套利函数
    profit()



