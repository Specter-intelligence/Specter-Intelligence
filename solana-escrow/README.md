# Solana Escrow Engine

An on‑chain escrow program demonstrating how traditional backend escrow logic can be migrated to Solana.

## 🧠 Architecture: Web2 vs Solana

### Web2 Escrow (Traditional Backend)
- **State**: Stored in a centralized database (PostgreSQL, Redis).
- **Logic**: Runs as a monolithic API (Node.js, Python) that updates the DB.
- **Security**: Relies on server authentication, rate‑limiting, and manual fraud review.
- **Trust**: Users must trust the escrow service operator.
- **Cost**: Infrastructure costs scale with usage; payment processing fees (Stripe, PayPal) apply.

### Solana Escrow (On‑Chain)
- **State**: Stored in program‑derived accounts (PDAs) on the Solana ledger.
- **Logic**: Encoded in a Rust program that runs on‑chain; execution is deterministic and verifiable.
- **Security**: Built on Solana’s permissionless network; funds are locked in escrow accounts controlled by the program.
- **Trust**: No trusted third party; code is open‑source and auditable.
- **Cost**: One‑time deployment; users pay minimal transaction fees (~$0.0001 per interaction).

## 🔧 How It Works

The program implements a two‑party conditional escrow:

1. **Create**: Maker locks funds into a PDA escrow account, specifying taker and optional expiry.
2. **Approve**: Maker and taker can independently signal approval.
3. **Release**: Once both parties approve (or expiry passes), anyone can trigger the release, transferring funds to the taker.
4. **Cancel**: If both parties agree before release, funds can be returned to the maker.

All state transitions are enforced by the on‑chain program; no off‑chain coordination required.

## 📦 Program Structure

- `src/lib.rs` – Core program logic (instructions, state, PDA derivation).
- `Cargo.toml` – Rust dependencies (Solana SDK, Borsh).
- This README – Architecture explanation and usage.

## 🚀 Usage Example

```rust
use solana_escrow::{EscrowInstruction, get_escrow_address};
use solana_sdk::{
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
    system_program,
};

// Create an escrow locking 1 SOL.
let maker = Pubkey::new_unique();
let taker = Pubkey::new_unique();
let seed = 12345;
let amount = 1_000_000_000; // 1 SOL in lamports
let expiry = 0; // no expiry

let (escrow_pda, bump) = get_escrow_address(&maker, seed);

let ix = Instruction::new_with_borsh(
    program_id,
    &EscrowInstruction::Create { seed, amount, taker, expiry },
    vec![
        AccountMeta::new(maker, true),
        AccountMeta::new(escrow_pda, false),
        AccountMeta::new_readonly(taker, false),
        AccountMeta::new_readonly(system_program::id(), false),
    ],
);
```

## ⚖️ Tradeoffs & Constraints

| Aspect | Web2 Backend | Solana Program |
|--------|--------------|----------------|
| **Uptime** | Requires 24/7 server monitoring. | Solana network guarantees global availability. |
| **Scalability** | Vertical scaling (bigger servers) or horizontal scaling (load balancers). | Inherits Solana’s throughput (~65k TPS). |
| **Cost Model** | Fixed infrastructure + variable payment‑processor fees. | Only transaction fees (lamports) paid by users. |
| **Development** | Familiar frameworks (Express, Django). | Steeper learning curve (Rust, accounts, PDAs). |
| **Upgradability** | Deploy new version instantly. | Program immutability (requires migration or new deployment). |
| **Privacy** | Data hidden behind authentication. | All state public on‑chain (patterns can use encryption). |
| **Interoperability** | REST/GraphQL APIs; integration with legacy systems. | Native cross‑program calls within Solana ecosystem. |

## 🧪 Testing & Deployment

### Local Testing
```bash
cd solana-escrow
cargo test
```

### Devnet Deployment
1. Build: `cargo build-bpf`
2. Deploy: `solana program deploy target/deploy/solana_escrow.so`
3. Verify: `solana program show <PROGRAM_ID>`

### Client Integration
A minimal frontend or CLI can invoke the program using `@solana/web3.js` or `solana‑cli`.

## 🎯 Why This Matters

Moving escrow logic on‑chain eliminates custodial risk, reduces operational overhead, and enables composability with other DeFi primitives (lending, AMMs, NFTs). It’s a concrete example of how traditional backend patterns can be reimagined as decentralized, trust‑minimized protocols.

## 📄 License

MIT