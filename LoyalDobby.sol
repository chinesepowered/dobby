// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract SuperCat is ERC20 {
    constructor() ERC20("LoyalDobby", "LD") {
        // Initial supply of 1 million tokens with 18 decimals
        _mint(msg.sender, 1000000 * 10**decimals());
    }
}