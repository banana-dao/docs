# Contract

## Abstract

### Introduction

In its most basic implementation, a vault is a smart contract that allows users to deposit assets in return for a proportional share of the vault's total assets.

The Banana Vaults contract contains basic interfaces to interact with [Osmosis](https://osmosis.zone) concentrated liquidity pools. An operator is designated to manage the vault's liquidity. The contract is relatively generalized, allowing anyone to create a vault with their own strategy. It is designed to be as simple as possible for users to interact with, while still providing a high level of security and flexibility.

### Shares

When a user deposits assets into the vault, they receive a proportional share of the vault's total assets, which can be redeemed by withdrawing. This share is recorded as a `ratio`, a percentage of the total assets that the user owns. The ratio is calculated by the function `ProcessNewEntriesAndExits`. As the vault is required to be instantiated with some assets, the instantiator's initial ratio will be 1. Deposits and withdrawals are processed after the configured `min_update_frequency` has passed, and only when the vault's LP position is fully closed.

If any withdrawals are pending they will be processed before any deposits. For each account that is pending withdraw, their share of the total active vault assets is calculated according to their ratio and sent to them.

If any deposits are pending, the value of each deposit and the value of each existing account share that has not exited is calculated and the new ratio for each account is set based on their proportion of the resulting total dollar value.

### Liquidity Mining

The vault contract exposes interfaces to manage the vault's liquidity in Osmosis concentrated liquidity pools through application of an off-chain [strategy](./vault_app.md#strategy). Operation is fairly straightforward, with the operator able to create, add to, and withdraw liquidity positions, with handling to ensure that the vault's active assets are not overdrawn.

Liquidity rewards, in the form of incentives and swap fees, are automatically compounded into the vault's assets after commission is deducted.

## Messages

### Instantiate

`InstantiateMsg` is used to create a new vault contract.

In addition to metadata for frontend applications, it contains configuration options for deposits including deposit minimums, caps, and update frequency, as well as the commission fee, fee receiver address, and the operator address.

```rust
pub struct InstantiateMsg {
    // Some metadata about the vault
    pub name: String,
    pub description: Option<String>,
    pub image: Option<String>,
    // Must be a CL pool
    pub pool_id: u64,
    // Update users frequency (adding users that want to join and removing users that want to leave), in seconds
    pub min_update_frequency: Option<u64>,
    // Interval after which ForceExits can be called, in seconds
    pub max_update_frequency: Option<u64>,
    // Seconds after which a price quote is rejected and joins/leaves can't be processed
    pub price_expiry: u64,
    //  Uptime must be enforced to accurately calculate commission
    pub min_uptime: Option<u64>,
    // CL Assets with their corresponding pyth price feed
    pub asset0: VaultAsset,
    pub asset1: VaultAsset,
    pub dollar_cap: Option<Uint128>, // with 8 decimals. Example: If vault cap is 50k USD we pass here 50000 * 10^8 = "5000000000000"
    // Vault commission (in %)
    pub commission: Option<Decimal>,
    // If no address specified, contract admin will be receiver of commissions
    pub commission_receiver: Option<Addr>,
    // Flag to take the right pyth contract address - defaults to mainnet
    pub mainnet: Option<bool>,
    // Vault operator address
    pub operator: Addr,
}

pub struct VaultAsset {
    pub denom: String,
    // Pyth asset id
    pub price_identifier: PriceIdentifier,
    // Need to know decimals to convert from pyth price to asset price
    pub decimals: u32,
    // The minimum amount of tokens that can be deposited in a single tx
    pub min_deposit: Uint128,
}
```

### Execute

`ExecuteMsg` is used to execute actions on the contract.

`Join` creates a new pending deposit. It takes no params, but must be sent with valid coins, defined as one or both of the vault's assets. The amount of each asset must be greater than the minimum deposit amount for that asset.

`Leave` starts a withdrawal. It takes an optional address, which if provided will remove an account other than the sender. Removing other accounts is restricted to the vault operator.

If the configured `min_update_frequency` has passed, the vault will execute `ProcessNewEntriesAndExits` to process all pending deposits and withdrawals the next time its LP position is fully closed and all assets have beens returned to the vault balance for processing.

`CreatePosition`, `AddToPosition` and `WithdrawPosition` are used by the vault operator to manage the vault's liquidity. These functions are essentially wrappers for the equivalent Osmosis messages, with the addition of a `swap` parameter which allows the operator to specify a swap in the same message.

`Halt` and `Resume` are used to pause and resume the vault. When the vault is paused, no new deposits or withdrawals will be processed or can be created. The vault will continue to process pending deposits and withdrawals when it is resumed.

`CloseVault` is used to close the vault permanently. All pending deposits will be canceled and all active addresses will be queued for withdrawal at the next update.

`ForceExits` is a contingency in case the vault operator is unable to make further updates, as deposits and withdrawals are only processed when the LP position is fully closed. It may be called by any account to process all pending deposits and withdrawals, if the last time `ProcessNewEntriesAndExits` has been called was longer ago than the configured `max_update_frequency`.

```rust
pub enum ExecuteMsg {
    // If for some reason the pyth oracle contract address or the price identifiers change, we can update it (also for testing)
    ModifyConfig {
        config: Box<Config>,
    },
    // Manage addresses whitelisted to exceed deposit limits
    Whitelist {
        add: Vec<Addr>,
        remove: Vec<Addr>,
    },
    // Create position
    CreatePosition {
        lower_tick: i64,
        upper_tick: i64,
        tokens_provided: Vec<Coin>,
        token_min_amount0: String,
        token_min_amount1: String,
        swap: Option<Swap>,
    },
    // Add to position
    AddToPosition {
        position_id: u64,
        amount0: String,
        amount1: String,
        token_min_amount0: String,
        token_min_amount1: String,
        swap: Option<Swap>,
    },
    // Withdraw position
    WithdrawPosition {
        position_id: u64,
        liquidity_amount: String,
    },
    // Process entries and exits (done internally by the contract every update frequency)
    ProcessNewEntriesAndExits {},
    // Join vault
    Join {},
    // Leave vault. If no address is specified, the sender will be removed. only the operator can remove other addresses
    Leave {
        address: Option<Addr>,
    },
    // Halt and Resume for Admin
    Halt {},
    Resume {},
    // Close vault. If this is triggered the vault will be closed, nobody else can join and all funds will be withdrawn and sent to the users during next update
    CloseVault {},
    // Dead man switch
    ForceExits {},
}

pub struct Swap {
    pub routes: Vec<SwapAmountInSplitRoute>,
    pub token_in_denom: String,
    pub token_out_min_amount: String,
}
```

### Query

`QueryMsg` is used to query the contract state.

`TotalActiveAssets` returns the total amount of each asset the vault currently holds, minus any pending deposits. `TotalPendingAssets` returns the total amount of pending deposits.

`CanUpdate` returns a boolean indicating whether the contract can process new entries and exits, determined by the last time `ProcessNewEntriesAndExits` was called and the configured `min_update_frequency`.

`PendingJoin` takes a parameter `address` and returns the amount of each asset the account has pending to join the vault. `AccountsPendingExit` returns a list of all accounts that have pending withdrawals.

`VaultRatio` takes a parameter `address` and returns the ratio of the vault's assets that the account owns.

`WhitelistedDepositors` returns a paginated list of whitelisted addresses.

```rust
pub enum QueryMsg {
    #[returns(Config)]
    Config {},
    // Tells you how much of each vault asset is currently being used (not pending join)
    #[returns(TotalAssetsResponse)]
    TotalActiveAssets {},
    // Tells you how much is pending join in total
    #[returns(TotalAssetsResponse)]
    TotalPendingAssets {},
    // Checks if the contract can process new entries and exits
    #[returns(bool)]
    CanUpdate {},
    // Tells you how much of each vault asset is pending to join for an address
    #[returns(Vec<Coin>)]
    PendingJoin { address: Addr },
    #[returns(Vec<Addr>)]
    AccountsPendingExit {},
    // How much of the vault this address owns
    #[returns(Decimal)]
    VaultRatio { address: Addr },
    #[returns(WhitelistedDepositorsResponse)]
    WhitelistedDepositors {
        start_after: Option<Addr>,
        limit: Option<u32>,
    },
}

pub struct TotalAssetsResponse {
    pub asset0: Coin,
    pub asset1: Coin,
}

pub struct WhitelistedDepositorsResponse {
    pub whitelisted_depositors: Vec<Addr>,
}
```

