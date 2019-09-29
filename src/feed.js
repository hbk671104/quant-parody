const WebSocket = require('ws')
const pako = require('pako')

const WS_URL = 'wss://api.huobi.pro/ws'

const subscribe = ws => {
    var symbols = ['btcusdt', 'ethusdt', 'eosusdt']
    // 订阅深度
    // 谨慎选择合并的深度，ws每次推送全量的深度数据，若未能及时处理容易引起消息堆积并且引发行情延时
    for (let symbol of symbols) {
        ws.send(
            JSON.stringify({
                sub: `market.${symbol}.depth.step0`,
                id: `${symbol}`
            })
        )
    }
    // 订阅K线
    for (let symbol of symbols) {
        ws.send(
            JSON.stringify({
                sub: `market.${symbol}.kline.1min`,
                id: `${symbol}`
            })
        )
    }
}

const init = () => {
    const ws = new WebSocket(WS_URL)
    ws.on('open', () => {
        console.log('open')
        subscribe(ws)
    })
    ws.on('message', data => {
        let text = pako.inflate(data, {
            to: 'string'
        })
        let msg = JSON.parse(text)
        if (msg.ping) {
            ws.send(
                JSON.stringify({
                    pong: msg.ping
                })
            )
        } else if (msg.tick) {
            console.log('tick: ', msg)
            // handle(msg)
        } else {
            console.log('raw: ', text)
        }
    })
    ws.on('close', () => {
        console.log('close')
        init()
    })
    ws.on('error', err => {
        console.log('error', err)
        init()
    })
}

init()
