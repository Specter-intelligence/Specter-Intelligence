//! Solana Escrow Engine
//!
//! An on‑chain escrow program implementing a secure, two‑party conditional transfer.
//! This demonstrates how traditional backend escrow logic can be migrated to Solana.

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    program_pack::{IsInitialized, Pack, Sealed},
    pubkey::Pubkey,
    system_instruction,
    sysvar::{clock::Clock, Sysvar},
};
use arrayref::{array_mut_ref, array_ref, array_refs, mut_array_refs};

solana_program::declare_id!("Escrow11111111111111111111111111111111111111");

/// Escrow state stored on‑chain.
#[derive(Debug)]
pub struct Escrow {
    /// The party that deposits the funds (maker).
    pub maker: Pubkey,
    /// The intended recipient (taker).
    pub taker: Pubkey,
    /// Amount of lamports locked in the escrow.
    pub amount: u64,
    /// Unix timestamp when the escrow expires (0 = no expiry).
    pub expiry: i64,
    /// Whether the maker has approved the transfer.
    pub maker_approved: bool,
    /// Whether the taker has approved the transfer.
    pub taker_approved: bool,
    /// Whether the funds have been released.
    pub released: bool,
}

impl Sealed for Escrow {}

impl Pack for Escrow {
    const LEN: usize = 32 + 32 + 8 + 8 + 1 + 1 + 1; // 83 bytes

    fn pack_into_slice(&self, dst: &mut [u8]) {
        let dst = array_mut_ref![dst, 0, 83];
        let (
            maker,
            taker,
            amount,
            expiry,
            maker_approved,
            taker_approved,
            released,
        ) = mut_array_refs![dst, 32, 32, 8, 8, 1, 1, 1];

        maker.copy_from_slice(self.maker.as_ref());
        taker.copy_from_slice(self.taker.as_ref());
        *amount = self.amount.to_le_bytes();
        *expiry = self.expiry.to_le_bytes();
        maker_approved[0] = self.maker_approved as u8;
        taker_approved[0] = self.taker_approved as u8;
        released[0] = self.released as u8;
    }

    fn unpack_from_slice(src: &[u8]) -> Result<Self, ProgramError> {
        let src = array_ref![src, 0, 83];
        let (
            maker,
            taker,
            amount,
            expiry,
            maker_approved,
            taker_approved,
            released,
        ) = array_refs![src, 32, 32, 8, 8, 1, 1, 1];

        Ok(Escrow {
            maker: Pubkey::new_from_array(*maker),
            taker: Pubkey::new_from_array(*taker),
            amount: u64::from_le_bytes(*amount),
            expiry: i64::from_le_bytes(*expiry),
            maker_approved: maker_approved[0] != 0,
            taker_approved: taker_approved[0] != 0,
            released: released[0] != 0,
        })
    }
}

impl IsInitialized for Escrow {
    fn is_initialized(&self) -> bool {
        // Consider an escrow initialized if maker is non‑zero (any valid pubkey).
        self.maker != Pubkey::default()
    }
}

/// Program instructions.
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum EscrowInstruction {
    /// Create a new escrow.
    /// Accounts: [maker, escrow, system_program]
    /// Data: (taker, amount, expiry)
    Create {
        taker: [u8; 32],
        amount: u64,
        expiry: i64,
    },
    /// Approve the escrow (maker or taker).
    /// Accounts: [approver, escrow]
    Approve,
    /// Release funds to the recipient (maker or taker).
    /// Accounts: [releaser, escrow, recipient, system_program]
    Release,
    /// Cancel the escrow and refund maker (only before expiry if not approved).
    /// Accounts: [maker, escrow, system_program]
    Cancel,
}

/// Deserializes an instruction.
pub fn unpack_instruction(data: &[u8]) -> Result<EscrowInstruction, ProgramError> {
    EscrowInstruction::try_from_slice(data).map_err(|_| ProgramError::InvalidInstructionData)
}

/// Processes a Create instruction.
fn process_create(
    accounts: &[AccountInfo],
    taker: [u8; 32],
    amount: u64,
    expiry: i64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let maker = next_account_info(account_info_iter)?;
    let escrow = next_account_info(account_info_iter)?;
    let system_program = next_account_info(account_info_iter)?;

    if !maker.is_signer {
        msg!("Maker must be a signer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    // Ensure escrow is a PDA derived from maker + taker + amount + expiry?
    // For simplicity, we assume the caller provides a fresh account.

    let rent = solana_program::sysvar::rent::Rent::get()?;
    let required_lamports = rent.minimum_balance(Escrow::LEN);

    if escrow.lamports() < required_lamports {
        msg!("Insufficient lamports for escrow account rent");
        return Err(ProgramError::InsufficientFunds);
    }

    // Transfer amount from maker to escrow.
    let ix = system_instruction::transfer(maker.key, escrow.key, amount);
    solana_program::program::invoke(&ix, &[maker.clone(), escrow.clone(), system_program.clone()])?;

    // Initialize escrow state.
    let escrow_data = Escrow {
        maker: *maker.key,
        taker: Pubkey::new_from_array(taker),
        amount,
        expiry,
        maker_approved: false,
        taker_approved: false,
        released: false,
    };
    escrow_data.pack_into_slice(&mut escrow.try_borrow_mut_data()?);

    msg!("Escrow created: {} lamports locked", amount);
    Ok(())
}

/// Processes an Approve instruction.
fn process_approve(accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let approver = next_account_info(account_info_iter)?;
    let escrow = next_account_info(account_info_iter)?;

    if !approver.is_signer {
        msg!("Approver must be a signer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    let mut escrow_data = Escrow::unpack_from_slice(&escrow.data.borrow())?;
    if approver.key == &escrow_data.maker {
        escrow_data.maker_approved = true;
    } else if approver.key == &escrow_data.taker {
        escrow_data.taker_approved = true;
    } else {
        msg!("Approver not part of this escrow");
        return Err(ProgramError::InvalidArgument);
    }

    escrow_data.pack_into_slice(&mut escrow.try_borrow_mut_data()?);
    Ok(())
}

/// Processes a Release instruction.
fn process_release(accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let releaser = next_account_info(account_info_iter)?;
    let escrow = next_account_info(account_info_iter)?;
    let recipient = next_account_info(account_info_iter)?;
    let system_program = next_account_info(account_info_iter)?;

    if !releaser.is_signer {
        msg!("Releaser must be a signer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    let mut escrow_data = Escrow::unpack_from_slice(&escrow.data.borrow())?;
    if escrow_data.released {
        msg!("Escrow already released");
        return Err(ProgramError::InvalidArgument);
    }

    // Only maker or taker can release, and both must have approved.
    if releaser.key != &escrow_data.maker && releaser.key != &escrow_data.taker {
        msg!("Releaser not part of this escrow");
        return Err(ProgramError::InvalidArgument);
    }
    if !escrow_data.maker_approved || !escrow_data.taker_approved {
        msg!("Both parties must approve before release");
        return Err(ProgramError::InvalidArgument);
    }

    // Transfer locked amount from escrow to recipient.
    let ix = system_instruction::transfer(escrow.key, recipient.key, escrow_data.amount);
    solana_program::program::invoke(&ix, &[escrow.clone(), recipient.clone(), system_program.clone()])?;

    // Mark as released.
    escrow_data.released = true;
    escrow_data.pack_into_slice(&mut escrow.try_borrow_mut_data()?);

    msg!("Escrow released to {}", recipient.key);
    Ok(())
}

/// Processes a Cancel instruction.
fn process_cancel(accounts: &[AccountInfo]) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let maker = next_account_info(account_info_iter)?;
    let escrow = next_account_info(account_info_iter)?;
    let system_program = next_account_info(account_info_iter)?;

    if !maker.is_signer {
        msg!("Maker must be a signer");
        return Err(ProgramError::MissingRequiredSignature);
    }

    let escrow_data = Escrow::unpack_from_slice(&escrow.data.borrow())?;
    if maker.key != &escrow_data.maker {
        msg!("Only maker can cancel");
        return Err(ProgramError::InvalidArgument);
    }
    if escrow_data.maker_approved || escrow_data.taker_approved {
        msg!("Cannot cancel after approval");
        return Err(ProgramError::InvalidArgument);
    }
    if escrow_data.expiry > 0 {
        let clock = Clock::get()?;
        if clock.unix_timestamp >= escrow_data.expiry {
            msg!("Escrow already expired; use Release instead");
            return Err(ProgramError::InvalidArgument);
        }
    }

    // Refund locked amount to maker.
    let ix = system_instruction::transfer(escrow.key, maker.key, escrow_data.amount);
    solana_program::program::invoke(&ix, &[escrow.clone(), maker.clone(), system_program.clone()])?;

    msg!("Escrow canceled, {} lamports refunded", escrow_data.amount);
    Ok(())
}

/// Main entrypoint.
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    msg!("Escrow program entrypoint");

    // Verify program ID matches.
    if program_id != &ID {
        return Err(ProgramError::IncorrectProgramId);
    }

    let instruction = unpack_instruction(instruction_data)?;
    match instruction {
        EscrowInstruction::Create { taker, amount, expiry } => {
            process_create(accounts, taker, amount, expiry)
        }
        EscrowInstruction::Approve => process_approve(accounts),
        EscrowInstruction::Release => process_release(accounts),
        EscrowInstruction::Cancel => process_cancel(accounts),
    }
}

entrypoint!(process_instruction);