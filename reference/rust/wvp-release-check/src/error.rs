use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum VerificationError {
    Io(String),
    CommandFailed {
        context: String,
        detail: String,
    },
    CountParse {
        endpoint: String,
        detail: String,
    },
    MissingAsset {
        suffix: String,
    },
    AmbiguousAsset {
        label: String,
        suffix: String,
        names: String,
    },
    InvalidUtf8Filename(String),
    MissingSignedAsset(String),
    MissingPublicKey(String),
    SignatureVerificationFailed(String),
}

impl fmt::Display for VerificationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(detail) => write!(f, "{detail}"),
            Self::CommandFailed { context, detail } => write!(f, "{context}: {detail}"),
            Self::CountParse { endpoint, detail } => {
                write!(f, "could not parse count for {endpoint}: {detail}")
            }
            Self::MissingAsset { suffix } => write!(f, "no {suffix} asset found"),
            Self::AmbiguousAsset {
                label,
                suffix,
                names,
            } => write!(
                f,
                "multiple {label} assets found for suffix {suffix}: {names}"
            ),
            Self::InvalidUtf8Filename(label) => write!(f, "{label} filename is not valid utf-8"),
            Self::MissingSignedAsset(name) => {
                write!(f, "signed asset not found for signature asset: {name}")
            }
            Self::MissingPublicKey(path) => {
                write!(f, "public verification key not found at {path}")
            }
            Self::SignatureVerificationFailed(detail) => {
                write!(f, "openssl signature verification failed: {detail}")
            }
        }
    }
}
