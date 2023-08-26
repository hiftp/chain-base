### AVAX Odoo module to interact with accounts and smart contracts

A minimal odoo module to interact with the Avalanche blockchain.

### Goal

Hi Odooers, this is another minimal project that I wanted to share with you. My driver for this research was the smart contracts development and integration with Odoo. Of course, there are many alternatives to achieve this, but my scope was to find a blockchain compatible with the Ethereum virtual machine to run Solidity code faster and cheaper.

That's how I found AVAX.

嗨 Odooers，这是我想与您分享的另一个最小项目。我进行这项研究的驱动力是智能合约的开发和与 Odoo 的集成。

当然，有很多替代方案可以实现这一点，但我的目标是找到与以太坊虚拟机兼容的区块链，以更快、更便宜地运行 Solidity 代码。这就是我找到 AVAX 的方式。

### Avax

Avalanche ([AVAX](https://www.avax.network/)) is an Ethereum compatible 3rd generation blockchain.

Avax network site says: **Build without limits.** I think they are right.

I am amazed at how fast this network is. The transactions are executed in seconds, and the fees are notably lower than Ethereum.

Also, the documentation and support available are excellent.

I joined Avalanche Discord support to drop a few questions, and I received multiple responses in minutes.

Anyway, I could solve most of my work using what is available on the web.

### Odoo

So basically, I developed this basic Odoo module to interact with smart contracts in Avax.

The architecture of this module is oriented to test the Avax integration only. You may find a lot of improvement opportunities.

This Odoo module uses [Web3.py](https://web3py.readthedocs.io/en/stable/#). Web3.py is a python library for interacting with Ethereum, and it works perfectly with Avax too.

It has the Avax connector implementation, accounts, and smart contract functionality with certain limitations.

I included the FUJI Testnet connector set up in the demo data.

I packed this inside a docker-compose.

所以基本上，我开发了这个基本的 Odoo 模块来与 Avax 中的智能合约进行交互。该模块的体系结构仅用于测试 Avax 集成。

你可能会发现很多改进的机会。这个 Odoo 模块使用 [Web3.py](https:web3py.readthedocs.ioenstable)。

Web3.py 是一个用于与以太坊交互的 python 库，它也可以与 Avax 完美配合。它具有 Avax 连接器实现、帐户和智能合约功能，但有一定的限制。

我在演示数据中包含了设置的 FUJI Testnet 连接器。我把它打包在一个 docker-compose 中。

#### basic steps:

- Clone this repository
- Initialize the docker container
- Create a new odoo database
- Search and install the Avax module
- Create an Avax account from odoo
- Don't forget to fund your account with the faucet
- Create a smart contract, paste de solidity content in the solidity field
- Compile and deploy the smart contract
- Test the smart contract functionally. You need funds to write, to pay the gas of the transactions, but not for reading.

#### Notes:

This blog is research; please don't use this code in production.

I didn't want to use Metamask; 

I preferred to encrypt the key with a password entered by the user, so every time the user wants to sign a transaction, they will need to enter this password from Odoo instead of Metamask. 

If we store the password in Odoo, we can use the bot without human intervention.

这个博客是研究；

请不要在生产中使用此代码。

我不想使用 Metamask；

我更喜欢用用户输入的密码来加密密钥，所以每次用户想要签署交易时，他们都需要从 Odoo 输入这个密码，而不是 Metamask。

如果我们将密码存储在 Odoo 中，我们可以在没有人工干预的情况下使用机器人。



I hope you like it :-)

