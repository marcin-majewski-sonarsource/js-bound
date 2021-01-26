# pragma pylint: disable=attribute-defined-outside-init

"""
This module load custom hyperopt
"""
import logging
from pathlib import Path
from typing import Dict

from freqtrade.constants import HYPEROPT_LOSS_BUILTIN, USERPATH_HYPEROPTS
from freqtrade.exceptions import OperationalException
from freqtrade.optimize.hyperopt_interface import IHyperOpt
from freqtrade.optimize.hyperopt_loss_interface import IHyperOptLoss
from freqtrade.resolvers import IResolver


logger = logging.getLogger(__name__)


class HyperOptResolver(IResolver):
    """
    This class contains all the logic to load custom hyperopt class
    """
    object_type = IHyperOpt
    object_type_str = "Hyperopt"
    user_subdir = USERPATH_HYPEROPTS
    initial_search_path = None

    @staticmethod
    def load_hyperopt(config: Dict) -> IHyperOpt:
        """
        Load the custom hyperopt class from config parameter
        :param config: configuration dictionary
        """
        if not config.get('hyperopt'):
            raise OperationalException("No Hyperopt set. Please use `--hyperopt` to specify "
                                       "the Hyperopt class to use.")

        hyperopt_name = config['hyperopt']

        hyperopt = HyperOptResolver.load_object(hyperopt_name, config,
                                                kwargs={'config': config},
                                                extra_dir=config.get('hyperopt_path'))

        if not hasattr(hyperopt, 'populate_indicators'):
            logger.info("Hyperopt class does not provide populate_indicators() method. "
                        "Using populate_indicators from the strategy.")
        if not hasattr(hyperopt, 'populate_buy_trend'):
            logger.info("Hyperopt class does not provide populate_buy_trend() method. "
                        "Using populate_buy_trend from the strategy.")
        if not hasattr(hyperopt, 'populate_sell_trend'):
            logger.info("Hyperopt class does not provide populate_sell_trend() method. "
                        "Using populate_sell_trend from the strategy.")
        return hyperopt


class HyperOptLossResolver(IResolver):
    """
    This class contains all the logic to load custom hyperopt loss class
    """
    object_type = IHyperOptLoss
    object_type_str = "HyperoptLoss"
    user_subdir = USERPATH_HYPEROPTS
    initial_search_path = Path(__file__).parent.parent.joinpath('optimize').resolve()

    @staticmethod
    def load_hyperoptloss(config: Dict) -> IHyperOptLoss:
        """
        Load the custom class from config parameter
        :param config: configuration dictionary
        """

        hyperoptloss_name = config.get('hyperopt_loss')
        if not hyperoptloss_name:
            raise OperationalException(
                "No Hyperopt loss set. Please use `--hyperopt-loss` to "
                "specify the Hyperopt-Loss class to use.\n"
                f"Built-in Hyperopt-loss-functions are: {', '.join(HYPEROPT_LOSS_BUILTIN)}"
            )
        hyperoptloss = HyperOptLossResolver.load_object(hyperoptloss_name,
                                                        config, kwargs={},
                                                        extra_dir=config.get('hyperopt_path'))

        # Assign timeframe to be used in hyperopt
        hyperoptloss.__class__.ticker_interval = str(config['timeframe'])
        hyperoptloss.__class__.timeframe = str(config['timeframe'])

        return hyperoptloss
