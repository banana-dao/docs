# Vault App

## Getting Started

### Vault info

<img src="../../img/app-image0.png" width="1000"/>

Basic information about the vault is displayed here, including the vault's name, the assets it manages, fee and annual percentage rate (APR), and total value locked (TVL)

### My Position

<img src="../../img/app-image1.png" width="1000"/>

When a wallet is connected, the user's position in the vault is displayed here. If any deposits are pending, their amounts will be displayed separately from the active assets. Note that the amount of active assets is an approximation provided for convenience, as vault ownership is share based.

### Deposit/Withdraw

<p float="left">
<img src="../../img/app-image2.png" width="350"/>
<img src="../../img/app-image3.png" width="350"/>
</p>

The deposit and withdraw buttons are used to interact with the vault. The deposit button will open a dialog to input the amount to deposit. Deposits must be higher than the minimum amount and will be queued for processing. Partial withdrawals are not supported; when withdrawing, the entire amount will be queued for processing and sent to the withdrawer's address at the next possible opportunity.

## Strategy

### HarvestCore
The engine behind Banana Vaults liquidity management is an algorithm called HarvestCore. Combining real time data from the Osmosis chain with external data sources, HarvestCore is able to make informed decisions on how to allocate assets in concentrated liquidity pools to maximize yield generation at the lowest cost.

For the vault implementation, extra safeguards have been added to disable withdrawals and deposits under certain adverse conditions, such as lack of valid price oracle updates, which could lead to a potential risk to user funds.

### BananAI
Banana DAO is actively researching and developing a machine learning model to further optimize the HarvestCore algorithm. Codenamed BananAI, the focus of the project is to be able to predict future market conditions with a high degree of accuracy.