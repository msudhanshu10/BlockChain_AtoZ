//sdcoin ICO

// Version of the compiler
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

contract sdcoin_ico {

    // intoducing the maximum number of sdcoins available for sale
    uint public max_sdcoins = 1000000;

    // Introducing to USD to sdcoin conversion rate
    uint public usd_to_sdcoin = 1000;

    // Introducing the total number of sdcoins that have been bought by the investors
    uint public total_sdcoins_bought = 0;

    // Mapping from the investor's address to its equity in sdcoin and USD
    mapping(address => uint) equity_sdcoin;
    mapping(address => uint) equity_usd;

    // Checking if an investor can buy sdcoins
    modifier can_buy_sdcoins(uint usd_invested) {
        require (usd_invested * usd_to_sdcoin + total_sdcoins_bought <= max_sdcoins);
        _;
    }


    // Getting the equity in sdcoins of an investor
    function equity_in_sdcoin(address investor) external view returns (uint) {
        return equity_sdcoin[investor];
    }
    // Getting the equity in USD of an investor
    function equity_in_usd(address investor) external view returns (uint) {
        return equity_usd[investor];
    }

    // Buying sdcoins
    function buy_sdcoins(address investor, uint usd_invested) external
    can_buy_sdcoins(usd_invested) {
        uint sdcoins_bought = usd_invested * usd_to_sdcoin;
        equity_sdcoin[investor] += sdcoins_bought;

        equity_usd[investor] = equity_sdcoin[investor] / usd_to_sdcoin;
        total_sdcoins_bought += sdcoins_bought;
    }

    // Selling sdcoins
    function sell_sdcoins(address investor, uint sd_coins_sold) external
    {
        equity_sdcoin[investor] -= sd_coins_sold;
        equity_usd[investor] = equity_sdcoin[investor] / usd_to_sdcoin;
        total_sdcoins_bought -= sd_coins_sold;
    }
}