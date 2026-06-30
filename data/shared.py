live_prices = {}

from strategy.strategy_engine import (
    StrategyEngine
)

from data.candle_engine import (
    CandleEngine
)

from broker.paper_broker import (
    PaperBroker
)

from risk.risk_manager import (
    RiskManager
)


risk_manager = RiskManager(
)


candle_engine = CandleEngine()


strategy = StrategyEngine(
    candle_engine
)

broker = PaperBroker(
)

from risk.exit_manager import (
    ExitManager
)

exit_manager = ExitManager(
    candle_engine,
    broker
)
