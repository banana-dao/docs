# Concepts

## Concentrated Liquidity

Concentrated liquidty allows providers to supply liquidity within a set price range, rather than across the entire price spectrum. This allows for an efficient use of capital and provides a better experience for traders by reducing price impact.

On Osmosis, concentrated liquidity is provided by creating a position with an amount of assets between a lower and upper tick. The ticks represent discrete price points, and a `tick spacing` parameter controls the granularity of the price range. A position is considered in-range if the current pool price, called the active tick, is between the lower and upper ticks. Positions that are in-range earn a share of swap fees and liquidity incentives proportional to their share of liquidity in the active tick.

This mechanism necessitates active management of the position to ensure that it is not just in-range but acheiving best possible capital efficiency.

For more information on Osmosis concentrated liquidity, see the [Osmosis documentation](https://github.com/osmosis-labs/osmosis/tree/main/x/concentrated-liquidity/README.md).

## Impermanent Loss 

Impermanent loss is a commonly used DeFi term that can be understood as when the price of deposited assets changes compared to when they were deposited. The loss is 'impermanent' because the value of deposited tokens can go back up, reducing the loss, if the prices return to their original state. The loss becomes permanent if the liquidity provider decides to withdraw their funds from the pool when the prices have diverged significantly. At that point, they might find that they would have been better off simply holding onto their assets rather than providing liquidity, because the value of their share of the pool is less - in terms of the deposited assets - than if they had not deposited them at all.

When dealing with actively managed liquidity, impermanent loss is a cost of doing business. This "loss" is realized each time the position is rebalanced, so it is important to control the frequency of rebalancing to minimize loss while maximizing yield.