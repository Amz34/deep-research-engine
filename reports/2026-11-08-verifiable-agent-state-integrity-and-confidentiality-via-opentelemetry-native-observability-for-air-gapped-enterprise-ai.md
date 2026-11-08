# Verifiable AI Agent State Integrity and Confidentiality via OpenTelemetry-Native Observability for Sovereign Air-Gapped Enterprise AI

**Author:** Aamir Zameer (@Amz34) · Principal AI Systems Architect, Az. Consultancy  
**Date:** November 08, 2026  
**Status:** Approved for Production Architecture  
**Tags:** AI Infrastructure, Systems Engineering, Autonomous Systems, Cybersecurity, OpenTelemetry, Formal Verification

---

## 1. Executive Abstract

The proliferation of advanced AI agents within air-gapped enterprise environments, particularly in sectors aligned with national digital sovereignty initiatives like Saudi Vision 2030, necessitates an unprecedented level of trust, auditability, and data control. Traditional observability solutions, designed for connected systems, fall short in providing verifiable integrity and confidentiality for AI agent internal states in these highly secure, isolated deployments. This whitepaper synthesizes a novel, production-grade architecture that leverages OpenTelemetry (OTel) as the native observability backbone, integrating formal verification and advanced cryptographic primitives. We detail mechanisms for cryptographically binding AI agent state transitions to OTel traces, logs, and metrics, employing Merkle trees for state integrity, AES-256 GCM for confidentiality, and digital signatures for agent attestation. Resource optimization strategies are presented to manage the computational overhead within constrained air-gapped environments, facilitating secure data exfiltration via one-way data diodes. The proposed sovereign observability platform, equipped with custom OTel processors, rigorously verifies these cryptographic proofs and enforces security boundary invariants, creating an immutable, auditable chain of custody. This framework transforms observability from passive monitoring into an active security and compliance mechanism, ensuring the trustworthiness, accountability, and sovereign control of mission-critical AI systems.

## 2. System Architecture & Component Topology

The proposed architecture establishes a high-assurance observability pipeline for air-gapped AI agents, ensuring verifiable integrity and confidentiality of their internal states. It is segmented into three logical zones: the **Air-Gapped Secure Zone**, the **Air-Gap Boundary**, and the **Sovereign Monitoring & Analysis Zone**. Data flows unidirectionally and is cryptographically protected at each critical juncture.

```mermaid
graph TD
    subgraph Air-Gapped Secure Zone (Isolated Network)
        A[AI Agent 1 (LLM App)] -- OTel SDK --> B(OTel Exporter: In-Process/Sidecar)
        C[AI Agent 2 (RAG Service)] -- OTel SDK --> B
        D[AI Agent N (Tooling)] -- OTel SDK --> B
        B -- OTLP (gRPC/HTTP) --> E(OTel Collector: Secure Zone)
        E -- Processors (Filter, Sample, Batch, Sign Bundle, Encrypt Bundle) --> F(Secure Data Staging / Local File Exporter)
    end

    subgraph Air-Gap Boundary (Controlled Egress)
        F -- Physical Transfer / Data Diode --> G{One-Way Data Diode}
    end

    subgraph Sovereign Monitoring & Analysis Zone (Trusted Network)
        G -- OTLP (gRPC/HTTP) --> H(OTel Collector: Sovereign Ingress)
        H -- Processors (Verify Bundle, Decrypt Agent State, Verify Agent State, Redact, Enrich) --> I(OTel Collector: Aggregator)
        I -- Traces --> J[Telemetry Backend: Traces (e.g., Tempo)]
        I -- Logs --> K[Telemetry Backend: Logs (e.g., Loki/Elasticsearch)]
        I -- Metrics --> L[Telemetry Backend: Metrics (e.g., Prometheus)]
        H -- Verification & Policy Engine --> M[Audit & Alerting System]
        M --> N[Security Operations Center (SOC)]
        K -- RBAC & Data Masking --> O[Authorized Analysts/Auditors]
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#ccf,stroke:#333,stroke-width:2px
    style F fill:#cff,stroke:#333,stroke-width:2px
    style G fill:#ffc,stroke:#333,stroke-width:2px
    style H fill:#ccf,stroke:#333,stroke-width:2px
    style I fill:#ccf,stroke:#333,stroke-width:2px
    style J fill:#cfc,stroke:#333,stroke-width:2px
    style K fill:#cfc,stroke:#333,stroke-width:2px
    style L fill:#cfc,stroke:#333,stroke-width:2px
    style M fill:#ffc,stroke:#333,stroke-width:2px
    style N fill:#f9f,stroke:#333,stroke-width:2px
    style O fill:#f9f,stroke:#333,stroke-width:2px
```

**Architectural Pattern:**
AI agents within the **Air-Gapped Secure Zone** are instrumented with OpenTelemetry SDKs. They capture critical internal state, canonicalize it, apply Merkle tree hashing for integrity, encrypt sensitive portions using AES-256 GCM, and digitally sign the resulting state snapshot. This augmented data is emitted as OTel traces and logs to a local OTel Collector. This **Secure Zone Collector** performs essential data reduction (filtering, sampling, batching) and then cryptographically signs and encrypts entire batches of telemetry before exporting them to a secure staging area.

The **Air-Gap Boundary** is traversed via a **One-Way Data Diode**, ensuring strict unidirectional data flow. The staged, encrypted, and signed telemetry bundles are transferred to the **Sovereign Monitoring & Analysis Zone**.

Upon ingress, a dedicated **Sovereign Ingress OTel Collector** receives the bundles. This collector hosts custom processors that perform multi-layered verification: first, the integrity of the telemetry bundle itself, then the digital signature of the originating AI agent, followed by decryption of sensitive state components, and finally, re-computation and verification of the Merkle root hash. Post-verification, data is redacted based on access policies and enriched with verification metadata before being routed to various **Telemetry Backends** (traces, logs, metrics). A **Verification & Policy Engine** continuously monitors verification outcomes, triggering alerts to the **SOC** for any integrity or confidentiality violations, thus establishing a robust, auditable, and sovereign AI observability framework.

## 3. Deep-Dive Architectural Investigation

### 3.1. Agent-Side Verifiable State Generation

The core of verifiable AI agent state lies in embedding cryptographic proofs directly at the source.

#### 3.1.1. Agent State Definition and Canonicalization

To ensure deterministic hashing and signing, the agent's state must be represented in a canonical, serializable format. This guarantees that identical logical states always yield identical byte representations.

*   **Data Structure:** A structured representation of the agent's critical state elements.
    ```json
    {
      "agent_id": "uuid-agent-123",
      "model_id": "model-resnet50-v2",
      "model_version": "1.2.3",
      "config_hash": "sha256:cfg_abcdef123...",
      "input_data_hash": "sha256:input_xyz789...",
      "output_data_hash": "sha256:output_pqr456...",
      "internal_variables": {
        "inference_count": 1024,
        "last_update_timestamp": 1678886400,
        "current_mode": "production"
      },
      "previous_state_digest": "sha256:prev_digest_000...", // For state chain-of-custody
      "sequence_number": 12345, // Monotonically increasing counter
      "timestamp_utc": "2023-03-15T10:00:00Z",
      "public_context": { /* Non-sensitive, verifiable data */ },
      "sensitive_context": { /* Sensitive data, encrypted */ }
    }
    ```
*   **Canonicalization Function `Canonicalize(State)`:**
    *   Deterministic JSON serialization (e.g., `json.dumps(state_dict, sort_keys=True, separators=(',', ':'))`).
    *   Protobuf serialization (with deterministic encoding rules) is also highly suitable for its efficiency and strict schema enforcement.
    *   All nested objects and arrays must have a defined, stable ordering. Numerical values must be serialized to a fixed precision.

#### 3.1.2. Integrity Hashing (Merkle Tree)

For complex or hierarchical agent states, a Merkle tree is constructed. Each leaf node represents a cryptographic hash of a granular state component (e.g., individual RAG document, a specific LLM prompt parameter). The root hash of this tree (`merkle_root_hash`) provides a compact, tamper-evident summary of the entire state.

**Mathematical Formula:**
*   `H(x)`: A collision-resistant hash function (e.g., SHA-256).
*   Leaf nodes `L_i = H(Canonicalize(state_component_i))`.
*   Internal nodes `N_j = H(N_{j_left} || N_{j_right})`.
*   Root hash `M_root = H(N_{root_left} || N_{root_right})`.
*   **Invariant**: Any modification to any `state_component_i` will deterministically alter `L_i` and propagate up to change `M_root`, ensuring tamper detection.

#### 3.1.3. Confidentiality Encryption (AES-256 GCM)

The `sensitive_context` portion of the `AgentStateSnapshot` is encrypted using AES-256 in Galois/Counter Mode (GCM) to provide authenticated encryption, ensuring both confidentiality and integrity of the encrypted data.

**Protocol:**
1.  **Key Derivation**: An agent-specific symmetric Data Encryption Key (DEK) is generated ephemerally for each encryption operation or retrieved from a local, air-gapped Key Management System (KMS). This DEK is then encrypted by a Key Encryption Key (KEK) whose public key is known to the sovereign platform.
2.  **Nonce Generation**: A unique, cryptographically secure 96-bit (12-byte) Initialization Vector (IV/Nonce) is generated for each encryption.
3.  **Encryption**: `C = AES-256-GCM(DEK, IV, P, AAD)`
    *   `P`: Plaintext (Canonicalized `sensitive_context`).
    *   `AAD`: Authenticated Additional Data (e.g., `agent_id`, `timestamp_utc`, `task_id`, `merkle_root_hash`). This data is not encrypted but its integrity is cryptographically bound to the ciphertext via the GCM authentication tag.
    *   `C`: Ciphertext (encrypted `sensitive_context`).
    *   `Tag`: Authentication tag (16 bytes) generated by GCM.

**Output Structure for `encrypted_sensitive_context`:**
```json
{
  "iv": "base64(nonce)",
  "ciphertext": "base64(C)",
  "tag": "base64(Tag)",
  "encrypted_dek": "base64(encrypted_DEK_by_KEK_public_key)" // Or DEK_ID
}
```

#### 3.1.4. Digital Signatures (ECDSA/EdDSA)

The `merkle_root_hash` and the `AAD` (Authenticated Additional Data) are digitally signed by the agent's private key. This provides non-repudiation and authenticates the agent as the source of the state snapshot.

**Protocol:**
1.  **Payload for Signing**: `payload_to_sign = H(merkle_root_hash || agent_id || timestamp_utc || task_id || previous_state_digest || sequence_number)`. The inclusion of `previous_state_digest` and `sequence_number` establishes a chain of custody for agent states.
2.  **Signing**: `Signature = SIGN(SK_agent, payload_to_sign)`
    *   `SK_agent`: Agent's unique private key (e.g., ECDSA P-256 or EdDSA), securely stored (HSM/TPM).
    *   `PK_agent`: Corresponding public key, pre-registered in the air-gapped Public Key Infrastructure (PKI) and distributed to the sovereign platform.

#### 3.1.5. OpenTelemetry Span/Log Augmentation

The processed state data, including `merkle_root_hash`, encrypted payload, IV, Tag, `encrypted_dek`, and digital signature, are embedded into OpenTelemetry traces and logs as attributes.

**Concrete Code Snippet (Python OTel Instrumentation):**

```python
import hashlib
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import urandom
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource

# --- Mock Cryptographic Primitives (In production, use HSM/TPM, secure KMS) ---
# Agent's private key (securely stored)
agent_private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
AGENT_PUBLIC_KEY_ID = "agent-pk-uuid-001"

# KEK (Key Encryption Key) for DEK encryption/decryption (managed by KMS)
KEK = urandom(32) # 256-bit KEK

def encrypt_dek_with_kek(dek: bytes, kek: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(kek), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    # PKCS7 padding for ECB
    padder = algorithms.AES.block_size - len(dek) % algorithms.AES.block_size
    padded_dek = dek + bytes([padder]) * padder
    return encryptor.update(padded_dek) + encryptor.finalize()

def decrypt_dek_with_kek(encrypted_dek: bytes, kek: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(kek), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_dek = decryptor.update(encrypted_dek) + decryptor.finalize()
    # Unpad
    padder = padded_dek[-1]
    return padded_dek[:-padder]

# --- End Mock Cryptographic Primitives ---

# Configure OpenTelemetry Tracer (simplified for snippet)
resource = Resource.create({"service.name": "ai-agent-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter())) # Exports to console for demo
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

def canonicalize_dict(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True, separators=(',', ':')).encode('utf-8')

def compute_merkle_root(state_components: dict) -> str:
    # Simplified Merkle tree: just hash the canonicalized full state for this example
    # In reality, this would involve hashing individual components and building a tree
    return hashlib.sha256(canonicalize_dict(state_components)).hexdigest()

class AgentState:
    def __init__(self, agent_id: str, initial_memory: dict):
        self.agent_id = agent_id
        self.memory = initial_memory
        self.current_llm_context = ""
        self.previous_state_digest = "sha256:initial_state_digest_000..."
        self.sequence_number = 0

    def capture_and_protect_state(self, task_id: str, public_ctx: dict, sensitive_ctx: dict):
        self.sequence_number += 1
        timestamp_utc = "2023-10-27T10:30:00.123Z" # Mock timestamp

        # 1. Canonicalize and Merkle Root (simplified to full state hash)
        full_state_for_merkle = {
            "public_context": public_ctx,
            "sensitive_context": sensitive_ctx,
            "previous_state_digest": self.previous_state_digest,
            "sequence_number": self.sequence_number,
            "timestamp_utc": timestamp_utc
        }
        merkle_root_hash = f"sha256:{compute_merkle_root(full_state_for_merkle)}"

        # 2. Encrypt Sensitive Context (AES-256 GCM)
        dek = urandom(32) # Ephemeral DEK
        iv = urandom(12)
        aad_data = canonicalize_dict({
            "agent_id": self.agent_id,
            "task_id": task_id,
            "merkle_root_hash": merkle_root_hash,
            "timestamp_utc": timestamp_utc
        })
        cipher = Cipher(algorithms.AES(dek), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encryptor.authenticate_additional_data(aad_data)
        
        plaintext_sensitive = canonicalize_dict(sensitive_ctx)
        ciphertext = encryptor.update(plaintext_sensitive) + encryptor.finalize()
        tag = encryptor.tag

        encrypted_dek = encrypt_dek_with_kek(dek, KEK) # Encrypt DEK with KEK

        encrypted_sensitive_context = {
            "iv": base64.b64encode(iv).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8'),
            "encrypted_dek": base64.b64encode(encrypted_dek).decode('utf-8')
        }

        # 3. Digital Signature
        payload_to_sign = canonicalize_dict({
            "merkle_root_hash": merkle_root_hash,
            "agent_id": self.agent_id,
            "timestamp_utc": timestamp_utc,
            "task_id": task_id,
            "previous_state_digest": self.previous_state_digest,
            "sequence_number": self.sequence_number
        })
        signature = agent_private_key.sign(payload_to_sign, ec.ECDSA(hashes.SHA256()))
        agent_signature = f"ecdsa_p256:{base64.b64encode(signature).decode('utf-8')}"

        # Update previous_state_digest for next step
        self.previous_state_digest = merkle_root_hash

        return {
            "agent_id": self.agent_id,
            "timestamp_utc": timestamp_utc,
            "task_id": task_id,
            "public_context": json.dumps(public_ctx), # Store as JSON string for OTel attribute
            "merkle_root_hash": merkle_root_hash,
            "encrypted_sensitive_context": json.dumps(encrypted_sensitive_context), # Store as JSON string
            "agent_signature": agent_signature,
            "agent_public_key_id": AGENT_PUBLIC_KEY_ID,
            "agent.state.previous_digest": self.previous_state_digest, # This is the *current* state's hash for the *next* state's previous_digest
            "agent.state.sequence_number": self.sequence_number
        }

# --- Agent Execution Simulation ---
agent = AgentState("uuid-agent-123", {"user_id": "user123", "session_id": "abc"})

for i in range(2):
    public_context_data = {
        "model_name": "llama3-8b",
        "tool_invocations": ["search_db"] if i == 0 else ["generate_report"],
        "input_token_count": 1200 + i*100
    }
    sensitive_context_data = {
        "prompt_template": "You are a financial analyst...",
        "user_query": f"Analyze Q3 2023 earnings for ACME Corp. (Iteration {i+1})",
        "retrieved_documents": [{"doc_id": "d123", "content": "financial report data..."}]
    }
    task_id = f"task-xyz-{i}"

    protected_state = agent.capture_and_protect_state(task_id, public_context_data, sensitive_context_data)

    with tracer.start_as_current_span(f"Agent/TaskExecution-{i}") as span:
        for key, value in protected_state.items():
            span.set_attribute(key, value)
        print(f"Emitted Span for Task {i}: Merkle Root={protected_state['merkle_root_hash'][:20]}..., Sig={protected_state['agent_signature'][:20]}...")
```

### 3.2. Air-Gapped Observability Pipeline & Egress

The OTel Collector within the air-gapped secure zone is the central point for processing and preparing observability data for secure exfiltration.

#### 3.2.1. Data Volume Reduction Strategies

Aggressive data reduction is critical to manage the limited egress bandwidth of air-gapped environments.

*   **Sampling (Traces):** `probabilistic_sampler` or `tail_sampling` processors reduce the number of traces. `probabilistic_sampler` is preferred for its low latency, making decisions at the head of the trace.
    *   **Formula (Probabilistic):** `P(sample) = 1 / R`, where `R` is the sampling ratio. A `TraceID` is sampled if `hash(TraceID) % R == 0`.
*   **Filtering & Redaction (Logs, Traces, Metrics):** `filter` and `attributes` processors remove irrelevant data or sensitive attributes *before* cryptographic operations. This is distinct from the post-decryption redaction on the sovereign side.
    *   **Example:** Removing high-cardinality attributes like ephemeral container IDs, or filtering out debug logs.
*   **Aggregation (Metrics):** OTel SDKs perform client-side aggregation (e.g., `Sum`, `Histogram`) to reduce raw data points to summary statistics over time windows.
*   **Compression:** OTLP exporters support `gzip` or `zstd` compression. This is applied *before* cryptographic signing of the batch to maximize efficiency.

#### 3.2.2. Batching and Custom Exporters

The `batch` processor groups multiple OTel signals into a single `Export*ServiceRequest` to reduce I/O overhead and improve compression. For air-gapped egress, a custom exporter is typically required.

*   **Custom Exporter:** This component writes OTLP-formatted (or a custom binary format) data to a local, encrypted file system or a specific device interface for physical transfer. This exporter integrates the cryptographic operations for the entire batch.

#### 3.2.3. Signed and Encrypted Telemetry Bundles

To ensure the integrity and confidentiality of the observability data itself as it traverses the air-gap, entire batches of OTel data are cryptographically signed and encrypted by the Secure Zone Collector.

*   **Data Structure: `SecureTelemetryBundle`**
    ```protobuf
    message SecureTelemetryBundle {
      bytes encrypted_payload = 1; // AES-256 GCM encrypted (SignedBatchHeader + CompressedOTLPBatch)
      bytes iv = 2;             // Initialization Vector for bundle encryption
      bytes tag = 3;            // Authentication Tag for bundle encryption
      string encryption_key_id = 4; // Identifier for the KEK used to encrypt the bundle DEK
      string bundle_signature = 5; // Digital signature of H(encrypted_payload || iv || tag || encryption_key_id)
      string signer_key_id = 6;    // Identifier for the Secure Zone Collector's public key
      uint64 timestamp = 7;      // UTC timestamp of bundle creation
      uint32 sequence_num = 8;   // Monotonically increasing sequence number for bundles
      bytes previous_bundle_hash = 9; // Hash of the previous SecureTelemetryBundle (for chaining)
    }
    ```
*   **Protocol:**
    1.  The `batch` processor forms an OTLP batch.
    2.  The OTLP batch payload is compressed (e.g., GZIP).
    3.  A `SignedBatchHeader` (containing hash of compressed payload, signature by collector's private key, etc.) is prepended to the compressed payload.
    4.  A unique symmetric DEK is generated for the bundle.
    5.  The `SignedBatchHeader + CompressedOTLPBatch` is encrypted using AES-256 GCM with the bundle DEK.
    6.  The bundle DEK is encrypted using a KEK known to the sovereign platform.
    7.  The entire `encrypted_payload` (including IV, Tag, encrypted DEK) is then signed by the Secure Zone Collector's private key, forming the `SecureTelemetryBundle`.
*   **Architectural Invariant:** All observability data leaving the air-gapped enclave MUST be cryptographically signed by a trusted enclave key and encrypted, and this signature/encryption MUST be verifiable by the external observability platform.

#### 3.2.4. One-Way Data Diode

The **One-Way Data Diode** is a critical physical or logical component that enforces unidirectional data flow, preventing any data from flowing back into the air-gapped secure zone. The `SecureTelemetryBundle` is the only data allowed to traverse this boundary.

### 3.3. Sovereign Ingress & Verification Platform

Upon reaching the sovereign network, the `SecureTelemetryBundle` undergoes a multi-stage verification and decryption process within a dedicated OTel Collector.

*   **OTel Collector (Sovereign Ingress):** This collector is configured with custom processors to handle the cryptographic and policy enforcement.
*   **`bundle_verifier` Processor:**
    1.  **Bundle Signature Verification**: Verifies `bundle_signature` using the Secure Zone Collector's public key against the hash of the bundle's encrypted content.
    2.  **Bundle Decryption**: Decrypts the bundle DEK using the sovereign KEK, then decrypts the `encrypted_payload` using AES-256 GCM. This yields the `SignedBatchHeader` and `CompressedOTLPBatch`.
    3.  **Batch Signature Verification**: Verifies the signature within the `SignedBatchHeader` against the hash of the `CompressedOTLPBatch`.
*   **`agent_state_verifier` Processor:** This processor operates on the now-decrypted OTLP signals (spans/logs).
    1.  **Agent Signature Verification**: For each OTel signal containing `agent_signature`, it retrieves the `PK_agent` from a secure, internal PKI. It verifies `agent_signature` against the `payload_to_sign` (reconstructed from `merkle_root_hash`, `agent_id`, `timestamp_utc`, `task_id`, `previous_state_digest`, `sequence_number`).
    2.  **Agent State Decryption**: If the agent signature is valid, it decrypts the agent's DEK (from `encrypted_dek`) using the sovereign KEK. Then, it decrypts `encrypted_sensitive_context` using AES-256 GCM with the agent's DEK, IV, Tag, and AAD.
    3.  **Merkle Tree Reconstruction & Verification (Post-Decryption)**: The full agent state (public and now-decrypted sensitive context) is reconstructed. A Merkle tree is re-computed, and its root hash is compared against the `merkle_root_hash` attribute. This is the definitive proof of agent state integrity.
*   **`state_redaction_processor`:** Applies granular data redaction/masking policies to the decrypted `sensitive_context` based on user roles, data sensitivity levels, or regulatory requirements *before* storage. This ensures that only authorized personnel with appropriate clearances can view sensitive data.
*   **`state_enrichment_processor`:** Adds verification status (e.g., `bundle.verification_status: "SUCCESS"`, `agent.state.verification_status: "SUCCESS"`, `decryption_status: "SUCCESS"`) and audit trail information to the OTel signals.

**OTel Collector Custom Processor Configuration (Sovereign Ingress):**

```yaml
# otel-collector-sovereign-ingress.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317 # Listens for incoming OTLP data from the air-gap boundary
      http:
        endpoint: 0.0.0.0:4318

processors:
  bundle_verifier:
    # Custom module to verify and decrypt the SecureTelemetryBundle
    module: "github.com/azconsultancy/otel-processors/bundleverifier"
    config:
      secure_zone_public_key_store_path: "/etc/otel-collector/secure_zone_public_keys.json"
      kek_management_service: # Access to sovereign KEKs
        type: "internal_kms_proxy"
        endpoint: "https://sovereign-kms.internal:8200"
        token_path: "/etc/otel-collector/kms_token"
      on_bundle_failure: "drop" # Drop entire bundle if verification fails

  agent_state_verifier:
    # Custom module for cryptographic verification and decryption of agent states
    module: "github.com/azconsultancy/otel-processors/agentstateverifier"
    config:
      public_key_store_path: "/etc/otel-collector/agent_public_keys.json" # Agent PKI
      kek_management_service: # Access to sovereign KEKs for agent DEK decryption
        type: "internal_kms_proxy"
        endpoint: "https://sovereign-kms.internal:8200"
        token_path: "/etc/otel-collector/kms_token"
      sensitive_field_path: "encrypted_sensitive_context"
      merkle_root_field_path: "merkle_root_hash"
      signature_field_path: "agent_signature"
      on_agent_state_failure: "alert_and_redact" # Alert SOC, but redact sensitive parts and pass through
      log_level: "info"

  state_redaction_processor:
    # Custom module for post-decryption data redaction/masking
    module: "github.com/azconsultancy/otel-processors/stateredactor"
    config:
      rules_config_path: "/etc/otel-collector/redaction_rules.yaml"
      default_action: "mask_partial" # e.g., mask last 4 chars of sensitive strings

  batch:
    send_batch_size: 1000
    timeout: 10s

exporters:
  otlp/traces:
    endpoint: "sovereign-trace-backend:4317"
    tls: { insecure: false, ca_file: "/etc/otel-collector/certs/ca.pem", cert_file: "/etc/otel-collector/certs/client.pem", key_file: "/etc/otel-collector/certs/client-key.pem" }
  otlp/logs:
    endpoint: "sovereign-log-backend:4317"
    tls: { insecure: false, ca_file: "/etc/otel-collector/certs/ca.pem", cert_file: "/etc/otel-collector/certs/client.pem", key_file: "/etc/otel-collector/certs/client-key.pem" }
  logging:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [bundle_verifier, agent_state_verifier, state_redaction_processor, batch]
      exporters: [otlp/traces]
    logs:
      receivers: [otlp]
      processors: [bundle_verifier, agent_state_verifier, state_redaction_processor, batch]
      exporters: [otlp/logs, logging]
    metrics: # Metrics typically don't carry sensitive state, so minimal verification needed
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/traces]
```

### 3.4. Sovereign Observability Platform

The verified and decrypted OTel data is then routed to the central observability platform within the sovereign network.

*   **Telemetry Backends**: Dedicated backends for traces (e.g., Tempo, Jaeger), logs (e.g., Loki, Elasticsearch), and metrics (e.g., Prometheus, Thanos) store the data.
*   **Verification & Audit Log**: A dedicated service (e.g., a tamper-evident ledger or a blockchain-like system) stores the results of all cryptographic verifications. This provides an immutable audit trail of agent state integrity and confidentiality events.
*   **Visualization & Analysis**: Grafana dashboards, custom UIs, and analytical tools enable monitoring, debugging, and auditing. Access to decrypted sensitive data is strictly controlled via RBAC integrated with the `state_redaction_processor`.

### 3.5. Formal Verification of Critical Components

Formal verification provides mathematical proof of correctness for critical system properties, establishing a higher trust baseline than empirical testing.

*   **Formal Verification Targets:**
    1.  **Canonicalization Function Correctness:**
        *   **Property:** `∀ S1, S2 . (S1 = S2 ⟺ Canonicalize(S1) = Canonicalize(S2))` (Injectivity and Determinism).
        *   **Method:** Theorem Proving (e.g., Coq, Isabelle/HOL) on the specification of the canonicalization algorithm.
    2.  **Integrity Protocol Correctness (Hashing & Signing):**
        *   **Property:** If `VERIFY(K_pub, H(S), SIG)` returns true, then `SIG` was indeed generated by `SIGN(K_priv, H(S))` where `K_priv` is the private key corresponding to `K_pub`.
        *   **Method:** Cryptographic Proofs (based on established security models for ECDSA/EdDSA) and Model Checking (e.g., TLA+, PlusCal) to prove that the overall protocol correctly detects tampering and ensures chain-of-custody.
    3.  **Air-Gapped PKI Lifecycle:**
        *   **Property:** The process for generating, distributing, revoking, and updating agent public keys within the air-gapped environment is secure and maintains the chain of trust.
        *   **Method:** Formal modeling of PKI operations (e.g., using state machines in TLA+) to prove properties like "only authorized entities can issue/revoke keys."
    4.  **ZKP Circuit Correctness (if ZKPs are used):**
        *   **Property:** The ZKP circuit correctly proves the specified statement without leaking any witness information, and it is sound.
        *   **Method:** Formal verification of the cryptographic circuit using specialized ZKP verification tools.

### 3.6. Security Boundary Invariants (SBIs) & Tamper Detection

Security Boundary Invariants are policy rules that define permissible states, transitions, or data origins/destinations for AI agents. Violations trigger immediate alerts.

**Mechanism:**
SBIs are encoded as custom OTel span attributes or events. The AI agent, or a trusted sidecar, evaluates these invariants at critical execution points.

**Data Structures & Protocols:**
*   **OTel Span Attributes:**
    *   `security.invariant.id`: Unique identifier for the invariant being checked (e.g., `LLM_INPUT_ORIGIN_TRUSTED`, `TOOL_OUTPUT_SCHEMA_VALID`).
    *   `security.invariant.status`: `PASS`, `FAIL`, `N/A`.
    *   `security.invariant.policy_version`: Version of the policy definition.
    *   `security.invariant.violation_details`: JSON string detailing the violation.
    *   `security.invariant.evidence_hash`: Cryptographic hash of the data used to evaluate the invariant.
*   **Verification:** The `Verification & Policy Engine` continuously queries the telemetry backend for spans containing `security.invariant.status: FAIL` or for missing expected `security.invariant.id` attributes on critical spans.

**Architectural Invariant (for SBIs):**
`∀ span ∈ S_critical, ∃ attr ∈ span.attributes : attr.key = "security.invariant.id" ∧ attr.value = "LLM_INPUT_ORIGIN_TRUSTED" ∧ attr.status = "PASS"`
(For every critical span, there must exist an attribute indicating a successful check of a defined security invariant).

## 4. Benchmark & Trade-off Matrix

The proposed architecture introduces cryptographic overhead and complexity but delivers unparalleled security and verifiability. The following matrix benchmarks these trade-offs against traditional or less secure approaches.

| Feature/Dimension       | Legacy/Alternative Paradigm (e.g., Basic OTel, Custom Logging)                                 | Proposed Architecture (OTel-Native Verifiable)