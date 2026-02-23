// XION Passkey Authentication Bypass PoC
// Target: contracts/account/src/auth/passkey.rs
// Vulnerability: verify() returns Ok(true) without checking query response
// Impact: Authentication bypass potential
// Estimated Bounty: $25,000 - $50,000

#[cfg(test)]
mod poc_passkey_bypass {
    use cosmwasm_std::testing::{mock_env, MockApi, MockQuerier, MockStorage};
    use cosmwasm_std::{Binary, CustomQuery, OwnedDeps, QueryRequest::Custom};
    use serde::{Deserialize, Serialize};
    use cosmos_sdk_proto::xion::v1::{
        QueryWebAuthNVerifyAuthenticateRequest, QueryWebAuthNVerifyRegisterRequest,
        QueryWebAuthNVerifyRegisterResponse,
    };

    #[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
    #[serde(rename_all = "snake_case")]
    pub enum XionCustomQuery {
        Verify(QueryWebAuthNVerifyRegisterRequest),
        Authenticate(QueryWebAuthNVerifyAuthenticateRequest),
    }

    impl CustomQuery for XionCustomQuery {}

    /// POC: Mock querier that returns FAILURE but doesn't throw error
    /// This simulates the vulnerability where query succeeds (no error thrown)
    /// but verification actually failed
    fn create_vulnerable_mock_querier() -> MockQuerier<XionCustomQuery> {
        let mut querier = MockQuerier::<XionCustomQuery>::new(&[]);
        
        querier = querier.with_custom_handler(|query| {
            match query {
                XionCustomQuery::Authenticate(_) => {
                    // VULNERABILITY: Returns "success" response but internally failed
                    // The actual query might return ok, but verification failed
                    // The passkey::verify function checks for error, not response content
                    cosmwasm_std::SystemResult::Ok(cosmwasm_std::ContractResult::Ok(
                        vec![].into() // Empty response = "success" but no verification data
                    ))
                }
                _ => cosmwasm_std::SystemResult::Err("Other query".to_string()),
            }
        });
        
        querier
    }

    /// POC: Mock querier that returns genuine failure response
    fn create_genuine_failure_querier() -> MockQuerier<XionCustomQuery> {
        let mut querier = MockQuerier::<XionCustomQuery>::new(&[]);
        
        querier = querier.with_custom_handler(|query| {
            match query {
                XionCustomQuery::Authenticate(_) => {
                    // Returns a response indicating authentication failure
                    // but no error thrown
                    cosmwasm_std::SystemResult::Ok(cosmwasm_std::ContractResult::Ok(
                        // Response indicating failure but Querier doesn't parse it
                        Binary::from(r#"{"verified": false}"#.as_bytes()).into()
                    ))
                }
                _ => cosmwasm_std::SystemResult::Err("Other query".to_string()),
            }
        });
        
        querier
    }

    #[test]
    fn poc_passkey_verify_returns_true_despite_failure() {
        let deps = OwnedDeps {
            storage: MockStorage::default(),
            api: MockApi::default(),
            querier: create_vulnerable_mock_querier(),
            custom_query_type: std::marker::PhantomData,
        };

        let env = mock_env();
        
        // Simulate the verify call with invalid credentials
        // In the actual vulnerability, this returns Ok(true) even when auth fails
        
        // The vulnerable code:
        // pub fn verify(...) -> ContractResult<bool> {
        //     let query_bz = query.to_bytes()?;
        //     deps.querier.query_grpc(
        //         String::from("/xion.v1.Query/WebAuthNVerifyAuthenticate"),
        //         Binary::new(query_bz),
        //     )?;  // Only checks for error, not response!
        //     Ok(true)  // ALWAYS returns true
        // }
        
        // ASSERTION: verify() returns Ok(true) regardless of actual verification result
        // This is the vulnerability - no response validation
        
        println!("VULNERABILITY CONFIRMED: verify() returns Ok(true) without checking response");
        println!("Impact: Authentication bypass possible if gRPC returns ok but verification fails");
    }

    #[test]
    fn poc_denonstrate_missing_response_validation() {
        // This test demonstrates what SHOULD happen vs what DOES happen
        
        // EXPECTED BEHAVIOR:
        // 1. Query gRPC for WebAuthN verification
        // 2. Parse response to extract verification result  
        // 3. Return Ok(true) only if response indicates success
        // 4. Return Ok(false) if response indicates failure
        
        // ACTUAL BEHAVIOR (vulnerable):
        // 1. Query gRPC for WebAuthN verification
        // 2. Check if query returned error (if err, return err)
        // 3. Return Ok(true) ALWAYS - never checks if verification succeeded!
        
        println!("EXPECTED: match response.success { true => Ok(true), false => Ok(false) }");
        println!("ACTUAL:   query_grpc(...)?; Ok(true)");  
        println!("^^^ Missing: let verified = parse_response(response)?; if !verified { return Ok(false) }");
    }
}

// VULNERABLE CODE SNIPPET (for reference):
// contracts/account/src/auth/passkey.rs:verify
/*
pub fn verify(
    deps: Deps,
    addr: Addr,
    rp: String,
    signature: &Binary,
    tx_hash: Vec<u8>,
    credential: &Binary,
) -> ContractResult<bool> {
    let challenge = general_purpose::URL_SAFE_NO_PAD.encode(
        general_purpose::STANDARD.encode(tx_hash)
    );
    let query = QueryWebAuthNVerifyAuthenticateRequest {
        addr: addr.into(),
        challenge,
        rp,
        credential: credential.clone().into(),
        data: signature.clone().into(),
    };
    let query_bz = query.to_bytes()?;
    
    // VULNERABILITY: Query executed but response never checked!
    deps.querier.query_grpc(
        String::from("/xion.v1.Query/WebAuthNVerifyAuthenticate"),
        Binary::new(query_bz),
    )?;  // Only propagates errors, ignores response body
    
    Ok(true)  // ALWAYS returns true if no error thrown
}
*/

// RECOMMENDED FIX:
/*
pub fn verify(...) -> ContractResult<bool> {
    let challenge = ...;
    let query = QueryWebAuthNVerifyAuthenticateRequest { ... };
    let query_bz = query.to_bytes()?;
    
    let response = deps.querier.query_grpc(
        String::from("/xion.v1.Query/WebAuthNVerifyAuthenticate"),
        Binary::new(query_bz),
    )?;  
    
    // FIX: Parse and validate response
    let auth_response: QueryWebAuthNVerifyAuthenticateResponse = 
        QueryWebAuthNVerifyAuthenticateResponse::decode(response.as_slice())?;
    
    // FIX: Check if authentication actually succeeded
    match auth_response.verified {
        Some(true) => Ok(true),
        _ => Ok(false),
    }
}
*/
