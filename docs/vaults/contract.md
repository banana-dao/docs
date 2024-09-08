# Contract

## Abstract

### Introduction

In its most basic implementation, a vault is a smart contract that allows users to deposit assets in return for a proportional share of the vault's total assets.

The Banana Vaults contract contains basic interfaces to interact with [Osmosis](https://osmosis.zone) concentrated liquidity pools. An operator is designated to manage the vault's liquidity. The contract is relatively generalized, allowing anyone to create a vault with their own strategy. It is designed to be as simple as possible for users to interact with, while still providing a high level of security and flexibility.

The Banana Vaults source code is available on [Github](https://github.com/banana-dao/banana-vaults/tree/v0.5.1).

### Tokens

When a user deposits assets into the vault, they receive tokens representing a proportional share of the vault's total assets, which can be redeemed by burning. The amount of tokens received is calculated by the function `process_mints`. As the vault is required to be instantiated with some assets, the instantiator will receive a predetermined `initial_mint`.

When a user deposits assets, they don't immediately receive tokens. Instead, their deposit is queued for processing. The process_mints function is called to mint tokens for pending deposits. This function calculates the number of tokens to be minted based on the current value of the vault's assets and the value of the deposited assets.

Users can initiate a withdrawal by requesting to burn their tokens. Similar to deposits, withdrawals are queued for processing. The process_burns function is called to process pending withdrawals. It calculates the amount of assets to be returned based on the number of tokens being burned and the current value of the vault's assets.

Benefits of tokenization include:

- Simplified Accounting: Users can easily track their share of the vault by monitoring their token balance.
- Transferability: Users can transfer their vault tokens to other addresses, effectively transferring their share of the vault without withdrawing assets.
- Composability: Vault tokens can potentially be used in other DeFi protocols, increasing the utility of the user's deposit.

### Liquidity Mining

The vault contract exposes interfaces to manage the vault's liquidity in Osmosis concentrated liquidity pools through application of an off-chain [strategy](./vault_app.md#strategy). Operation is fairly straightforward, with the operator able to create, add to, and withdraw liquidity positions, with handling to ensure that the vault's active assets are not overdrawn.

Liquidity rewards, in the form of incentives and swap fees, are automatically compounded into the vault's assets after commission is deducted.

## Messages

### Instantiate

`InstantiateMsg` is used to create a new vault contract.

In addition to metadata for frontend applications, it contains configuration options for deposits including deposit minimums, caps, and update frequency, as well as the commission fee, fee receiver address, and the operator address.

```rust
pub struct InstantiateMsg {
    pub metadata: Option<Metadata>,
    // CL Assets with their corresponding pyth price feed
    pub asset0: VaultAsset,
    pub asset1: VaultAsset,
    // Minimum amount of tokens that can be deposited in a single tx
    pub min_asset0: Uint128,
    pub min_asset1: Uint128,
    // Seconds after which a price quote is rejected and entries can't be processed
    pub price_expiry: u64,
    // Must be a CL pool
    pub pool_id: u64,
    // Minimum amount of tokens that can be redeemed in a single tx
    pub min_redemption: Option<Uint128>,
    // USD cap: 1 * 10^(18+8) = 1 USD
    pub dollar_cap: Option<Uint128>,
    // Vault commission, as a percentage
    pub commission: Option<Decimal>,
    // If not specified, receiver will be set to the owner
    pub commission_receiver: Option<Addr>,
    // Used to get the desired pyth contract address - defaults to mainnet
    pub env: Option<Environment>,
    // Vault operator address
    pub operator: Addr,
}

pub struct VaultAsset {
    pub denom: String,
    // Pyth asset id
    pub price_identifier: PriceIdentifier,
    // Need to know decimals to convert from pyth price to asset price
    pub decimals: u32,
}
```

### Execute

`ExecuteMsg` is used to execute actions on the contract. It includes the following top level messages:

- `ManageVault`: Admin functions for managing the vault
- `ManagePosition`: Functions for managing liquidity positions
- `Deposit`: Functions for joining or leaving the vault
- `Cancel`: Functions for canceling pending join/leave requests
- `Unlock`: A dead man switch to unlock the vault after 14 days of operator inactivity

#### ManageVault (VaultMsg)

- `Modify`: Allows modifying various vault settings (operator, config, pool ID, commission, whitelist)
- `CompoundRewards`: Compounds rewards for a specific position or all positions
- `CollectCommission`: Collects the accumulated commission
- `ProcessMints`: Processes pending deposits
- `ProcessBurns`: Processes pending withdrawals
- `Halt`: Pauses deposits and exits
- `Resume`: Resumes deposits and exits

#### ManagePosition (PositionMsg)

- `CreatePosition`: Creates a new liquidity position
- `AddToPosition`: Adds liquidity to an existing position
- `WithdrawPosition`: Withdraws liquidity from a position

#### Deposit (DepositMsg)

- `Mint`: Deposits assets into the vault
- `Burn`: Withdraws assets from the vault

#### Cancel (CancelMsg)

- `Mint`: Cancels a pending deposit
- `Burn`: Cancels a pending withdrawal

#### Unlock

Called to unlock the vault and allow manual redemptions after 14 days of operator inactivity.


```rust
pub enum ExecuteMsg {
    ManageVault(VaultMsg),
    ManagePosition(PositionMsg),
    Deposit(DepositMsg),
    Cancel(CancelMsg),
    Unlock,
}

pub enum VaultMsg {
    Modify(ModifyMsg),
    CompoundRewards {
        position_id: Option<u64>,
        override_uptime: Option<bool>,
        swap: Vec<Swap>,
    },
    CollectCommission,
    ProcessMints,
    ProcessBurns,
    Halt,
    Resume,
}

pub enum ModifyMsg {
    Operator(Addr),
    Config(Box<Config>),
    PoolId(u64),
    Commission(Decimal),
    Whitelist {
        add: Option<Vec<Addr>>,
        remove: Option<Vec<Addr>>,
    },
}

pub enum PositionMsg {
    CreatePosition {
        lower_tick: i64,
        upper_tick: i64,
        tokens_provided: Vec<Coin>,
        token_min_amount0: String,
        token_min_amount1: String,
        swap: Option<Swap>,
    },
    AddToPosition {
        position_id: u64,
        amount0: String,
        amount1: String,
        token_min_amount0: String,
        token_min_amount1: String,
        swap: Option<Swap>,
        override_uptime: Option<bool>,
    },
    WithdrawPosition {
        position_id: u64,
        liquidity_amount: String,
        override_uptime: Option<bool>,
    },
}

pub enum DepositMsg {
    Mint {
        min_out: Option<Uint128>,
    },
    Burn {
        address: Option<Addr>,
        amount: Option<Uint128>,
    },
}

pub enum CancelMsg {
    Mint { address: Option<Addr> },
    Burn { address: Addr },
}

pub struct Swap {
    pub routes: Vec<SwapAmountInSplitRoute>,
    pub token_in_denom: String,
    pub token_out_min_amount: String,
}
```

### Query

`QueryMsg` is used to query the contract state. It includes the following top level queries:

- `EstimateDeposit`: Estimates the result of a deposit or withdrawal
- `LockedAssets`: Returns the total amount of locked assets in the vault
- `AccountStatus`: Queries the status of accounts for minting or burning
- `Rewards`: Queries commission or uncompounded rewards
- `Whitelist`: Returns a paginated list of whitelisted addresses
- `VaultState`: Queries the vault's information or status

#### EstimateDeposit

Estimates the result of a deposit (Mint) or withdrawal (Burn) operation.

#### LockedAssets

Returns the total amount of assets currently locked in the vault.

#### AccountStatus

Queries the status of accounts for minting (depositing) or burning (withdrawing). It returns a list of `AccountResponse` objects containing the address, amount, and minimum output for each account.

#### Rewards

Queries either the accumulated commission or uncompounded rewards.

#### Whitelist

Returns a paginated list of whitelisted addresses.

#### VaultState

Queries the vault's information (Info) or current status (Status). The Info state includes details about the vault's assets, pool ID, owner, operator, commission rate, and configuration. The Status state includes information about join time, last update, various flags (uptime locked, cap reached, halted, terminated), and supply details.

```rust
pub enum QueryMsg {
    #[returns(Vec<Coin>)]
    EstimateDeposit(DepositQuery),
    #[returns(Vec<Coin>)]
    LockedAssets,
    #[returns(Vec<AccountResponse>)]
    AccountStatus(AccountQuery),
    #[returns(Vec<Coin>)]
    Rewards(RewardQuery),
    #[returns(WhitelistResponse)]
    Whitelist {
        start_after: Option<Addr>,
        limit: Option<u32>,
    },
    #[returns(State)]
    VaultState(StateQuery),
}

pub enum DepositQuery {
    Mint(Vec<Coin>),
    Burn(Uint128),
}

pub enum AccountQuery {
    Mint(AccountQueryParams),
    Burn(AccountQueryParams),
}

pub struct AccountQueryParams {
    pub address: Option<Addr>,
    pub start_after: Option<Addr>,
    pub limit: Option<u32>,
}

pub struct AccountResponse {
    pub address: Addr,
    pub amount: Vec<Coin>,
    pub min_out: Option<Uint128>,
}

pub enum RewardQuery {
    Commission,
    Uncompounded,
}

pub struct WhitelistResponse {
    pub whitelisted_depositors: Vec<Addr>,
}

pub enum State {
    Info { /* ... */ },
    Status { /* ... */ },
}

pub enum StateQuery {
    Info,
    Status,
}
```
