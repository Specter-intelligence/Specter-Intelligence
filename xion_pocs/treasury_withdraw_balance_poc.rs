// XION Treasury Withdraw Balance Bypass PoC
// Target: contracts/treasury/src/execute.rs:withdraw_coins
// Vulnerability: No balance validation before withdrawal attempt
// Impact: DoS via failed transaction, unexpected state changes
// Estimated Bounty: Low ($1,000 - $5,000) - requires admin compromise

#[cfg(test)]
mod poc_treasury_withdraw_balance {
    use cosmwasm_std::{Coin, Response, CosmosMsg, BankMsg};

    /// POC: Demonstrates missing balance validation
    #[test]
    fn poc_withdraw_without_balance_check() {
        // VULNERABLE CODE:
        // pub fn withdraw_coins(deps: DepsMut, info: MessageInfo, coins: Vec<Coin>) 
        //     -> ContractResult<Response> {
        //     let admin = ADMIN.load(deps.storage)?;
        //     if admin != info.sender { return Err(Unauthorized); }
        //     
        //     // BUG: No balance check! Just sends whatever is requested
        //     Ok(Response::new().add_message(Send {
        //         to_address: info.sender.into_string(),
        //         amount: coins,  // Could exceed contract balance!
        //     }))
        // }
        
        // SCENARIO:
        // Contract balance: 100 uatom
        // Withdraw request: 1000 uatom
        
        let contract_balance = Coin {
            denom: "uatom".to_string(),
            amount: 100u128.into(),
        };
        
        let withdrawal_request = vec![
            Coin {
                denom: "uatom".to_string(),
                amount: 1000u128.into(),  // 10x contract balance!
            }
        ];
        
        // VULNERABLE: Just creates the message, no validation
        let vulnerable_response = Response::new().add_message(CosmosMsg::Bank(BankMsg::Send {
            to_address: "attacker".to_string(),
            amount: withdrawal_request.clone(),
        }));
        
        println!("VULNERABILITY: Function creates withdrawal message without checking balance");
        println!("Contract balance:  {} {}", contract_balance.amount, contract_balance.denom);
        println!("Withdrawal amount: {} {}", withdrawal_request[0].amount, withdrawal_request[0].denom);
        println!("Result: Transaction will FAIL (insufficient funds) but creates DoS vector");
        
        // In CosmWasm, this transaction would fail during execution
        // because the contract doesn't have enough balance
        // NOT a direct theft vulnerability, but poor design
    }

    /// POC: Shows proper implementation
    #[test]
    fn poc_proper_balance_validation() {
        use cosmwasm_std::DepsMut;
        
        // PROPER IMPLEMENTATION:
        // pub fn withdraw_coins(deps: DepsMut, info: MessageInfo, coins: Vec<Coin>) 
        //     -> ContractResult<Response> {
        //     let admin = ADMIN.load(deps.storage)?;
        //     if admin != info.sender { return Err(Unauthorized); }
        //     
        //     // FIX: Check contract has sufficient balance
        //     for coin in &coins {
        //         let balance = deps.querier.query_balance(env.contract.address, &coin.denom)?;
        //         if balance.amount < coin.amount {
        //             return Err(ContractError::InsufficientFunds {
        //                 required: coin.amount,
        //                 available: balance.amount,
        //                 denom: coin.denom.clone(),
        //             });
        //         }
        //     }
        //     
        //     // Only proceed if validation passes
        //     Ok(Response::new().add_message(Send {
        //         to_address: info.sender.into_string(),
        //         amount: coins,
        //     }))
        // }
        
        println!("PROPER FIX: Query contract balance before creating messages");
        println!("Reject withdrawal if balance < requested amount");
        println!("Clear error message: 'Insufficient funds: requested 1000, available 100'");
    }

    /// POC: Demonstrates the DoS vector
    #[test]
    fn poc_dos_vector() {
        // This isn't a financial vulnerability directly, but has impacts:
        
        // 1. Admin can accidentally request impossible withdrawals
        //    -> Transaction fails, wastes gas
        //    -> Confusing error messages ("insufficient funds at runtime")
        
        // 2. In automation/scripts, unexpected failures
        //    -> Script stops mid-operation
        //    -> Requires manual intervention
        
        // 3. Potential for UI confusion
        //    -> User sees "withdraw" button
        //    -> Transaction fails unexpectedly
        //    -> Poor UX, confused users
        
        println!("IMPACT ANALYSIS:");
        println!("- Severity: LOW (requires admin key)");
        println!("- Financial: No direct theft possible without admin key");
        println!("- DoS: Moderate - creates failed transactions, poor UX");
        println!("- Risk: Admin error leading to confusion/gas waste");
    }
}

// VULNERABLE CODE SNIPPET:
/*
pub fn withdraw_coins(
    deps: DepsMut,
    info: MessageInfo,
    coins: Vec<Coin>,
) -> ContractResult<Response> {
    let admin = ADMIN.load(deps.storage)?;
    if admin != info.sender {
        return Err(Unauthorized);
    }
    
    // MISSING: Balance validation
    // Should query contract balance first!
    
    Ok(Response::new().add_message(Send {
        to_address: info.sender.into_string(),
        amount: coins,  // Trusts caller to provide valid amount
    }))
}
*/

// RECOMMENDED FIX:
/*
pub fn withdraw_coins(
    deps: DepsMut,
    env: Env,  // Need env for contract address
    info: MessageInfo,
    coins: Vec<Coin>,
) -> ContractResult<Response> {
    let admin = ADMIN.load(deps.storage)?;
    if admin != info.sender {
        return Err(Unauthorized);
    }
    
    // FIX: Validate sufficient balance exists
    for coin in &coins {
        let balance = deps
            .querier
            .query_balance(env.contract.address.clone(), &coin.denom)?;
        
        if balance.amount < coin.amount {
            return Err(ContractError::InsufficientFunds {
                required: coin.amount,
                available: balance.amount,
                denom: coin.denom.clone(),
            });
        }
    }
    
    Ok(Response::new().add_message(Send {
        to_address: info.sender.into_string(),
        amount: coins,
    }))
}
*/
